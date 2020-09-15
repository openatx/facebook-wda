# Created: codeskyblue 2020/05
# Inspired by: https://github.com/iOSForensics/pymobiledevice

import logging
import os
import plistlib
import socket
import struct
import sys
from functools import lru_cache
from typing import Optional, Union

from .exceptions import MuxConnectError, MuxError


PROGRAM_NAME = "facebook-wda"
logger = logging.getLogger(PROGRAM_NAME)


class SafeStreamSocket():
    def __init__(self, addr: Union[str, tuple, socket.socket]):
        """
        Args:
            addr: can be /var/run/usbmuxd or (localhost, 27015)
        """
        self._sock = None
        if isinstance(addr, socket.socket):
            self._sock = addr
            return
        if isinstance(addr, str):
            if not os.path.exists(addr):
                raise MuxError("socket unix:{} unable to connect".format(addr))
            family = socket.AF_UNIX
        else:
            family = socket.AF_INET

        self._sock = socket.socket(family, socket.SOCK_STREAM)
        self._sock.connect(addr)

    def recvall(self, size: int) -> bytearray:
        buf = bytearray()
        while len(buf) < size:
            chunk = self._sock.recv(size - len(buf))
            if not chunk:
                raise MuxError("socket connection broken")
            buf.extend(chunk)
        return buf

    def sendall(self, data: Union[bytes, bytearray]) -> int:
        return self._sock.sendall(data)

    def close(self):
        logger.debug("Socket closed")
        self._sock.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class PlistSocket(SafeStreamSocket):
    def __init__(self, addr: str, tag: int = 0):
        super().__init__(addr)
        self._tag = tag
        self._first = True

    def send_packet(self, payload: dict, reqtype: int = 8):
        """
        Args:
            payload: required

            # The following args only used in the first request
            reqtype: request type, always 8 
            tag: int
        """
        body_data = plistlib.dumps(payload)
        if self._first:  # first package
            length = 16 + len(body_data)
            header = struct.pack(
                "IIII", length, 1, reqtype,
                self._tag)  # version: 1, request: 8(?), tag: 1(?)
        else:
            header = struct.pack(">I", len(body_data))
        self.sendall(header + body_data)

    def recv_packet(self, header_size=None) -> dict:
        if self._first or header_size == 16:  # first receive
            header = self.recvall(16)
            (length, version, resp, tag) = struct.unpack("IIII", header)
            length -= 16  # minus header length
            self._first = False
        else:
            header = self.recvall(4)
            (length, ) = struct.unpack(">I", header)

        body_data = self.recvall(length)
        payload = plistlib.loads(body_data)
        return payload

    def send_recv_packet(self, payload: dict) -> dict:
        self.send_packet(payload)
        return self.recv_packet()


class Usbmux:
    def __init__(self, address: Optional[Union[str, tuple]] = None):
        if address is None:
            if os.name == "posix":  # linux or darwin
                address = "/var/run/usbmuxd"
            elif os.name == "nt":  # windows
                address = ('127.0.0.1', 27015)
            else:
                raise EnvironmentError("Unsupported system:", sys.platform)

        self.__address = address
        self.__tag = 0

    def _next_tag(self) -> int:
        self.__tag += 1
        return self.__tag

    def create_connection(self) -> PlistSocket:
        return PlistSocket(self.__address, self._next_tag())

    def send_recv(self, payload: dict) -> dict:
        with self.create_connection() as s:
            s.send_packet(payload)
            recv_data = s.recv_packet()
            self._check(recv_data)
            return recv_data

    def device_list(self):
        """
        Return example:
        {'DeviceList': [{'DeviceID': 37,
                'MessageType': 'Attached',
                'Properties': {'ConnectionSpeed': 480000000,
                            'ConnectionType': 'USB',
                            'DeviceID': 37,
                            'LocationID': 123456,
                            'ProductID': 4776,
                            'SerialNumber': 'xxx',
                            'UDID': 'xxx',
                            'USBSerialNumber': 'xxx'}}]}
        """
        payload = {
            "MessageType": "ListDevices",  # 必选
            "ClientVersionString": "libusbmuxd 1.1.0",
            "ProgName": PROGRAM_NAME,
            "kLibUSBMuxVersion": 3,
            # "ProcessID": 0, # Xcode send it processID
        }
        data = self.send_recv(payload)
        _devices = [item['Properties'] for item in data['DeviceList']]
        return [d for d in _devices if d['ConnectionType'] == 'USB']

    def get_single_device_udid(self) -> str:
        """ to run this function, there must be only one device connected
        
        Raises:
            MuxError
        """
        devices = self.device_list()
        if len(devices) == 0:
            raise MuxError("No device connected")
        if len(devices) > 1:
            raise MuxError("More then two device connected")
        udid = devices[0]['SerialNumber']
        return udid

    @lru_cache(1024)
    def device(self, udid: str) -> "Device":
        """ return device object """
        return Device(udid, self)

    def _check(self, data: dict):
        if 'Number' in data and data['Number'] != 0:
            raise MuxError(data)

    def read_system_BUID(self):
        """ BUID is always same """
        data = self.send_recv({
            'ClientVersionString': 'libusbmuxd 1.1.0',
            'MessageType': 'ReadBUID',
            'ProgName': PROGRAM_NAME,
            # 'kLibUSBMuxVersion': 3
        })
        return data['BUID']


class Device(object):
    def __init__(self, udid: str, _usbmux=None):
        assert udid, "udid should not empty"
        self._usbmux = _usbmux or Usbmux()
        self._udid = udid
        self._info = self.info

    # DeviceID will be changed if device re-plug
    # So can not use cached_property here
    @property
    def info(self) -> dict:
        """
        Example return:
        {
            "SerialNumber": "xxxx", # udid
            "DeviceID": 12,
        }
        """
        for dinfo in self._usbmux.device_list():
            if dinfo['SerialNumber'] == self._udid:
                return dinfo

        raise MuxError("Device {} not connected".format(self._udid))

    def create_inner_connection(self, port: int = 0xf27e) -> PlistSocket:
        # I really donot know why do this
        # The following code convert port(0x1234) to port(0x3412)
        _port = ((port & 0xff) << 8) | (port >> 8)
        logger.debug("port convert %s(%d) -> %s(%d)", hex(port), port,
                     hex(_port), _port)
        _original_port = port
        del (port)

        device_id = self.info['DeviceID']
        conn = self._usbmux.create_connection()
        payload = {
            'DeviceID': device_id,  # Required
            'MessageType': 'Connect',  # Required
            'PortNumber': _port,  # Required
            'ProgName': PROGRAM_NAME,
        }
        logger.debug("Send payload: %s", payload)
        data = conn.send_recv_packet(payload)
        logger.debug("connect port: %d", _port)
        if 'Number' in data and data['Number'] != 0:
            err_code = data['Number']
            if err_code == 3:
                raise MuxConnectError(
                    "device port:{} is not ready".format(_original_port))
            else:
                raise MuxError(data)
        logger.debug("connection established")
        return conn

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Created on Thu Dec 09 2021 09:56:30 by codeskyblue
"""

import json
from http.client import HTTPConnection, HTTPSConnection, HTTPResponse
from urllib.parse import urlparse

from wda.usbmux.exceptions import HTTPError, MuxConnectError, MuxError
from wda.usbmux.pyusbmux import select_device

_DEFAULT_CHUNK_SIZE = 4096

def http_create(url: str) -> HTTPConnection:
    u = urlparse(url)
    if u.scheme == "http+usbmux":
        udid, device_wda_port = u.netloc.split(":")
        device = select_device(udid)
        return device.make_http_connection(int(device_wda_port))
    elif u.scheme == "http":
        return HTTPConnection(u.netloc)
    elif u.scheme == "https":
        return HTTPSConnection(u.netloc)
    else:
        raise ValueError(f"unknown scheme: {u.scheme}")


class HTTPResponseWrapper:
    def __init__(self, content: bytes, status_code: int):
        self.content = content
        self.status_code = status_code
    
    def json(self):
        return json.loads(self.content)

    @property
    def text(self) -> str:
        return self.content.decode("utf-8")

    def getcode(self) -> int:
        return self.status_code
    

def fetch(url: str, method="GET", data=None, timeout=None, chunk_size: int = _DEFAULT_CHUNK_SIZE) -> HTTPResponseWrapper:
    """
    thread safe http request

    Raises:
        HTTPError
    """
    try:
        method = method.upper()
        conn = http_create(url)
        conn.timeout = timeout
        u = urlparse(url)
        urlpath = url[len(u.scheme) + len(u.netloc) + 3:]

        if not data:
            conn.request(method, urlpath)
        else:
            conn.request(method, urlpath, json.dumps(data), headers={"Content-Type": "application/json"})
        response = conn.getresponse()
        content = _read_response(response, chunk_size)
        resp = HTTPResponseWrapper(content, response.status)
        return resp
    except Exception as e:
        raise HTTPError(e)


def _read_response(response:HTTPResponse, chunk_size: int = _DEFAULT_CHUNK_SIZE) -> bytearray:
    content = bytearray()
    while True:
        chunk = response.read(chunk_size)
        if len(chunk) == 0:
            break
        content.extend(chunk)
    return content

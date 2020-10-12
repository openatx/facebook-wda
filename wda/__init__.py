#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import base64
import copy
import contextlib
import enum
import functools
import io
import json
import logging
import os
import re
import threading
import time
from collections import defaultdict, namedtuple
from typing import Callable, Optional, Union
from urllib.parse import urlparse

import attrdict
import requests
import retry
import six
from deprecated import deprecated
from six.moves import urllib

from . import requests_usbmux, xcui_element_types
from ._proto import *
from .exceptions import *
from .utils import inject_call, limit_call_depth

try:
    from functools import cached_property  # Python3.8+
except ImportError:
    from cached_property import cached_property

try:
    import sys
    import logzero
    if not (hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()):
        log_format = '[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d] %(message)s'
        logzero.setup_default_logger(formatter=logzero.LogFormatter(
            fmt=log_format))
    logger = logzero.logger
except ImportError:
    logger = logging.getLogger("facebook-wda")  # default level: WARNING

DEBUG = False
HTTP_TIMEOUT = 180.0  # unit second
DEVICE_WAIT_TIMEOUT = 180.0  # wait ready

LANDSCAPE = 'LANDSCAPE'
PORTRAIT = 'PORTRAIT'
LANDSCAPE_RIGHT = 'UIA_DEVICE_ORIENTATION_LANDSCAPERIGHT'
PORTRAIT_UPSIDEDOWN = 'UIA_DEVICE_ORIENTATION_PORTRAIT_UPSIDEDOWN'


class Status(enum.IntEnum):
    # 不是怎么准确，status在mds平台上变来变去的
    UNKNOWN = 100  # other status
    ERROR = 110


class Callback(str, enum.Enum):
    ERROR = "::error"
    HTTP_REQUEST_BEFORE = "::http-request-before"
    HTTP_REQUEST_AFTER = "::http-request-after"

    RET_RETRY = "::retry"  # Callback return value
    RET_ABORT = "::abort"
    RET_CONTINUE = "::continue"


def convert(dictionary):
    """
    Convert dict to namedtuple
    """
    return attrdict.AttrDict(dictionary)

    # Old implement
    #return namedtuple('GenericDict', list(dictionary.keys()))(**dictionary)


def urljoin(*urls):
    """
    The default urlparse.urljoin behavior look strange
    Standard urlparse.urljoin('http://a.com/foo', '/bar')
    Expect: http://a.com/foo/bar
    Actually: http://a.com/bar

    This function fix that.
    """
    return '/'.join([u.strip("/") for u in urls])


def roundint(i):
    return int(round(i, 0))


def namedlock(name):
    """
    Returns:
        threading.Lock
    """
    if not hasattr(namedlock, 'locks'):
        namedlock.locks = defaultdict(threading.Lock)
    return namedlock.locks[name]


def httpdo(url, method="GET", data=None) -> attrdict.AttrDict:
    """
    thread safe http request

    Raises:
        WDAError, WDARequestError, WDAEmptyResponseError
    """
    p = urlparse(url)
    with namedlock(p.scheme + "://" + p.netloc):
        return _unsafe_httpdo(url, method, data)


@functools.lru_cache(1024)
def _requests_session_pool_get(scheme, netloc):
    return requests_usbmux.Session()


def _is_tmq_platform() -> bool:
    return os.getenv("TMQ") == "true"

def _unsafe_httpdo(url, method='GET', data=None):
    """
    Do HTTP Request
    """
    start = time.time()
    if DEBUG:
        body = json.dumps(data) if data else ''
        print("Shell$ curl -X {method} -d '{body}' '{url}'".format(
            method=method.upper(), body=body or '', url=url))

    try:
        u = urlparse(url)
        request_session = _requests_session_pool_get(u.scheme, u.netloc)
        response = request_session.request(method,
                                           url,
                                           json=data,
                                           timeout=HTTP_TIMEOUT)
    except (requests.ConnectionError, requests.ReadTimeout) as e:
        raise

    if response.status_code == 502:  # Bad Gateway
        raise WDABadGateway(response.status_code, response.text)

    if DEBUG:
        ms = (time.time() - start) * 1000
        print('Return ({:.0f}ms): {}'.format(ms, response.text))

    try:
        retjson = response.json()
        retjson['status'] = retjson.get('status', 0)
        r = convert(retjson)

        if isinstance(r.value, dict) and r.value.get("error"):
            status = Status.ERROR
            value = r.value.copy()
            value.pop("traceback", None)

            for errCls in (WDAInvalidSessionIdError, WDAPossiblyCrashedError, WDAKeyboardNotPresentError, WDAUnknownError):
                if errCls.check(value):
                    raise errCls(status, value)

            raise WDARequestError(status, value)
        return r
    except JSONDecodeError:
        if response.text == "":
            raise WDAEmptyResponseError(method, url, data)
        raise WDAError(method, url, response.text)
    except requests.ConnectionError as e:
        raise WDAError("Failed to establish connection to to WDA")


class Rect(list):
    def __init__(self, x, y, width, height):
        super().__init__([x, y, width, height])
        self.__dict__.update({
            "x": x,
            "y": y,
            "width": width,
            "height": height
        })

    def __str__(self):
        return 'Rect(x={x}, y={y}, width={w}, height={h})'.format(
            x=self.x, y=self.y, w=self.width, h=self.height)

    def __repr__(self):
        return str(self)

    @property
    def center(self):
        return namedtuple('Point', ['x', 'y'])(self.x + self.width // 2,
                                               self.y + self.height // 2)

    @property
    def origin(self):
        return namedtuple('Point', ['x', 'y'])(self.x, self.y)

    @property
    def left(self):
        return self.x

    @property
    def top(self):
        return self.y

    @property
    def right(self):
        return self.x + self.width

    @property
    def bottom(self):
        return self.y + self.height


class BaseClient(object):
    def __init__(self, url=None, _session_id=None):
        """
        Args:
            target (string): the device url
        
        If target is empty, device url will set to env-var "DEVICE_URL" if defined else set to "http://localhost:8100"
        """
        if not url:
            url = os.environ.get('DEVICE_URL', 'http://localhost:8100')
        assert re.match(r"^(usbmux|https?)://", url), "Invalid URL: %r" % url

        # Session variable
        self.__wda_url = url
        self.__session_id = _session_id
        self.__is_app = bool(_session_id)  # set to freeze session_id
        self.__timeout = 30.0
        self.__callbacks = defaultdict(list)
        self.__callback_depth = 0
        self.__callback_running = False

        if not _session_id:
            self._init_callback()

    def _callback_fix_invalid_session_id(self, err: WDAError):
        """ 当遇到 invalid session id错误时，更新session id并重试 """
        if isinstance(err, WDAInvalidSessionIdError): # and not self.__is_app:
            self.session_id = None
            return Callback.RET_RETRY
        if isinstance(err, WDAPossiblyCrashedError):
            self.session_id = self.session().session_id # generate new sessionId
            return Callback.RET_RETRY
        """ 等待设备恢复上线 """

    def _callback_wait_ready(self, err):
        logger.warning("Error: %s", err)
        if isinstance(err, (ConnectionError, requests.ConnectionError,
                            requests.ReadTimeout, WDABadGateway)):
            if not self.wait_ready(DEVICE_WAIT_TIMEOUT):  # 等待设备恢复在线
                return Callback.RET_ABORT
            return Callback.RET_RETRY

    def _callback_tmq_before_send_keys(self, urlpath: str):
        if urlpath.endswith("/wda/keys"):
            if self.alert.exists:
                self.alert.accept()
            print("send_keys callback called")

    def _callback_tmq_print_error(self, method, url, data, err):
        if 'no such alert' in str(err):  # too many this error
            return

        logger.warning(
            "HTTP Error happens, this message is printed for better debugging")
        body = json.dumps(data) if data else ''
        logger.warning("Shell$ curl -X {method} -d '{body}' '{url}'".format(
            method=method.upper(), body=body or '', url=url))
        logger.warning("Error: %s", err)

    def _init_callback(self):
        self.register_callback(Callback.ERROR,
                               self._callback_fix_invalid_session_id)
        if _is_tmq_platform():
            # 输入之前处理弹窗
            # 出现错误是print出来，方便调试
            logger.info("register callbacks for tmq")
            self.register_callback(Callback.ERROR, self._callback_wait_ready)
            self.register_callback(Callback.HTTP_REQUEST_BEFORE,
                                   self._callback_tmq_before_send_keys)
            self.register_callback(Callback.ERROR,
                                   self._callback_tmq_print_error)

    def _callback_json_report(self, method, urlpath):
        """ TODO: ssx """
        pass

    def _set_output_report(self, filename: str):
        """
        Args:
            filename: json log
        """
        self.register_callback(Callback.HTTP_REQUEST_BEFORE, self._callback_json_report)

    def is_ready(self) -> bool:
        try:
            self.status()
            return True
        except:
            return False

    def wait_ready(self, timeout=120, noprint=False) -> bool:
        """
        wait until WDA back to normal

        Returns:
            bool (if wda works)
        """
        deadline = time.time() + timeout

        def _dprint(message: str):
            if noprint:
                return
            print(time.ctime(), message)

        _dprint("Wait ready (timeout={:.1f})".format(timeout))
        while time.time() < deadline:
            if self.is_ready():
                _dprint("device back online")
                return True
            else:
                _dprint("wait_ready left {:.1f} seconds".format(deadline -
                                                                time.time()))
                time.sleep(1.0)
        _dprint("device still offline")
        return False

    @retry.retry(exceptions=WDAEmptyResponseError, tries=3, delay=2)
    def status(self):
        res = self.http.get('status')
        res["value"]['sessionId'] = res.get("sessionId")
        # Can't use res.value['sessionId'] = ...
        return res.value

    def register_callback(self, event_name: str, func: Callable):
        self.__callbacks[event_name].append(func)

    def unregister_callback(self,
                            event_name: Optional[str] = None,
                            func: Optional[Callable] = None):
        """ 反注册 """
        if event_name is None:
            self.__callbacks.clear()
        elif func is None:
            self.__callbacks[event_name].clear()
        else:
            self.__callbacks[event_name].remove(func)

    def _run_callback(self, event_name, callbacks,
                      **kwargs) -> Union[None, Callback]:
        """ 运行回调函数 """
        if not callbacks:
            return

        self.__callback_running = True
        try:
            for fn in callbacks[event_name]:
                ret = inject_call(fn, **kwargs)
                if ret in [
                        Callback.RET_RETRY, Callback.RET_ABORT,
                        Callback.RET_CONTINUE
                ]:
                    return ret
        finally:
            self.__callback_running = False

    @property
    def callbacks(self):
        return self.__callbacks

    @limit_call_depth(4)
    def _fetch(self,
               method: str,
               urlpath: str,
               data: Optional[dict] = None,
               with_session: bool = False) -> attrdict.AttrDict:
        """ do http request """
        urlpath = "/" + urlpath.lstrip("/")  # urlpath always startswith /

        callbacks = self.__callbacks

        if self.__callback_running:
            callbacks = None

        url = urljoin(self.__wda_url, urlpath)

        run_callback = functools.partial(self._run_callback,
                                         callbacks=callbacks,
                                         method=method,
                                         url=url,
                                         urlpath=urlpath,
                                         with_session=with_session,
                                         data=data,
                                         client=self)

        try:
            if with_session:
                url = urljoin(self.__wda_url, "session", self.session_id,
                              urlpath)
            run_callback(Callback.HTTP_REQUEST_BEFORE)
            response = httpdo(url, method, data)
            run_callback(Callback.HTTP_REQUEST_AFTER, response=response)
            return response
        except Exception as err:
            ret = run_callback(Callback.ERROR, err=err)
            if ret == Callback.RET_RETRY:
                return self._fetch(method, urlpath, data, with_session)
            elif ret == Callback.RET_CONTINUE:
                return
            else:
                raise

    @property
    def http(self):
        return namedtuple("HTTPRequest", ['fetch', 'get', 'post'])(
            self._fetch,
            functools.partial(self._fetch, "GET"),
            functools.partial(self._fetch, "POST")) # yapf: disable

    @property
    def _session_http(self):
        return namedtuple("HTTPSessionRequest", ['fetch', 'get', 'post', 'delete'])(
            functools.partial(self._fetch, with_session=True),
            functools.partial(self._fetch, "GET", with_session=True),
            functools.partial(self._fetch, "POST", with_session=True),
            functools.partial(self._fetch, "DELETE", with_session=True)) # yapf: disable

    def home(self):
        """Press home button"""
        try:
            self.http.post('/wda/homescreen')
        except WDARequestError as e:
            if "Timeout waiting until SpringBoard is visible" in str(e):
                return
            raise

    def healthcheck(self):
        """Hit healthcheck"""
        return self.http.get('/wda/healthcheck')

    def locked(self):
        """ returns locked status, true or false """
        return self.http.get("/wda/locked").value

    def lock(self):
        return self.http.post('/wda/lock')

    def unlock(self):
        """ unlock screen, double press home """
        return self.http.post('/wda/unlock')

    def sleep(self, secs: float):
        """ same as time.sleep """
        time.sleep(secs)

    @retry.retry(WDAUnknownError, tries=3, delay=.5, jitter=.2)
    def app_current(self) -> dict:
        """
        Returns:
            dict, eg:
            {"pid": 1281,
             "name": "",
             "bundleId": "com.netease.cloudmusic"}
        """
        return self.http.get("/wda/activeAppInfo").value

    def source(self, format='xml', accessible=False):
        """
        Args:
            format (str): only 'xml' and 'json' source types are supported
            accessible (bool): when set to true, format is always 'json'
        """
        if accessible:
            return self.http.get('/wda/accessibleSource').value
        return self.http.get('source?format=' + format).value

    def screenshot(self, png_filename=None, format='pillow'):
        """
        Screenshot with PNG format

        Args:
            png_filename(string): optional, save file name
            format(string): return format, "raw" or "pillow” (default)
        
        Returns:
            PIL.Image or raw png data
        
        Raises:
            WDARequestError
        """
        value = self.http.get('screenshot').value
        raw_value = base64.b64decode(value)
        png_header = b"\x89PNG\r\n\x1a\n"
        if not raw_value.startswith(png_header) and png_filename:
            raise WDARequestError(-1, "screenshot png format error")

        if png_filename:
            with open(png_filename, 'wb') as f:
                f.write(raw_value)

        if format == 'raw':
            return raw_value
        elif format == 'pillow':
            from PIL import Image
            buff = io.BytesIO(raw_value)
            return Image.open(buff)
        else:
            raise ValueError("unknown format")

    def session(self,
                bundle_id=None,
                arguments: Optional[list] = None,
                environment: Optional[dict] = None,
                alert_action: Optional[AlertAction] = None):
        """
        Launch app in a session

        Args:
            - bundle_id (str): the app bundle id
            - arguments (list): ['-u', 'https://www.google.com/ncr']
            - enviroment (dict): {"KEY": "VAL"}
            - alert_action (AlertAction): AlertAction.ACCEPT or AlertAction.DISMISS

        WDA Return json like

        {
            "value": {
                "sessionId": "69E6FDBA-8D59-4349-B7DE-A9CA41A97814",
                "capabilities": {
                    "device": "iphone",
                    "browserName": "部落冲突",
                    "sdkVersion": "9.3.2",
                    "CFBundleIdentifier": "com.supercell.magic"
                }
            },
            "sessionId": "69E6FDBA-8D59-4349-B7DE-A9CA41A97814",
            "status": 0
        }

        To create a new session, send json data like

        {
            "capabilities": {
                "alwaysMatch": {
                    "bundleId": "your-bundle-id",
                    "app": "your-app-path"
                    "shouldUseCompactResponses": (bool),
                    "shouldUseTestManagerForVisibilityDetection": (bool),
                    "maxTypingFrequency": (integer),
                    "arguments": (list(str)),
                    "environment": (dict: str->str)
                }
            },
        }

        Or {"capabilities": {}}
        """
        # if not bundle_id:
        #     # 旧版的WDA创建Session不允许bundleId为空，但是总是可以拿到sessionId
        #     # 新版的WDA允许bundleId为空，但是初始状态没有sessionId
        #     session_id = self.status().get("sessionId")
        #     if session_id:
        #         return self

        capabilities = {}
        if bundle_id:
            always_match = {
                "bundleId": bundle_id,
                "arguments": arguments or [],
                "environment": environment or {},
                "shouldWaitForQuiescence": False,
            }
            if alert_action:
                assert alert_action in ["accept", "dismiss"]
                capabilities["defaultAlertAction"] = alert_action

            capabilities['alwaysMatch'] = always_match

        payload = {
            "capabilities": capabilities,
            "desiredCapabilities": capabilities.get('alwaysMatch',
                                                    {}),  # 兼容旧版的wda
        }

        try:
            res = self.http.post('session', payload)
        except WDAEmptyResponseError:
            """ when there is alert, might be got empty response
            use /wda/apps/state may still get sessionId
            """
            res = self.session().app_state(bundle_id)
            if res.value != 4:
                raise
        client = Client(self.__wda_url, _session_id=res.sessionId)
        client.__timeout = self.__timeout
        client.__callbacks = self.__callbacks
        return client

    def close(self):  # close session
        try:
            return self._session_http.delete('/')
        except WDARequestError as e:
            if not isinstance(e, (WDAInvalidSessionIdError, WDAPossiblyCrashedError)):
                raise

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#
    ######  Session methods and properties ######
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#
    def __enter__(self):
        """
        Usage example:
            with c.session("com.example.app") as app:
                # do something
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    @property
    @deprecated(version="1.0.0", reason="Use session_id instread id")
    def id(self):
        return self._get_session_id()

    @property
    def session_id(self) -> str:
        if self.__session_id:
            return self.__session_id
        current_sid = self.status()['sessionId']
        if current_sid:
            self.__session_id = current_sid  # store old session id to reduce request count
            return current_sid
        return self.session().session_id

    @session_id.setter
    def session_id(self, value):
        self.__session_id = value

    def _get_session_id(self) -> str:
        return self.session_id

    @cached_property
    def scale(self):
        """
        UIKit scale factor
        
        Refs:
            https://developer.apple.com/library/archive/documentation/DeviceInformation/Reference/iOSDeviceCompatibility/Displays/Displays.html
        There is another way to get scale
            self.http.get("/wda/screen").value returns {"statusBarSize": {'width': 320, 'height': 20}, 'scale': 2}
        """
        v = max(self.screenshot().size) / max(self.window_size())
        return round(v)

    @cached_property
    def bundle_id(self):
        """ the session matched bundle id """
        v = self._session_http.get("/").value
        return v['capabilities'].get('CFBundleIdentifier')

    def implicitly_wait(self, seconds):
        """
        set default element search timeout
        """
        assert isinstance(seconds, (int, float))
        self.__timeout = seconds

    def battery_info(self):
        """
        Returns dict: (I do not known what it means)
            eg: {"level": 1, "state": 2}
        """
        return self._session_http.get("/wda/batteryInfo").value

    def device_info(self):
        """
        Returns dict:
            eg: {'currentLocale': 'zh_CN', 'timeZone': 'Asia/Shanghai'}
        """
        return self._session_http.get("/wda/device/info").value

    @property
    def info(self):
        """
        Returns:
            {'timeZone': 'Asia/Shanghai',
            'currentLocale': 'zh_CN',
            'model': 'iPhone',
            'uuid': '9DAC43B3-6887-428D-B5D5-4892D1F38BAA',
            'userInterfaceIdiom': 0,
            'userInterfaceStyle': 'unsupported',
            'name': 'iPhoneSE',
            'isSimulator': False}
        """
        return self.device_info()

    def set_clipboard(self, content, content_type="plaintext"):
        """ set clipboard """
        self._session_http.post(
            "/wda/setPasteboard", {
                "content": base64.b64encode(content.encode()).decode(),
                "contentType": content_type
            })

    @deprecated(version="1.0.0", reason="This method is deprecated now.")
    def set_alert_callback(self, callback):
        """
        Args:
            callback (func): called when alert popup
        
        Example of callback:

            def callback(session):
                session.alert.accept()
        """
        pass

    #Not working
    #def get_clipboard(self):
    #    return self.http.post("/wda/getPasteboard").value

    # Not working
    #def siri_activate(self, text):
    #    self.http.post("/wda/siri/activate", {"text": text})

    def app_launch(self,
                   bundle_id,
                   arguments=[],
                   environment={},
                   wait_for_quiescence=False):
        """
        Args:
            - bundle_id (str): the app bundle id
            - arguments (list): ['-u', 'https://www.google.com/ncr']
            - enviroment (dict): {"KEY": "VAL"}
            - wait_for_quiescence (bool): default False
        """
        # Deprecated, use app_start instead
        assert isinstance(arguments, (tuple, list))
        assert isinstance(environment, dict)

        return self._session_http.post(
            "/wda/apps/launch", {
                "bundleId": bundle_id,
                "arguments": arguments,
                "environment": environment,
                "shouldWaitForQuiescence": wait_for_quiescence,
            })

    def app_activate(self, bundle_id):
        return self._session_http.post("/wda/apps/launch", {
            "bundleId": bundle_id,
        })

    def app_terminate(self, bundle_id):
        # Deprecated, use app_stop instead
        return self._session_http.post("/wda/apps/terminate", {
            "bundleId": bundle_id,
        })

    def app_state(self, bundle_id):
        """
        Returns example:
            {
                "value": 4,
                "sessionId": "0363BDC5-4335-47ED-A54E-F7CCB65C6A65"
            }
        
        value 1(not running) 2(running in background) 3(running in foreground)
        """
        return self._session_http.post("/wda/apps/state", {
            "bundleId": bundle_id,
        })

    def app_start(self,
                  bundle_id,
                  arguments=[],
                  environment={},
                  wait_for_quiescence=False):
        """ alias for app_launch """
        return self.app_launch(bundle_id, arguments, environment,
                               wait_for_quiescence)

    def app_stop(self, bundle_id: str):
        """ alias for app_terminate """
        self.app_terminate(bundle_id)

    def app_list(self):
        """
        Not working very well, only show springboard

        Returns:
            list of app
        
        Return example:
            [{'pid': 52, 'bundleId': 'com.apple.springboard'}]
        """
        return self._session_http.get("/wda/apps/list").value

    def open_url(self, url):
        """
        TODO: Never successed using before. Looks like use Siri to search.
        https://github.com/facebook/WebDriverAgent/blob/master/WebDriverAgentLib/Commands/FBSessionCommands.m#L43
        Args:
            url (str): url
        
        Raises:
            WDARequestError
        """
        return self._session_http.post('url', {'url': url})

    def deactivate(self, duration):
        """Put app into background and than put it back
        Args:
            - duration (float): deactivate time, seconds
        """
        return self._session_http.post('/wda/deactivateApp',
                                       dict(duration=duration))

    def tap(self, x, y):
        if _is_tmq_platform() and os.environ.get(
                "TMQ_ORIGIN") == "civita":  # in TMQ and belong to MDS
            return self._session_http.post("/mds/touchAndHold",
                                           dict(x=x, y=y, duration=0.02))
        return self._session_http.post('/wda/tap/0', dict(x=x, y=y))

    def _percent2pos(self, x, y, window_size=None):
        if any(isinstance(v, float) for v in [x, y]):
            w, h = window_size or self.window_size()
            x = int(x * w) if isinstance(x, float) else x
            y = int(y * h) if isinstance(y, float) else y
            assert w >= x >= 0
            assert h >= y >= 0
        return (x, y)

    def click(self, x, y, duration: Optional[float] = None):
        """
        Combine tap and tap_hold
        
        Args:
            x, y: can be float(percent) or int
            duration (optional): tap_hold duration
        """
        x, y = self._percent2pos(x, y)
        if duration:
            return self.tap_hold(x, y, duration)
        return self.tap(x, y)

    def double_tap(self, x, y):
        x, y = self._percent2pos(x, y)
        return self._session_http.post('/wda/doubleTap', dict(x=x, y=y))

    def tap_hold(self, x, y, duration=1.0):
        """
        Tap and hold for a moment

        Args:
            - x, y(int, float): float(percent) or int(absolute coordicate)
            - duration(float): seconds of hold time

        [[FBRoute POST:@"/wda/touchAndHold"] respondWithTarget:self action:@selector(handleTouchAndHoldCoordinate:)],
        """
        x, y = self._percent2pos(x, y)
        data = {'x': x, 'y': y, 'duration': duration}
        return self._session_http.post('/wda/touchAndHold', data=data)

    def swipe(self, x1, y1, x2, y2, duration=0):
        """
        Args:
            x1, y1, x2, y2 (int, float): float(percent), int(coordicate)
            duration (float): start coordinate press duration (seconds)

        [[FBRoute POST:@"/wda/dragfromtoforduration"] respondWithTarget:self action:@selector(handleDragCoordinate:)],
        """
        if any(isinstance(v, float) for v in [x1, y1, x2, y2]):
            size = self.window_size()
            x1, y1 = self._percent2pos(x1, y1, size)
            x2, y2 = self._percent2pos(x2, y2, size)

        data = dict(fromX=x1, fromY=y1, toX=x2, toY=y2, duration=duration)
        return self._session_http.post('/wda/dragfromtoforduration', data=data)

    def _fast_swipe(self, x1, y1, x2, y2, velocity: int = 500):
        """
        velocity: the larger the faster
        """
        data = dict(fromX=x1, fromY=y1, toX=x2, toY=y2, velocity=velocity)
        return self._session_http.post('/wda/drag', data=data)

    def swipe_left(self):
        """ swipe right to left """
        w, h = self.window_size()
        return self.swipe(w, h // 2, 1, h // 2)

    def swipe_right(self):
        """ swipe left to right """
        w, h = self.window_size()
        return self.swipe(1, h // 2, w, h // 2)

    def swipe_up(self):
        """ swipe from center to top """
        w, h = self.window_size()
        return self.swipe(w // 2, h // 2, w // 2, 1)

    def swipe_down(self):
        """ swipe from center to bottom """
        w, h = self.window_size()
        return self.swipe(w // 2, h // 2, w // 2, h - 1)

    def _fast_swipe_ext(self, direction: str):
        if direction == "up":
            w, h = self.window_size()
            return self.swipe(w // 2, h // 2, w // 2, 1)
        elif direction == "down":
            w, h = self.window_size()
            return self._fast_swipe(w // 2, h // 2, w // 2, h - 1)
        else:
            raise RuntimeError("not supported direction:", direction)

    @property
    def orientation(self):
        """
        Return string
        One of <PORTRAIT | LANDSCAPE>
        """
        for _ in range(3):
            result = self._session_http.get('orientation').value
            if result:
                return result
            time.sleep(.5)

    @orientation.setter
    def orientation(self, value):
        """
        Args:
            - orientation(string): LANDSCAPE | PORTRAIT | UIA_DEVICE_ORIENTATION_LANDSCAPERIGHT |
                    UIA_DEVICE_ORIENTATION_PORTRAIT_UPSIDEDOWN
        """
        return self._session_http.post('orientation',
                                       data={'orientation': value})

    def window_size(self):
        """
        Returns:
            namedtuple: eg
                Size(width=320, height=568)
        """
        size = self._unsafe_window_size()
        if min(size) > 0:
            return size
        # FIXME(ssx): launch another app is not a good idea, but I did'nt found some other way
        self.unlock()
        self.session("com.apple.Preferences")
        return self._unsafe_window_size()

    def _unsafe_window_size(self):
        """
        returns (width, height) might be (0, 0)
        """
        value = self._session_http.get('/window/size').value
        w = roundint(value['width'])
        h = roundint(value['height'])
        return namedtuple('Size', ['width', 'height'])(w, h)

    @retry.retry(WDAKeyboardNotPresentError, tries=3, delay=1.0)
    def send_keys(self, value):
        """
        send keys, yet I know not, todo function
        """
        if isinstance(value, six.string_types):
            value = list(value)
        return self._session_http.post('/wda/keys', data={'value': value})

    def press(self, name: str):
        """
        Args:
            name: one of <home|volumeUp|volumeDown>
        """
        valid_names = ("home", "volumeUp", "volumeDown")
        if name not in valid_names:
            raise ValueError(
                f"Invalid name: {name}, should be one of {valid_names}")
        self._session_http.post("/wda/pressButton", {"name": name})

    def keyboard_dismiss(self):
        """
        Not working for now
        """
        raise RuntimeError("not pass tests, this method is not allowed to use")
        self._session_http.post('/wda/keyboard/dismiss')

    def appium_settings(self, value: Optional[dict] = None) -> dict:
        """
        Get and set /session/$sessionId/appium/settings
        """
        if value is None:
            return self._session_http.get("/appium/settings").value
        return self._session_http.post("/appium/settings",
                                       data={
                                           "settings": value
                                       }).value

    def xpath(self, value):
        """
        For weditor, d.xpath(...)
        """
        return Selector(self, xpath=value)

    def __call__(self, *args, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.__timeout
        return Selector(self, *args, **kwargs)

    @property
    def alibaba(self):
        """ Only used in alibaba company """
        try:
            import wda_taobao
            return wda_taobao.Alibaba(self)
        except ImportError:
            raise RuntimeError(
                "@alibaba property requires wda_taobao library installed")

    @property
    def taobao(self):
        try:
            import wda_taobao
            return wda_taobao.Taobao(self)
        except ImportError:
            raise RuntimeError(
                "@taobao property requires wda_taobao library installed")


class Alert(object):
    DEFAULT_ACCEPT_BUTTONS = []

    def __init__(self, client: BaseClient):
        self._c = client
        self.http = client._session_http

    @property
    def exists(self):
        try:
            self.text
            return True
        except WDARequestError as e:
            # expect e.status != 27 in old version and e.value == 'no such alert' in new version
            return False

    @property
    def text(self):
        return self.http.get('/alert/text').value

    def wait(self, timeout=20.0):
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.exists:
                return True
            time.sleep(0.2)
        return False

    def accept(self):
        return self.http.post('/alert/accept')

    def dismiss(self):
        return self.http.post('/alert/dismiss')

    def buttons(self):
        return self.http.get('/wda/alert/buttons').value

    def click(self, button_name: Union[str, list]):
        """
        Args:
            - button_name: the name of the button

        Raises:
            ValueError when button_name is not in avaliable button names
        """
        # Actually, It has no difference POST to accept or dismiss
        if isinstance(button_name, str):
            return self.http.post('/alert/accept', data={"name": button_name})
        avaliable_names = self.buttons()
        for bname in button_name:
            if bname in avaliable_names:
                return self.http.post('/alert/accept', data={"name": bname})
        raise ValueError("Only these buttons can be clicked", avaliable_names)

    @contextlib.contextmanager
    def watch_and_click(self,
                        buttons: Optional[list] = [
                            "使用App时允许", "无线局域网与蜂窝网络", "好", "稍后", "稍后提醒", "确定",
                            "允许", "以后", "打开", "录屏"
                        ],
                        interval: float = 2.0):
        """ watch and click button
        Args:
            buttons: buttons name which need to click
            interval: check interval
        """
        event = threading.Event()

        def _inner():
            while not event.is_set():
                try:
                    alert_buttons = self.buttons()
                    logger.info("Alert detected, buttons: %s", alert_buttons)
                    for btn_name in buttons:
                        if btn_name in alert_buttons:
                            logger.info("Alert click: %s", btn_name)
                            self.click(btn_name)
                            break
                    else:
                        logger.warning("Alert not handled")
                except WDARequestError:
                    pass
                time.sleep(interval)

        threading.Thread(name="alert", target=_inner, daemon=True).start()
        yield None
        event.set()


class Client(BaseClient):
    @property
    def alert(self) -> Alert:
        return Alert(self)


Session = Client  # for compability


class Selector(object):
    def __init__(self,
                 session: Session,
                 predicate=None,
                 id=None,
                 className=None,
                 type=None,
                 name=None,
                 nameContains=None,
                 nameMatches=None,
                 text=None,
                 textContains=None,
                 textMatches=None,
                 value=None,
                 valueContains=None,
                 label=None,
                 labelContains=None,
                 visible=None,
                 enabled=None,
                 classChain=None,
                 xpath=None,
                 parent_class_chains=[],
                 timeout=10.0,
                 index=0):
        '''
        Args:
            predicate (str): predicate string
            id (str): raw identifier
            className (str): attr of className
            type (str): alias of className
            name (str): attr for name
            nameContains (str): attr of name contains
            nameMatches (str): regex string
            text (str): alias of name
            textContains (str): alias of nameContains
            textMatches (str): alias of nameMatches
            value (str): attr of value, not used in most times
            valueContains (str): attr of value contains
            label (str): attr for label
            labelContains (str): attr for label contains
            visible (bool): is visible
            enabled (bool): is enabled
            classChain (str): string of ios chain query, eg: **/XCUIElementTypeOther[`value BEGINSWITH 'blabla'`]
            xpath (str): xpath string, a little slow, but works fine
            timeout (float): maxium wait element time, default 10.0s
            index (int): index of founded elements
        
        WDA use two key to find elements "using", "value"
        Examples:
        "using" can be on of 
            "partial link text", "link text"
            "name", "id", "accessibility id"
            "class name", "class chain", "xpath", "predicate string"
        
        predicate string support many keys
            UID,
            accessibilityContainer,
            accessible,
            enabled,
            frame,
            label,
            name,
            rect,
            type,
            value,
            visible,
            wdAccessibilityContainer,
            wdAccessible,
            wdEnabled,
            wdFrame,
            wdLabel,
            wdName,
            wdRect,
            wdType,
            wdUID,
            wdValue,
            wdVisible
        '''
        assert isinstance(session, Session)
        self._session = session

        self._predicate = predicate
        self._id = id
        self._class_name = className or type
        self._name = self._add_escape_character_for_quote_prime_character(
            name or text)
        self._name_part = nameContains or textContains
        self._name_regex = nameMatches or textMatches
        self._value = value
        self._value_part = valueContains
        self._label = label
        self._label_part = labelContains
        self._enabled = enabled
        self._visible = visible
        self._index = index

        self._xpath = self._fix_xcui_type(xpath)
        self._class_chain = self._fix_xcui_type(classChain)
        self._timeout = timeout
        # some fixtures
        if self._class_name and not self._class_name.startswith(
                'XCUIElementType'):
            self._class_name = 'XCUIElementType' + self._class_name
        if self._name_regex:
            if not self._name_regex.startswith(
                    '^') and not self._name_regex.startswith('.*'):
                self._name_regex = '.*' + self._name_regex
            if not self._name_regex.endswith(
                    '$') and not self._name_regex.endswith('.*'):
                self._name_regex = self._name_regex + '.*'
        self._parent_class_chains = parent_class_chains

    @property
    def http(self):
        return self._session._session_http

    def _fix_xcui_type(self, s):
        if s is None:
            return
        re_element = '|'.join(xcui_element_types.ELEMENTS)
        return re.sub(r'/(' + re_element + ')', '/XCUIElementType\g<1>', s)

    def _add_escape_character_for_quote_prime_character(self, text):
        """
        Fix for https://github.com/openatx/facebook-wda/issues/33
        Returns:
            string with properly formated quotes, or non changed text
        """
        if text is not None:
            if "'" in text:
                return text.replace("'", "\\'")
            elif '"' in text:
                return text.replace('"', '\\"')
            else:
                return text
        else:
            return text

    def _wdasearch(self, using, value):
        """
        Returns:
            element_ids (list(string)): example ['id1', 'id2']
        
        HTTP example response:
        [
            {"ELEMENT": "E2FF5B2A-DBDF-4E67-9179-91609480D80A"},
            {"ELEMENT": "597B1A1E-70B9-4CBE-ACAD-40943B0A6034"}
        ]
        """
        element_ids = []
        for v in self.http.post('/elements', {
                'using': using,
                'value': value
        }).value:
            element_ids.append(v['ELEMENT'])
        return element_ids

    def _gen_class_chain(self):
        # just return if aleady exists predicate
        if self._predicate:
            return '/XCUIElementTypeAny[`' + self._predicate + '`]'
        qs = []
        if self._name:
            qs.append("name == '%s'" % self._name)
        if self._name_part:
            qs.append("name CONTAINS '%s'" % self._name_part)
        if self._name_regex:
            qs.append("name MATCHES '%s'" %
                      self._name_regex.encode('unicode_escape'))
        if self._label:
            qs.append("label == '%s'" % self._label)
        if self._label_part:
            qs.append("label CONTAINS '%s'" % self._label_part)
        if self._value:
            qs.append("value == '%s'" % self._value)
        if self._value_part:
            qs.append("value CONTAINS ’%s'" % self._value_part)
        if self._visible is not None:
            qs.append("visible == %s" % 'true' if self._visible else 'false')
        if self._enabled is not None:
            qs.append("enabled == %s" % 'true' if self._enabled else 'false')
        predicate = ' AND '.join(qs)
        chain = '/' + (self._class_name or 'XCUIElementTypeAny')
        if predicate:
            chain = chain + '[`' + predicate + '`]'
        if self._index:
            chain = chain + '[%d]' % self._index
        return chain

    def find_element_ids(self):
        elems = []
        if self._id:
            return self._wdasearch('id', self._id)
        if self._predicate:
            return self._wdasearch('predicate string', self._predicate)
        if self._xpath:
            return self._wdasearch('xpath', self._xpath)
        if self._class_chain:
            return self._wdasearch('class chain', self._class_chain)

        chain = '**' + ''.join(
            self._parent_class_chains) + self._gen_class_chain()
        if DEBUG:
            print('CHAIN:', chain)
        return self._wdasearch('class chain', chain)

    def find_elements(self):
        """
        Returns:
            Element (list): all the elements
        """
        es = []
        for element_id in self.find_element_ids():
            e = Element(self._session, element_id)
            es.append(e)
        return es

    def count(self):
        return len(self.find_element_ids())

    def get(self, timeout=None, raise_error=True):
        """
        Args:
            timeout (float): timeout for query element, unit seconds
                Default 10s
            raise_error (bool): whether to raise error if element not found

        Returns:
            Element: UI Element

        Raises:
            WDAElementNotFoundError if raise_error is True else None
        """
        start_time = time.time()
        if timeout is None:
            timeout = self._timeout
        while True:
            elems = self.find_elements()
            if len(elems) > 0:
                return elems[0]
            if start_time + timeout < time.time():
                break
            time.sleep(0.5)

        if raise_error:
            raise WDAElementNotFoundError("element not found",
                                          "timeout %.1f" % timeout)

    def __getattr__(self, oper):
        if oper.startswith("_"):
            raise AttributeError("invalid attr", oper)
        if not hasattr(Element, oper):
            raise AttributeError("'Element' object has no attribute %r" % oper)

        el = self.get()
        return getattr(el, oper)

    def set_timeout(self, s):
        """
        Set element wait timeout
        """
        self._timeout = s
        return self

    def __getitem__(self, index):
        self._index = index
        return self

    def child(self, *args, **kwargs):
        chain = self._gen_class_chain()
        kwargs['parent_class_chains'] = self._parent_class_chains + [chain]
        return Selector(self._session, *args, **kwargs)

    @property
    def exists(self):
        return len(self.find_element_ids()) > self._index

    def click(self, timeout: Optional[float] = None):
        """
        Click element

        Args:
            timeout (float): max wait seconds
        """
        e = self.get(timeout=timeout)
        e.click()

    def click_exists(self, timeout=0):
        """
        Wait element and perform click

        Args:
            timeout (float): timeout for wait
        
        Returns:
            bool: if successfully clicked
        """
        e = self.get(timeout=timeout, raise_error=False)
        if e is None:
            return False
        e.click()
        return True

    def wait(self, timeout=None, raise_error=True):
        """ alias of get
        Args:
            timeout (float): timeout seconds
            raise_error (bool): default true, whether to raise error if element not found
        
        Raises:
            WDAElementNotFoundError
        """
        return self.get(timeout=timeout, raise_error=raise_error)

    def wait_gone(self, timeout=None, raise_error=True):
        """
        Args:
            timeout (float): default timeout
            raise_error (bool): return bool or raise error
        
        Returns:
            bool: works when raise_error is False

        Raises:
            WDAElementNotDisappearError
        """
        start_time = time.time()
        if timeout is None or timeout <= 0:
            timeout = self._timeout
        while start_time + timeout > time.time():
            if not self.exists:
                return True
        if not raise_error:
            return False
        raise WDAElementNotDisappearError("element not gone")

    # todo
    # pinch
    # touchAndHold
    # dragfromtoforduration
    # twoFingerTap

    # todo
    # handleGetIsAccessibilityContainer
    # [[FBRoute GET:@"/wda/element/:uuid/accessibilityContainer"] respondWithTarget:self action:@selector(handleGetIsAccessibilityContainer:)],


class Element(object):
    def __init__(self, session: Session, id: str):
        """
        base_url eg: http://localhost:8100/session/$SESSION_ID
        """
        self._session = session
        self._id = id

    def __repr__(self):
        return '<wda.Element(id="{}")>'.format(self._id)

    @property
    def http(self):
        return self._session._session_http

    def _req(self, method, url, data=None):
        return self.http.fetch(method, '/element/' + self._id + url, data)

    def _wda_req(self, method, url, data=None):
        return self.http.fetch(method, '/wda/element/' + self._id + url, data)

    def _prop(self, key):
        return self._req('get', '/' + key.lstrip('/')).value

    def _wda_prop(self, key):
        ret = self.http.get('/wda/element/%s/%s' % (self._id, key)).value
        return ret

    @property
    def info(self):
        return {
            "id": self.session_id,
            "label": self.label,
            "value": self.value,
            "text": self.text,
            "name": self.name,
            "className": self.className,
            "enabled": self.enabled,
            "displayed": self.displayed,
            "visible": self.visible,
            "accessible": self.accessible,
            "accessibilityContainer": self.accessibility_container
        }

    @property
    def id(self):
        return self._id

    @property
    def label(self):
        return self._prop('attribute/label')

    @property
    def className(self):
        return self._prop('attribute/type')

    @property
    def text(self):
        return self._prop('text')

    @property
    def name(self):
        return self._prop('name')

    @property
    def displayed(self):
        return self._prop("displayed")

    @property
    def enabled(self):
        return self._prop('enabled')

    @property
    def accessible(self):
        return self._wda_prop("accessible")

    @property
    def accessibility_container(self):
        return self._wda_prop('accessibilityContainer')

    @property
    def value(self):
        return self._prop('attribute/value')

    @property
    def visible(self):
        return self._prop('attribute/visible')

    @property
    def bounds(self) -> Rect:
        value = self._prop('rect')
        x, y = value['x'], value['y']
        w, h = value['width'], value['height']
        return Rect(x, y, w, h)

    # operations
    def tap(self):
        return self._req('post', '/click')

    def click(self):
        """
        Get element center position and do click, a little slower
        """
        # Some one reported, invisible element can not click
        # So here, git position and then do tap
        x, y = self.bounds.center
        self._session.click(x, y)
        # return self.tap()

    def tap_hold(self, duration=1.0):
        """
        Tap and hold for a moment

        Args:
            duration (float): seconds of hold time

        [[FBRoute POST:@"/wda/element/:uuid/touchAndHold"] respondWithTarget:self action:@selector(handleTouchAndHold:)],
        """
        return self._wda_req('post', '/touchAndHold', {'duration': duration})

    def scroll(self, direction='visible', distance=1.0):
        """
        Args:
            direction (str): one of "visible", "up", "down", "left", "right"
            distance (float): swipe distance, only works when direction is not "visible"
               
        Raises:
            ValueError

        distance=1.0 means, element (width or height) multiply 1.0
        """
        if direction == 'visible':
            self._wda_req('post', '/scroll', {'toVisible': True})
        elif direction in ['up', 'down', 'left', 'right']:
            self._wda_req('post', '/scroll', {
                'direction': direction,
                'distance': distance
            })
        else:
            raise ValueError("Invalid direction")
        return self

    # TvOS
    # @property
    # def focused(self):
    #
    # def focuse(self):

    def pickerwheel_select(self):
        """ Select by pickerwheel """
        # Ref: https://github.com/appium/WebDriverAgent/blob/e5d46a85fbdb22e401d396cedf0b5a9bbc995084/WebDriverAgentLib/Commands/FBElementCommands.m#L88
        raise NotImplementedError()

    def pinch(self, scale, velocity):
        """
        Args:
            scale (float): scale must > 0
            velocity (float): velocity must be less than zero when scale is less than 1
        
        Example:
            pinchIn  -> scale:0.5, velocity: -1
            pinchOut -> scale:2.0, velocity: 1
        """
        data = {'scale': scale, 'velocity': velocity}
        return self._wda_req('post', '/pinch', data)

    def set_text(self, value):
        return self._req('post', '/value', {'value': value})

    def clear_text(self):
        return self._req('post', '/clear')

    # def child(self, **kwargs):
    #     return Selector(self.__base_url, self._id, **kwargs)

    # todo lot of other operations
    # tap_hold


class USBClient(Client):
    """ connect device through unix:/var/run/usbmuxd """
    def __init__(self, udid: str = "", port: int = 8100):
        super().__init__(url="usbmux://{}:{}".format(udid, port))

        if not self.is_ready():
            self._start_xctest()

    def _start_xctest(self) -> bool:
        import shutil
        import subprocess
        tins_path = shutil.which("tins")
        if not tins_path:
            return False

        logger.info("WDA is not running, exec: tins xctest")
        p = subprocess.Popen([tins_path, 'xctest'])
        time.sleep(3)
        assert p.poll() is None
        return self.wait_ready()


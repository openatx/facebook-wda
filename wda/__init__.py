#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals


import functools
import json
import base64
import copy
import time
import re
from collections import namedtuple

import six
import requests
from . import xcui_element_types

if six.PY3:
    from urllib.parse import urljoin as _urljoin
    from functools import reduce
else:
    from urlparse import urljoin as _urljoin

DEBUG = False
HTTP_TIMEOUT = 60.0 # unit second

LANDSCAPE = 'LANDSCAPE'
PORTRAIT = 'PORTRAIT'
LANDSCAPE_RIGHT = 'UIA_DEVICE_ORIENTATION_LANDSCAPERIGHT'
PORTRAIT_UPSIDEDOWN = 'UIA_DEVICE_ORIENTATION_PORTRAIT_UPSIDEDOWN'


def convert(dictionary):
    """
    Convert dict to namedtuple
    """
    return namedtuple('GenericDict', list(dictionary.keys()))(**dictionary)


def urljoin(*urls):
    """
    The default urlparse.urljoin behavior look strange
    Standard urlparse.urljoin('http://a.com/foo', '/bar')
    Expect: http://a.com/foo/bar
    Actually: http://a.com/bar

    This function fix that.
    """
    return reduce(_urljoin, [u.strip('/')+'/' for u in urls if u.strip('/')], '').rstrip('/')

def roundint(i):
    return int(round(i, 0))


def httpdo(url, method='GET', data=None):
    """
    Do HTTP Request
    """
    if isinstance(data, dict):
        data = json.dumps(data)
    if DEBUG:
        print("Shell: curl -X {method} -d '{data}' '{url}'".format(method=method, data=data or '', url=url))

    fn = dict(GET=requests.get, POST=requests.post, DELETE=requests.delete)[method]
    try:
        response = fn(url, data=data, timeout=HTTP_TIMEOUT)
    except requests.exceptions.ConnectionError as e:
        # retry again
        print('retry to connect, error: {}'.format(e))
        time.sleep(1.0)
        response = fn(url, data=data, timeout=10)

    retjson = response.json()
    if DEBUG:
        print('Return: {}'.format(json.dumps(retjson, indent=4)))
    r = convert(retjson)
    if r.status != 0:
        raise WDAError(r.status, r.value)
    return r


class WDAError(Exception):
    def __init__(self, status, value):
        self.status = status
        self.value = value

    def __str__(self):
        return 'WDAError(status=%d, value=%s)' % (self.status, self.value)


class Rect(object):
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __str__(self):
        return 'Rect(x={x}, y={y}, width={w}, height={h})'.format(
            x=self.x, y=self.y, w=self.width, h=self.height)

    def __repr__(self):
        return str(self)

    @property
    def center(self):
        return namedtuple('Point', ['x', 'y'])(self.x+self.width/2, self.y+self.height/2)

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
        return self.x+self.width

    @property
    def bottom(self):
        return self.y+self.height


class Client(object):
    def __init__(self, target='http://127.0.0.1:8100'):
        """
        Args:
            - target(string): base URL of your iPhone, ex http://10.0.0.1:8100
        """
        self._target = target

    def _request(self, base_url, method='GET', data=None):
        return httpdo(urljoin(self._target, base_url), method, data)

    def status(self):
        res = self._request('status')
        sid = res.sessionId
        res.value['sessionId'] = sid
        return res.value

    def home(self):
        """Press home button"""
        return self._request('/wda/homescreen', 'POST')

    def healthcheck(self):
        """Hit healthcheck"""
        return self._request('/wda/healthcheck', 'GET')

    def source(self, accessible=False):
        if accessible:
            return self._request('/wda/accessibleSource', 'GET').value
        return self._request('source', 'GET').value

    def session(self, bundle_id=None):
        """
        Args:
            - bundle_id(str): the app bundle id

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
        """
        if bundle_id is None:
            sid = self.status()['sessionId']
            if not sid:
                raise RuntimeError("no session created ever")
            return Session(self._target, sid)
        else:
            data = json.dumps({'desiredCapabilities': {'bundleId': bundle_id}})
            res = self._request('session', 'POST', data=data)
            return Session(self._target, res.sessionId)

    def screenshot(self, png_filename=None):
        """
        Screenshot with PNG format

        Args:
            - png_filename(string): optional, save file name

        Returns:
            png raw data
        """
        value = self._request('screenshot').value
        raw_value = base64.b64decode(value)
        if png_filename:
            with open(png_filename, 'w') as f:
                f.write(raw_value)
        return raw_value


class Session(object):
    def __init__(self, target, session_id):
        """
        Args:
            - target(string): for example, http://127.0.0.1:8100
            - session_id(string): wda session id
        """
        self._target = target.rstrip('/')
        self._sid = session_id
        # Example session value
        # "capabilities": {
        #     "CFBundleIdentifier": "com.netease.aabbcc",
        #     "browserName": "?????",
        #     "device": "iphone",
        #     "sdkVersion": "10.2"
        # }
        self.capabilities = self._request('/', 'GET').value['capabilities']

    def __str__(self):
        return 'wda.Session (id=%s)' % self._sid

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def _request(self, base_url, method='POST', data=None):
        url = urljoin(self._target, 'session', self._sid, base_url)
        return httpdo(url, method, data)

    @property
    def id(self):
        return self._sid

    @property
    def bundle_id(self):
        return self.capabilities.get('CFBundleIdentifier')

    def deactivate(self, duration):
        """Put app into background and than put it back
        Args:
            - duration(float): deactivate time, seconds
        """
        return self._request('/wda/deactivateApp', data=json.dumps(dict(duration=duration)))

    def tap(self, x, y):
        return self._request('/wda/tap/0', data=json.dumps(dict(x=x, y=y)))

    def double_tap(self, x, y):
        return self._request('/wda/doubleTap', data=json.dumps(dict(x=x, y=y)))

    def tap_hold(self, x, y, duration=1.0):
        """
        Tap and hold for a moment

        Args:
            - x, y(int): position
            - duration(float): seconds of hold time

        [[FBRoute POST:@"/wda/touchAndHold"] respondWithTarget:self action:@selector(handleTouchAndHoldCoordinate:)],
        """
        data = json.dumps({'x': x, 'y': y, 'duration': duration})
        return self._request('/wda/touchAndHold', data=data)

    def swipe(self, x1, y1, x2, y2, duration=0.2):
        """
        Args:
            - duration(float): in the unit of second(NSTimeInterval)

        [[FBRoute POST:@"/wda/dragfromtoforduration"] respondWithTarget:self action:@selector(handleDragCoordinate:)],
        """
        data = dict(fromX=x1, fromY=y1, toX=x2, toY=y2, duration=duration)
        return self._request('/wda/dragfromtoforduration', data=json.dumps(data))

    def dump(self):
        """ Bad """
        return self._request('source', 'GET')

    @property
    def orientation(self):
        """
        Return string
        One of <PORTRAIT | LANDSCAPE>
        """
        return self._request('orientation', 'GET').value

    @orientation.setter
    def orientation(self, value):
        """
        Args:
            - orientation(string): LANDSCAPE | PORTRAIT | UIA_DEVICE_ORIENTATION_LANDSCAPERIGHT |
                    UIA_DEVICE_ORIENTATION_PORTRAIT_UPSIDEDOWN
        """
        data = json.dumps({'orientation': value})
        return self._request('orientation', 'POST', data=data)

    def window_size(self):
        """
        Return namedtuple

        For example:
            Size(width=320, height=568)
        """
        value = self._request('/window/size', 'GET').value
        w = roundint(value['width'])
        h = roundint(value['height'])
        return namedtuple('Size', ['width', 'height'])(w, h)

    def send_keys(self, value):
        """
        send keys, yet I know not, todo function
        """
        if isinstance(value, six.string_types):
            value = list(value)
        return self._request('/wda/keys', data=json.dumps({'value': value}))

    @property
    def alert(self):
        return Alert(self)

    @property
    def keyboard(self):
        return Keyboard(self)

    def close(self):
        return self._request('/', 'DELETE')

    def __call__(self, **kwargs):
        if kwargs.get('className'):
            kwargs['class_name'] = kwargs.get('class_name') or kwargs.pop('className')
        return Selector(urljoin(self._target, '/session', self._sid), **kwargs)


class Alert(object):
    def __init__(self, session):
        self._s = session
        self._request = session._request

    @property
    def exists(self):
        try:
            self.text
        except WDAError as e:
            if e.status != 27:
                raise
            return False
        return True

    @property
    def text(self):
        return self._request('/alert/text', 'GET').value

    def wait(self, timeout=20.0):
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.exists:
                return True
            time.sleep(0.2)
        return False

    def accept(self):
        return self._request('/alert/accept', 'POST')

    def dismiss(self):
        return self._request('/alert/dismiss', 'POST')

    def buttons(self):
        return self._request('/wda/alert/buttons', 'GET').value

    def click(self, button_name):
        """
        Args:
            - button_name: the name of the button
        """
        # Actually, It has no difference POST to accept or dismiss
        return self._request('/alert/accept', 'POST', data={"name": button_name})


class Keyboard(object):
    def __init__(self, session):
        self._s = session
        self._request = session._request

    def dismiss(self):
        return self._request('/wda/keyboard/dismiss', 'POST')


class Selector(object):
    def __init__(self, base_url, sub_eid=None, name=None, text=None, class_name=None, value=None, label=None, xpath=None, index=0, partial=False):
        '''
        Args:
            - name(str): attr for name
            - text(str): alias of name
            - class_name(str): attr of className
            - value(str): attr
            - label(str): attr for label
            - xpath(str): xpath string, a little slow, but works fine
            - index(int): useful when found multi elements
        '''
        self._base_url = base_url
        self._sub_eid = sub_eid

        if text:
            name = text
        self._index = index
        self._name = six.text_type(name) if name else None
        self._value = six.text_type(value) if value else None
        self._label = six.text_type(label) if label else None
        self._xpath = six.text_type(xpath) if xpath else None
        self._class_name = six.text_type(class_name) if class_name else None
        if class_name and not class_name.startswith('XCUIElementType'):
            self._class_name = 'XCUIElementType' + class_name
        if xpath and not xpath.startswith('//XCUIElementType'):
            element = '|'.join(xcui_element_types.xcui_element)
            self._xpath = re.sub(r'/('+element+')', '/XCUIElementType\g<1>', xpath)
        self._partial = True if partial else False
        self._default_timeout = 90.0

        # # set attributes
        # def _element_func(name):
        #     el = self.wait()
        #     return getattr(el, name)
            
        # self.enabled = functools.partial(_element_func, 'enabled')

    def _request(self, data, suburl='elements', method='POST'):
        url = urljoin(self._base_url, suburl)
        if self._sub_eid:
            url = urljoin(self._base_url, 'element', self._sub_eid, suburl)
        return httpdo(url, method, data=data)

    @property
    def elements(self):
        """
        xpath: //XCUIElementTypeButton[@name='Share']
        Return like
        [
            {u'label': u'Dashboard', u'type': u'XCUIElementTypeStaticText', u'ELEMENT': u'E60237CB-5FD8-4D60-A6E4-F54B583931DF'},
            {u'label': None, u'type': u'XCUIElementTypeNavigationBar', u'ELEMENT': u'786F9BB6-7734-4B52-B341-09030256C3A6'},
            {u'label': u'Dashboard', u'type': u'XCUIElementTypeButton', u'ELEMENT': u'504C94B5-742D-4757-B954-096EE3512018'}
        ]

        Raises:
            SyntaxError
        """
        if self._name:
            using = 'partial link text' if self._partial else 'link text'
            value = 'name={name}'.format(name=self._name)
        elif self._value:
            using = 'partial link text' if self._partial else 'link text'
            value = 'value={value}'.format(value=self._value)
        elif self._label:
            using = 'partial link text' if self._partial else 'link text'
            value = 'label={label}'.format(label=self._label)
        elif self._class_name:
            using = 'class name'
            value = self._class_name
        elif self._xpath:
            using = 'xpath'
            value = self._xpath
        else:
            raise SyntaxError("text or className must be set at least one")
        data = json.dumps({'using': using, 'value': value})
        response = self._request(data).value
        elems = []
        for elem in response:
            if self._class_name and elem.get('type') != self._class_name:
                continue
            if self._label and elem.get('label') != self._label:
                continue
            elems.append(elem)
        return elems

    def elems(self):
        """
        Returns:
            Element[]
        """
        els = []
        for el in self.elements:
            els.append(Element(self._base_url, id=el['ELEMENT'], type=el['type'], label=el['label']))
        return els

    def clone(self):
        return copy.deepcopy(self)

    def __getitem__(self, index):
        selector = self.clone()
        selector._index = index
        return selector

    @property
    def exists(self):
        return len(self.elements) > self._index

    def wait(self, timeout=None):
        """
        Args:
            - timeout(float): None means 90s

        Returns:
            element(json) for example:
            Element object
        """
        start_time = time.time()
        if timeout is None or timeout <= 0:
            timeout = self._default_timeout
        while start_time+timeout > time.time():
            elems = self.elems()
            if len(elems) <= self._index:
                continue
            return elems[self._index]
        raise RuntimeError("element not found")

    def timeout(self, duration):
        """
        Set element wait timeout
        """
        self._default_timeout = duration
        return self

    def tap(self, timeout=None):
        element = self.wait(timeout)
        return element.tap()

    def click(self, *args, **kwargs):
        """ Alias of tap """
        return self.tap(*args, **kwargs)

    def tap_hold(self, duration=1.0, timeout=None):
        """
        Tap and hold for a moment

        Args:
            - duration(float): seconds of hold time

        [[FBRoute POST:@"/wda/element/:uuid/touchAndHold"] respondWithTarget:self action:@selector(handleTouchAndHold:)],
        """
        element = self.wait(timeout)
        eid = element['ELEMENT']
        data = json.dumps({'duration': duration})
        return self._request(data, suburl='wda/element/%s/touchAndHold' % eid)

    def double_tap(self, timeout=None):
        """
        [[FBRoute POST:@"/wda/element/:uuid/doubleTap"] respondWithTarget:self action:@selector(handleDoubleTap:)],
        """
        element = self.wait(timeout)
        eid = element['ELEMENT']
        return self._request("", suburl='wda/element/%s/doubleTap' % eid)

    def pinch(self, scale, velocity, timeout=None):
        """
        Args:
            - scale(float): scale must be greater than zero
            - velocity(float): velocity must be less than zero when scale is less than 1
        """
        element = self.wait(timeout)
        eid = element['ELEMENT']
        data = json.dumps({'scale': scale, 'velocity': velocity})
        return self._request(data, suburl='wda/element/%s/pinch' % eid)

    def scroll(self, text=None, text_contains=None, direction=None, timeout=None):
        """
        Scroll to somewhere, if no args provided, scroll to self visible

        Args:
            - text (string): element name equals text
            - text_contains (string): element contains text(donot use it now)
            - direction (string): one of <up|down|left|right>
            - timeout (float): timeout to find start element

        Returns:
            self

        Example:
            s(text="Hello").scroll() # scroll to visible
            s(text="Hello").scroll(text="World")
            s(text="Hello").scroll(text_contains="World")
            s(text="Hello").scroll(direction="right", timeout=5.0)
            s(text="Login").scroll().click()

        The comment in WDA source code looks funny
        // Using presence of arguments as a way to convey control flow seems like a pretty bad idea but it's
        // what ios-driver did and sadly, we must copy them.
        """
        text_contains = None # will raise Coredump of WDA

        element = self.wait(timeout)
        eid = element['ELEMENT']
        if text:
            data = json.dumps({'name': text})
        elif text_contains:
            data = json.dumps({'predicateString': text})
        elif direction:
            data = json.dumps({'direction': direction})
        else:
            data = json.dumps({'toVisible': True})
        self._request(data, suburl='wda/element/{elem_id}/scroll'.format(elem_id=eid))
        return self

    def swipe(self, direction, timeout=None):
        if direction not in ['up', 'down', 'left', 'right']:
            raise ValueError
        element = self.wait(timeout)
        eid = element['ELEMENT']
        data = json.dumps({'direction': direction})
        return self._request(data, suburl='wda/element/%s/swipe' % eid)

    # todo
    # pinch
    # touchAndHold
    # dragfromtoforduration
    # twoFingerTap

    def set_text(self, text, clear=False):
        el = self.wait()
        if clear:
            el.clear_text()
        return el.set_text(text)

    def clear_text(self):
        return self.wait().clear_text()

    def attribute(self, name):
        return self.wait().attribute(name)

    @property
    def value(self):
        return self.wait().attribute('value')

    @property
    def enabled(self):
        """ true or false """
        return self.wait().enabled

    @property
    def accessible(self):
        return self.wait().enabled

    # todo
    # handleGetIsAccessibilityContainer
    # [[FBRoute GET:@"/wda/element/:uuid/accessibilityContainer"] respondWithTarget:self action:@selector(handleGetIsAccessibilityContainer:)],

    @property
    def displayed(self):
        return self.wait().displayed

    @property
    def bounds(self):
        """
        Return example:
            Rect(x=144, y=28, width=88, height=27)
        """
        return self.wait().bounds

    @property
    def count(self):
        return len(self.elements)

    @property
    def class_name(self):
        return self.wait().class_name

    @property
    def text(self):
        return self.wait().text

    @property
    def name(self):
        return self.text

    def __len__(self):
        return self.count


class Element(object):
    def __init__(self, base_url, id, type, label):
        """
        base_url eg: http://localhost:8100/session/$SESSION_ID
        """
        self.__base_url = base_url
        self.__attrs = {}

        self._id = id
        self._type = type
        self._label = label
        self.__props = {'ELEMENT': id, 'type': type, 'label': label}

    def __repr__(self):
        return '<wda.Element(id="{}", class="{}", label={})>'.format(self.id, self._type, repr(self.label))

    def __getitem__(self, key):
        return self.__props[key]

    def _request(self, method, suburl, data=None):
        return httpdo(urljoin(self.__base_url, suburl), method, data=data)

    def _prop(self, key, cache=True):
        if cache and self.__attrs.get(key):
            return self.__attrs[key]
        ret = self._request('GET', 'element/%s/%s' %(self._id, key)).value
        if ret and cache:
            self.__attrs[key] = ret
        return ret

    def _wda_prop(self, key):
        ret = self._request('GET', 'wda/element/%s/%s' %(self._id, key)).value
        return ret

    @property
    def id(self):
        return self._id

    @property
    def label(self):
        return self._label

    @property
    def class_name(self):
        return self._type

    @property
    def text(self):
        return self._prop('text')

    @property
    def displayed(self):
        return self._prop("displayed", cache=False)

    @property
    def name(self):
        return self.text

    @property
    def accessible(self):
        return self._wda_prop("accessible")

    @property
    def value(self):
        return self.attribute('value')

    @property
    def enabled(self):
        return self._prop('enabled', cache=False)

    @property
    def bounds(self):
        value = self._prop('rect')
        x, y = value['x'], value['y']
        w, h = value['width'], value['height']
        return Rect(x, y, w, h)

    # operations
    def tap(self):
        self._request('POST', 'element/%s/%s' %(self._id, 'click'))

    def set_text(self, value):
        # Test result:
        # {"value": list(value)} or {"value": value} works
        self._request('POST', 'element/%s/%s' %(self._id, 'value'), {'value': value})

    def clear_text(self):
        self._request('POST', 'element/%s/%s' %(self._id, 'clear'))

    def attribute(self, name):
        """
        get element attribute
        //POST element/:uuid/attribute/:name
        """
        return self._prop('attribute/%s' % name)

    def child(self, **kwargs):
        return Selector(self.__base_url, self._id, **kwargs)
        
    # todo lot of other operations
    # tap_hold

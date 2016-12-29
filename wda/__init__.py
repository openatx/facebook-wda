#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import urlparse
import base64
import copy
import time
import re
from collections import namedtuple

import requests
import xcui_element_types

DEBUG = False


def convert(dictionary):
    """
    Convert dict to namedtuple
    """
    return namedtuple('GenericDict', dictionary.keys())(**dictionary)


def urljoin(*urls):
    """
    The default urlparse.urljoin behavior look strange
    Standard urlparse.urljoin('http://a.com/foo', '/bar')
    Expect: http://a.com/foo/bar
    Actually: http://a.com/bar

    This function fix that.
    """
    return reduce(urlparse.urljoin, [u.strip('/')+'/' for u in urls if u.strip('/')], '').rstrip('/')

def roundint(i):
    return int(round(i, 0))


def httpdo(url, method='GET', data=None):
    """
    Do HTTP Request
    """
    if isinstance(data, dict):
        data = json.dumps(data)
    if DEBUG:
        print "Shell: curl -X {method} -d '{data}' '{url}'".format(method=method, data=data or '', url=url)

    fn = dict(GET=requests.get, POST=requests.post, DELETE=requests.delete)[method]
    response = fn(url, data=data)
    retjson = response.json()
    if DEBUG:
        print 'Return:', json.dumps(retjson, indent=4)
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
        """ Press home button """
        return self._request('homescreen', 'POST')

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

    def source(self):
        # TODO: not tested
        return self._request('source', 'GET').value


class Session(object):
    def __init__(self, target, session_id):
        """
        Args:
            - target(string): for example, http://127.0.0.1:8100
            - session_id(string): wda session id
        """
        self._target = target.rstrip('/')
        self._sid = session_id

    def __str__(self):
        return 'wda.Session (id=%s)' % self._sid

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def _request(self, base_url, method='POST', data=None):
        url = urljoin(self._target, 'session', self._sid, base_url)
        return httpdo(url, method, data)

    def tap(self, x, y):
        return self._request('/tap/0', data=json.dumps(dict(x=x, y=y)))

    def swipe(self, x1, y1, x2, y2, duration=0.2):
        """
        duration(float) not sure the unit, need to test so that you can known

        [[FBRoute POST:@"/uiaTarget/:uuid/dragfromtoforduration"] respondWithTarget:self action:@selector(handleDrag:)],
        """
        data = dict(fromX=x1, fromY=y1, toX=x2, toY=y2, duration=duration)
        return self._request('/uiaTarget/0/dragfromtoforduration', data=json.dumps(data))

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

    def window_size(self):
        """
        Return namedtuple

        For example:
            Size(width=320, height=568)
        """
        value = self._request('/window/0/size', 'GET').value
        w = roundint(value['width'])
        h = roundint(value['height'])
        return namedtuple('Size', ['width', 'height'])(w, h)

    def send_keys(self, value):
        """
        send keys, yet I know not, todo function
        """
        if isinstance(value, basestring):
            value = list(value)
        return self._request('/keys', data=json.dumps({'value': value}))

    @property
    def alert(self):
        return Alert(self)

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
    def text(self):
        return self._request('/alert/text', 'GET').value

    def accept(self):
        return self._request('/alert/accept', 'POST')

    def dismiss(self):
        return self._request('/alert/dismiss', 'POST')
    

class Selector(object):
    def __init__(self, base_url, name=None, text=None, class_name=None, value=None, label=None, xpath=None, index=0):
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
        if text:
            name = text
        self._name = unicode(name) if name else None
        self._value = unicode(value) if value else None
        self._label = unicode(label) if label else None
        self._class_name = unicode(class_name) if class_name else None
        self._xpath = unicode(xpath) if xpath else None
        self._index = index
        if class_name and not class_name.startswith('XCUIElementType'):
            self._class_name = 'XCUIElementType' + class_name.title()
        if xpath and not xpath.startswith('//XCUIElementType'):
            element = '|'.join(xcui_element_types.xcui_element)
            self._xpath = re.sub(r'/('+element+')', '/XCUIElementType\g<1>', xpath)

    def _request(self, data, suburl='elements', method='POST'):
        return httpdo(urljoin(self._base_url, suburl), method, data=data)

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
            using = 'link text'
            value = u'name={name}'.format(name=self._name)
        elif self._value:
            using = 'link text'
            value = u'value={value}'.format(value=self._value)
        elif self._label:
            using = 'link text'
            value = u'label={label}'.format(label=self._label)
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

    def clone(self):
        return copy.deepcopy(self)

    def __getitem__(self, index):
        count = self.count
        if index >= count:
            raise IndexError()
        elif count == 1:
            return self
        else:
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
            {"label": "Dashboard"," "type": "XCUIElementTypeStaticText"," "ELEMENT": "E60237CB-5FD8-4D60-A6E4-F54B583931DF'}
        """
        start_time = time.time()
        if timeout is None or timeout <= 0:
            timeout = 90.0
        while start_time+timeout > time.time():
            elems = self.elements
            if len(elems) <= self._index:
                continue
            return elems[self._index]
        raise RuntimeError("element not found")

    def tap(self, timeout=None):
        element = self.wait(timeout)
        eid = element['ELEMENT']
        return self._request("", suburl='element/%s/click' % eid)

    def click(self, *args, **kwargs):
        """ Alias of tap """
        return self.tap(*args, **kwargs)
    
    def tap_hold(self, duration=1.0, timeout=None):
        """
        Tap and hold for a moment

        Args:
            - duration(float): seconds of hold time

        [[FBRoute POST:@"/uiaElement/:uuid/touchAndHold"] respondWithTarget:self action:@selector(handleTouchAndHold:)],
        """
        element = self.wait(timeout)
        eid = element['ELEMENT']
        data = json.dumps({'duration': duration})
        return self._request(data, suburl='uiaElement/%s/touchAndHold' % eid)

    def double_tap(self, x, y):
        """
        [[FBRoute POST:@"/uiaElement/:uuid/doubleTap"] respondWithTarget:self action:@selector(handleDoubleTap:)],
        """
        raise NotImplementedError()

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
        self._request(data, suburl='uiaElement/{elem_id}/scroll'.format(elem_id=eid))
        return self

    def _property(self, name, data='', method='GET', timeout=None, eid=None):
        if not eid:
            eid = self.wait(timeout)['ELEMENT']
        if isinstance(data, dict):
            data = json.dumps(data)
        return self._request(data, suburl='element/%s/%s' % (eid, name), method=method).value

    def set_text(self, text, clear=False):
        if clear:
            self.clear_text()
        return self._property('value', data=json.dumps({'value': list(text)}), method='POST')

    def clear_text(self):
        return self._property('clear', method='POST')

    def attribute(self, name):
        """
        get element attribute
        //POST element/:uuid/attribute/:name
        """
        return self._property('attribute/%s' % name)

    @property
    def value(self):
        """true or false"""
        return self.attribute('value')

    @property
    def enabled(self):
        """ true or false """
        return self._property('enabled')

    @property
    def accessible(self):
        """ true or false """
        return self._property('accessible')

    @property
    def displayed(self):
        """ true or false """
        return self._property('displayed')

    @property
    def bounds(self):
        """
        Return example:
            Rect(x=144, y=28, width=88, height=27)
        """
        value = self._property('rect')
        x, y = value['x'], value['y']
        w, h = value['width'], value['height']
        return Rect(x, y, w, h)

    @property
    def count(self):
        return len(self.elements)

    @property
    def class_name(self):
        return self._property('name')

    @property
    def text(self):
        return self._property('text')

    def __len__(self):
        return self.count

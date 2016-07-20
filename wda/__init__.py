#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import urlparse
import base64
import copy
import time

import requests


def urljoin(*urls):
    """
    The default urlparse.urljoin behavior look strange
    Standard urlparse.urljoin('http://a.com/foo', '/bar')
    Expect: http://a.com/foo/bar
    Actually: http://a.com/bar

    This function fix that.
    """
    return reduce(urlparse.urljoin, [u.strip('/')+'/' for u in urls if u.strip('/')], '').rstrip('/')


class Selector(object):
    def __init__(self, base_url, text=None, label=None, class_name=None, index=0):
        self._base_url = base_url
        self._text = unicode(text) if text else None
        self._class_name = unicode(class_name) if class_name else None
        self._index = index
        if class_name and not class_name.startswith('XCUIElementType'):
            self._class_name = 'XCUIElementType' + class_name.title()

    def _request(self, data, suburl='elements', method='POST'):
        func = dict(GET=requests.get, POST=requests.post, DELETE=requests.delete)[method]
        res = func(urljoin(self._base_url, suburl), data=data)
        return res.json()

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
        if self._text:
            using = 'link text'
            value = u'name={name}'.format(name=self._text)
        elif self._class_name:
            using = 'class name'
            value = self._class_name
        else:
            raise SyntaxError("text or className must be set at least one")

        data = json.dumps({'using': using, 'value': value})
        response = self._request(data)['value']
        # print response
        elems = []
        for elem in response: 
            if self._class_name and elem.get('type') != self._class_name:
                continue
            if self._text and elem.get('label') != self._text:
                continue
            eid = elem.get('ELEMENT')
            if not self._property('displayed', eid=eid): # Since you can't see it, it is better to ignore it.
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
            - timeout(float): None means infinient

        Returns:
            element(json) for example:
            {"label": "Dashboard"," "type": "XCUIElementTypeStaticText"," "ELEMENT": "E60237CB-5FD8-4D60-A6E4-F54B583931DF'}
        """
        start_time = time.time()
        while timeout is None or start_time+timeout > time.time():
            elems = self.elements
            if len(elems) <= self._index:
                continue
            return elems[self._index]
        raise RuntimeError("element not found")

    def tap(self, timeout=None):
        element = self.wait(timeout)
        eid = element['ELEMENT']
        return self._request("", suburl='element/%s/click' % eid)

    def double_tap(self, x, y):
        """
        [[FBRoute POST:@"/uiaElement/:uuid/doubleTap"] respondWithTarget:self action:@selector(handleDoubleTap:)],
        """
        raise NotImplementedError()

    def scroll(self):
        """
        The comment in WDA source code looks funny

        // Using presence of arguments as a way to convey control flow seems like a pretty bad idea but it's
        // what ios-driver did and sadly, we must copy them.
        """
        raise NotImplementedError()

    def touch_hold(self, x, y, duration):
        """
        [[FBRoute POST:@"/uiaElement/:uuid/touchAndHold"] respondWithTarget:self action:@selector(handleTouchAndHold:)],
        """
        raise NotImplementedError()

    def _property(self, name, data='', method='GET', timeout=None, eid=None):
        eid = eid or self.wait(timeout)['ELEMENT']
        return self._request(data, suburl='element/%s/%s' % (eid, name), method=method)['value']

    def set_text(self, text):
        return self._property('value', data=json.dumps({'value': list(text)}), method='POST')

    def clear_text(self):
        return self._property('clear', method='POST')

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
    def rect(self):
        """
        Include location and size

        Return example:
        {u'origin': {u'y': 0, u'x': 0}, u'size': {u'width': 85, u'height': 20}}
        """
        return self._property('rect')
    
    # @property
    # def location(self):
    #     """
    #     Return like
    #     {"x": 2, "y": 200}
    #     """
    #     return self._property('location')
    
    # @property
    # def size(self):
    #     """
    #     Return like
    #     {"width": 2, "height": 200}
    #     """
    #     return self._property('size')

    def click(self, *args, **kwargs):
        """ Alias of tap """
        return self.tap(*args, **kwargs)

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


class Session(object):
    def __init__(self, target, session_id):
        self._target = target.rstrip('/')
        self._sid = session_id

    def __str__(self):
        return 'wda.Session (id=%s)' % self._sid

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def _request(self, base_url, method='POST', data=None):
        func = dict(GET=requests.get, POST=requests.post, DELETE=requests.delete)[method]
        url = urljoin(self._target, 'session', self._sid, base_url)
        # print base_url, url
        res = func(url, data=data)
        return res.json()

    def tap(self, x, y):
        return self._request('/tap/0', data=json.dumps(dict(x=x, y=y)))

    def swipe(self, x1, y1, x2, y2, duration=0.5):
        """
        duration(float) not sure the unit, need to test so that you can known

        [[FBRoute POST:@"/uiaTarget/:uuid/dragfromtoforduration"] respondWithTarget:self action:@selector(handleDrag:)],
        """
        raise NotImplementedError()
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
        return self._request('orientation', 'GET')['value']

    # def set_text(self, text):
    #     return self._request('/element/0/value', data=json.dumps(dict(value=list(text))))

    def window_size(self):
        """
        Return dict:
        For example:

        {"width": 400, "height": 200}
        """
        return self._request('/window/0/size', 'GET')['value']

    def close(self):
        return self._request('/', 'DELETE')

    def __call__(self, **kwargs):
        if kwargs.get('className'):
            kwargs['class_name'] = kwargs.get('class_name') or kwargs.pop('className')
        return Selector(urljoin(self._target, '/session', self._sid), **kwargs)


class Client(object):
    def __init__(self, target='http://127.0.0.1:8100'):
        """
        Args:
            - target(string): base URL of your iPhone, ex http://10.0.0.1:8100
        """
        self._target = target

    def _request(self, base_url, method='GET', data=None):
        func = dict(GET=requests.get, POST=requests.post)[method]
        res = func(urljoin(self._target, base_url), data=data)
        return res.json()

    def status(self):
        return self._request('status')['value']

    def home(self):
        """ Press home button """
        return self._request('homescreen', 'POST')

    def session(self, bundle_id):
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
        data = json.dumps({'desiredCapabilities': {'bundleId': bundle_id}})
        res = self._request('session', 'POST', data=data)
        session_id = res.get('sessionId')
        if session_id is None:
            raise RuntimeError("WDA session start failed.")
        return Session(self._target, session_id)

    def screenshot(self, png_filename=None):
        """
        Screenshot with PNG format
        
        Args:
            - png_filename(string): optional, save file name

        Returns:
            png raw data
        """
        value = self._request('screenshot')['value']
        raw_value = base64.b64decode(value)
        if png_filename:
            with open(png_filename, 'w') as f:
                f.write(raw_value)
        return raw_value

    def source(self):
        # TODO: not tested
        return self._request('source', 'POST')['value']

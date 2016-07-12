#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import urlparse
import base64
import copy

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
        self._text = text
        self._class_name = class_name
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
        """
        value = "name={name}".format(name=self._text)
        # value = "[@name='{name}']".format(name=self._text)
        # data = json.dumps(dict(using='xpath', value=value))
        print self._base_url
        data = json.dumps(dict(using='link text', value=value))
        print data
        # TODO(ssx): filter by class name
        return self._request(data)['value']

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
        return len(self.elements) > 0
    
    def set_text(self, text):
        pass

    def clear_text(self):
        pass

    def tap(self):
        """ TODO: shit, not working at all """
        eid = self.elements[0]['ELEMENT']
        return self._request("", suburl='element/%s/click' % eid)

    def click(self):
        return self.tap()

    @property
    def count(self):
        return len(self.elements)

    def __len__(self):
        return self.count


class Session(object):
    def __init__(self, target, session_id):
        self._target = target.rstrip('/')
        self._sid = session_id

    def __str__(self):
        return 'wda.Session (id=%s)' % self._sid

    def _request(self, base_url, method='POST', data=None):
        func = dict(GET=requests.get, POST=requests.post, DELETE=requests.delete)[method]
        url = urljoin(self._target, 'session', self._sid, base_url)
        print base_url, url
        res = func(url, data=data)
        return res.json()

    def tap(self, x, y):
        return self._request('/tap/0', data=json.dumps(dict(x=x, y=y)))
        
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
            kwargs['class_name'] = kwargs.get('class_name') or kwargs.get('className')
        return Selector(urljoin(self._target, '/session', self._sid), **kwargs)


class Client(object):
    def __init__(self, target):
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

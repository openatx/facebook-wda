#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import requests
import urlparse


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
    __alias = dict(Button='XCUIElementTypeButton')

    def __init__(self, base_url, text=None, label=None, class_name=None):
        self._base_url = base_url
        self._text = text
        self._class_name = class_name

    def _request(self, data, method='POST'):
        func = dict(GET=requests.get, POST=requests.post, DELETE=requests.delete)[method]
        res = func(self._base_url, data=data)
        return res.json()

    @property
    def elements(self):
        """
        xpath: //XCUIElementTypeButton[@name='Share']
        """
        value = "name={name}".format(name=self._text)
        # value = "[@name='{name}']".format(name=self._text)
        # data = json.dumps(dict(using='xpath', value=value))
        print self._base_url
        data = json.dumps(dict(using='link text', value=value))
        print data
        # TODO(ssx): filter by class name
        return self._request(data)['value']

    @property
    def exists(self):
        return len(self.elements) > 0
    

    def set_text(self, text):
        pass

    def clear_text(self):
        pass

    def tap(self):
        pass

    def click(self):
        return self.tap()

    @property
    def exists(self):
        pass

    @property
    def count(self):
        pass

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
        One of <PORTRAIT | >
        """
        return self._request('orientation', 'GET')['value']


    # def long_tap(self, x, y):
    #     pass

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
        return Selector(urljoin(self._target, '/session', self._sid, 'elements'), **kwargs)


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
        return self._request('status')

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

#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import requests
from urlparse import urljoin


class _ElementObject(object):
    def __init__(self, elem_id):
        self._id = elem_id

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
        self._target = target
        self._sid = session_id

    def __str__(self):
        return 'wda.Session (id=%s)' % self._sid

    def tap(self, x, y):
        pass

    def long_tap(self, x, y):
        pass

    def rect(self):
        pass

    def close(self):
        pass

    def __call__(self, text=None, class_name=None):
        pass


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

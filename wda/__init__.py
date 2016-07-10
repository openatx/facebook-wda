#!/usr/bin/env python
# -*- coding: utf-8 -*-


import requests
from urlparse import urljoin


class Client(object):
    def __init__(self, target):
        """
        Args:
            - target(string): base URL of your iPhone, ex http://10.0.0.1:8100
        """
        self._target = target

    def status(self):
        url = urljoin(self._target, 'status')
        res = requests.get(url)
        return res.json()



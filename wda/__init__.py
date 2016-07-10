#!/usr/bin/env python
# -*- coding: utf-8 -*-


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

	def tap(self, x, y):
		pass

	def long_tap(self, x, y):
		pass

	def rect(self):
		pass

	def close(self):
		pass

	def __call__(self, text=None, class_name=None, className=None):
		pass


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

    def session(self, bundle_id):
    	pass




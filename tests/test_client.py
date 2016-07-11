#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time

import wda

__target = os.getenv("DEVICE_TARGET") or 'http://localhost:8100'

def test_status():
    c = wda.Client(__target)
    print c.status()


def test_session():
    c = wda.Client(__target)
    sess = c.session('com.apple.Health')
    print sess
    time.sleep(2.0)
    sess.tap(200, 200)
    time.sleep(5.0)
    sess.close()


if __name__ == '__main__':
    test_status()
    test_session()

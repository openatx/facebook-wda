#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time

import wda

__target = os.getenv("DEVICE_TARGET") or 'http://localhost:8100'

def test_status():
    c = wda.Client(__target)
    print c.status()
    c.screenshot()


def test_session():
    c = wda.Client(__target)
    sess = c.session('com.apple.Health')
    print sess
    time.sleep(2.0)
    sess.tap(200, 200)
    time.sleep(5.0)
    print sess.window_size()
    sess.close()

def test_set_text():
    c = wda.Client(__target)
    with c.session('com.apple.Health') as s:
        print 'switch to element'
        time.sleep(3)
        print s.orientation
        print s(text='Month').elements
        print s(text='Dashboard').elements
        # s.set_text("Hello world")
        time.sleep(3)


if __name__ == '__main__':
    test_status()
    test_set_text()
    # test_session()

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
        # print s(text='Month').elements
        print s(text='Dashboard', class_name='Button').elements
        # s.set_text("Hello world")
        time.sleep(3)

def test_scroll():
    c = wda.Client(__target)
    with c.session('com.apple.Preferences') as s:
        s(class_name='Table').scroll('Developer')
        s(text='Developer').tap()
        time.sleep(3)

def test_alert():
    c = wda.Client(__target)
    with c.session('com.apple.Health') as s:
        #print s.alert.text
        pass
        

def test_rect():
    r = wda.Rect(10, 20, 10, 30) # x=10, y=20, w=10, h=30
    assert r.left == 10
    assert r.right == 20
    assert r.bottom == 50
    assert r.top == 20
    assert r.x == 10 and r.y == 20 and r.width == 10 and r.height == 30
    assert r.center.x == 15 and r.center.y == 35
    assert r.origin.x == 10 and r.origin.y == 20

if __name__ == '__main__':
    test_status()
    test_set_text()
    test_scroll()
    # test_session()

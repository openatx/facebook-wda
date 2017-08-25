#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import time
import xml.etree.ElementTree as ET

import wda

# Note !!!
# Set env-var DEVICE_URL before run tests
# run test with
# $ py.test

wda.DEBUG = True
__target = os.getenv("DEVICE_TARGET") or 'http://localhost:8100'
c = wda.Client()

def setup_function():
    """ initial test environment """
    wda.DEBUG = True
    c.healthcheck()


def test_client_status():
    """ Example response
    {
        "state": "success",
        "os": {
            "version": "10.3.3",
            "name": "iOS"
        },
        "ios": {
            "ip": "192.168.2.85",
            "simulatorVersion": "10.3.3"
        },
        "build": {
            "time": "Aug  8 2017 17:06:05"
        },
        "sessionId": "xx...x.x.x.x.x.x" # added by python code
    }
    """
    st = c.status() # json value
    assert st['state'] == 'success'
    assert 'sessionId' in st


def test_client_session_without_argument():
    s = c.session('com.apple.Health')
    session_id = c.status()['sessionId']
    assert s.id == session_id
    assert s.bundle_id == 'com.apple.Health'
    s.close()


def test_client_session_with_argument():
    """
    In mose case, used to open browser with url
    """
    with c.session('com.apple.mobilesafari', ['-u', 'https://www.google.com/ncr']) as s:
        time.sleep(2.0)
        assert s(name='ReloadButton').exists


def test_client_home():
    """ error will raise if status is not 0 when call home """
    c.home()

def test_client_screenshot():
    wda.DEBUG = False
    c.screenshot()


def test_client_source():
    wda.DEBUG = False
    xml_data = c.source()
    root = ET.fromstring(xml_data.encode('utf-8'))
    assert root.tag == 'XCUIElementTypeApplication'

    json_data = c.source(format='json')
    assert json_data['type'] == 'Application'

    json_data = c.source(accessible=True)
    assert json_data['type'] == 'Application'


def test_alert():
    """
    Skip: because alert not always happens
    """
    return
    # c = wda.Client(__target)
    # with c.session('com.apple.Health') as s:
    #     #print s.alert.text
    #     pass

def test_partial():
    c = wda.Client()
    with c.session('com.apple.Preferences') as s:
        assert s(text="WLA", partial=True).exists
        assert not s(text="WLA").exists
        assert s(text="WLAN").exists


def test_alert_wait():
    pass
    """ Skip because alert not always happens """
    # c = wda.Client(__target)
    # with c.session('com.apple.Preferences') as s:
    #     # start_time = time.time()
    #     assert s.alert.wait(20)
    #     # print time.time() - start_time


# def test_scroll():
#     c = wda.Client()
#     with c.session('com.apple.Preferences') as s:
#         s(class_name='Table').scroll('Developer')
#         s(text='Developer').tap()
#         time.sleep(3)
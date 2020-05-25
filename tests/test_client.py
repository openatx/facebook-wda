#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import time
import pytest
import xml.etree.ElementTree as ET

import wda
from pytest import mark


@pytest.fixture(scope="function")
def client(c):
    c.home()
    return c

def test_client_status(client: wda.Client):
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
    st = client.status() # json value
    assert st['state'] == 'success'
    # assert 'sessionId' in st


def test_client_session_without_argument(client: wda.Client):
    s = client.session('com.apple.Health')
    session_id = client.status()['sessionId']
    assert s.id == session_id
    assert s.bundle_id == 'com.apple.Health'
    s.close()


@mark.skip("iOS not supported")
def test_client_session_with_argument(client: wda.Client):
    """
    In mose case, used to open browser with url
    """
    with client.session('com.apple.mobilesafari', ['-u', 'https://www.github.com']) as s:
        # time.sleep(1.0)
        # s(id='URL').wait()
        assert s(name='Share', className="Button").wait()


def test_client_screenshot(client: wda.Client):
    wda.DEBUG = False
    client.screenshot()


@mark.skip("unstable api")
def test_client_source():
    wda.DEBUG = False
    xml_data = c.source()
    root = ET.fromstring(xml_data.encode('utf-8'))
    assert root.tag == 'XCUIElementTypeApplication'

    json_data = c.source(format='json')
    assert json_data['type'] == 'Application'

    json_data = c.source(accessible=True)
    assert json_data['type'] == 'Application'


@mark.skip("hard to test")
def test_alert():
    """
    Skip: because alert not always happens
    """
    return
    # c = wda.Client(__target)
    # with c.session('com.apple.Health') as s:
    #     #print s.alert.text
    #     pass

@mark.skip("hard to test")
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

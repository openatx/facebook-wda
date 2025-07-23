# coding: utf-8
#

import wda
import pytest
import os


@pytest.fixture
def c():
    if os.getenv("DEVICE_URL"):
        return wda.Client(os.getenv("DEVICE_URL"))
    return wda.USBClient()

    #wda.DEBUG = True
    #__target = os.getenv("DEVICE_URL") or 'http://localhost:8100'


@pytest.fixture(scope="function")
def app(c) -> wda.Client:
    return c.session('com.apple.Preferences')

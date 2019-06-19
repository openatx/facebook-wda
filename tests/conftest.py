# coding: utf-8
#

import wda
import pytest
import os


@pytest.fixture
def c():
    print("HI")
    wda.DEBUG = True
    __target = os.getenv("DEVICE_URL") or 'http://localhost:8100'
    return wda.Client(__target)

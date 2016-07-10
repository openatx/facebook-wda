#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import wda

__target = os.getenv("DEVICE_TARGET") or 'http://localhost:8100'

def test_status():
    c = wda.Client(__target)
    print c.status()


def test_session():
    c = wda.Client(__target)
    sess = c.session('com.supercell.magic')
    print sess


if __name__ == '__main__':
    test_status()
    test_session()

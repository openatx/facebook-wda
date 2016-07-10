#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import wda

__target = os.getenv("DEVICE_TARGET") or 'http://localhost:8100'

def test_status():
    c = wda.Client(__target)
    print c.status()


if __name__ == '__main__':
    test_status()

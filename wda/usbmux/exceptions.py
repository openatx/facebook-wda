#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Created on Tue Mar 05 2024 10:18:09 by codeskyblue

Copy from https://github.com/doronz88/pymobiledevice3
"""

class NotPairedError(Exception):
    pass


class MuxError(Exception):
    pass


class MuxVersionError(MuxError):
    pass


class BadCommandError(MuxError):
    pass


class BadDevError(MuxError):
    pass


class MuxConnectError(MuxError):
    pass


class MuxConnectToUsbmuxdError(MuxConnectError):
    pass


class ArgumentError(Exception):
    pass


class HTTPError(Exception):
    pass
    
# coding: utf-8
#
# 网易云音乐测试示例
#

import os
import time
import wda
import pytest
from pytest import mark


bundle_id = 'com.netease.cloudmusic'

c = wda.Client()
s = None

USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')

def account_logout(s):
    s(nameMatches=u'帐[ ]*号', type='Button').tap() # not support \s, wired
    s(name=u'退出登录').scroll().tap()
    s.alert.click(u'确定')

def account_netease_login(s):
    """ 完成网易邮箱登录 """
    if s(name=u'发现音乐', type='Button').wait(3, raise_error=False):
        # Already logged in
        return

    s(name=u'网易邮箱').tap()
    s(type='TextField').set_text(USERNAME+'\n')
    s(type='SecureTextField').set_text(PASSWORD+'\n')
    s(name=u'开启云音乐').click_exists(timeout=3.0)
    assert s(name=u'发现音乐', type='Button').wait(5.0)


def alert_callback(session):
    btns = set([u'不再提醒', 'OK', u'知道了', 'Allow']).intersection(session.alert.buttons())
    if len(btns) == 0:
        raise RuntimeError("Alert can not handled, buttons: " + ', '.join(session.alert.buttons()))
    session.alert.click(list(btns)[0])

def create_session():
    s = c.session(bundle_id)
    s.set_alert_callback(alert_callback)
    return s

def setup_function():
    global s
    s = create_session()
    account_netease_login(s)

def teardown_function():
    s.close()
    # s = create_session()
    # account_logout(s)
    # s.close()


def test_discover_music():
    """
    测试 发现音乐->私人FM 中的播放功能
    """
    s(name=u'发现音乐', type='Button').tap()
    time.sleep(.5)
    assert s(name=u'听歌识曲', visible=True).wait()
    s(name=u'私人FM').tap()
    assert s(name=u'不再播放').exists
    assert s(name=u'添加到我喜欢的音乐').exists
    assert s(name=u'00:00', className='StaticText').exists
    s(nameMatches=u'(暂停|播放)').tap()
    assert s(name=u'00:00', className='StaticText').wait_gone(10.0)
    s(name=u'跑步FM').tap()
    s(name=u'知道了').click_exists(2.0)


def test_my_music():
    """
    测试 我的音乐->本地音乐
    """
    s(name=u'我的音乐', type='Button').tap()
    assert s(name=u'最近播放').wait(2.0)
    s(name=u'本地音乐').tap()
    assert s(name=u'管理').wait()
    s(name=u'播放全部').tap()
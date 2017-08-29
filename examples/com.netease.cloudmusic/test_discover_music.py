# coding: utf-8
#

import time
import wda
import pytest
from pytest import mark


bundle_id = 'com.netease.cloudmusic'

c = wda.Client()
s = None

def alert_callback(session):
    btns = set([u'不再提醒', 'OK']).intersection(session.alert.buttons())
    if len(btns) == 0:
        raise RuntimeError("Alert can not handled, buttons: " + ', '.join(session.alert.buttons()))
    session.alert.click(list(btns)[0])

def setup_function():
    global s
    s = c.session(bundle_id)
    s.set_alert_callback(alert_callback)


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
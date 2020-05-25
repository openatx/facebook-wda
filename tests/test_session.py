# coding: utf-8

import pytest
from pytest import mark
import time
import wda



@mark.skip("no test enviroment")
def test_session_open_url():
    """ TODO: do not know how to use this api """
    pass


@mark.skip("wda bug")
def test_session_deactivate():
    with c.session('com.apple.mobilesafari') as s:
        s.deactivate(3.0)
        assert s(name='Share').wait(2.0, raise_error=False)

@mark.skip("TODO")
def test_session_just_tap():
    s = c.session()
    x, y = s(name='Settings').bounds.center
    s.tap(x, y)
    assert s(name='Bluetooth').wait(2.0, raise_error=False)
    c.home()

@mark.skip("TODO")
def test_session_double_tap():
    s = c.session()
    x, y = s(name='Settings').bounds.center
    s.double_tap(x, y)

@mark.skip("TODO")
def test_session_tap_hold():
    s = c.session()
    x, y = s(name='Settings').bounds.center
    s.tap_hold(x, y, 2.0)
    s(name="DeleteButton").wait(2.0, raise_error=False)
    c.home()

@mark.skip("TODO")
def test_session_swipe():
    s = c.session()
    s.swipe_left()
    assert not s(name="Settings").displayed
    s.swipe_right()
    assert s(name="Settings").displayed
    s.swipe_up()
    assert s(name="Airplane Mode").wait(2.0, raise_error=False)
    s.swipe_down()
    assert s(name="Airplane Mode").wait_gone(2.0, raise_error=False)

@mark.skip("wda bug")
def test_session_set_text():
    with c.session('com.apple.mobilesafari') as s:
        s(name='URL', className='Button').set_text("status.github.com")
        url = s(name='URL', className='TextField').get()
        assert url.value == 'status.github.com'

@mark.skip("TODO")
def test_session_window_size():
    s = c.session()
    wsize = s.window_size()
    assert wsize.width == 320
    assert wsize.height == 568

@mark.skip("wda bug")
def test_session_send_keys():
    with c.session('com.apple.mobilesafari') as s:
        u = s(label='Address', className='Button')
        u.clear_text()
        s.send_keys('www.github.com')
        assert 'www.github.com' == s(label='Address', className='TextField').get().value


@mark.skip("wait for WDA fix")
def test_session_keyboard_dismiss():
    with c.session('com.apple.mobilesafari') as s:
        u = s(label='Address', className='Button')
        u.clear_text()
        s.send_keys('www.github.com')

        assert s(className='Keyboard').exists
        s.keyboard_dismiss()
        assert not s(className='Keyboard').exists


def test_session_orientation(c: wda.Client):
    with c.session('com.apple.mobilesafari') as s:
        assert s.orientation == wda.PORTRAIT
        s.orientation = wda.LANDSCAPE
        time.sleep(1.0)
        assert s.orientation == wda.LANDSCAPE
        # recover orientation
        s.orientation = wda.PORTRAIT

@mark.skip("TODO")
def test_session_wait_gone():
    s = c.session()
    elem = s(name="Settings", visible=True)
    with pytest.raises(wda.WDAElementNotDisappearError) as e_info:
        elem.wait_gone(1.0)
    assert not elem.wait_gone(1.0, raise_error=False)
    s.swipe_left()
    assert elem.wait_gone(1.0)

@mark.skip("Require English")
def test_text_contains_matches(c: wda.Client):
    with c.session('com.apple.Preferences') as s:
        s(text='Bluetooth').get()
        assert s(textContains="Blue").exists
        assert not s(text="Blue").exists
        assert s(text="Bluetooth").exists
        assert s(textMatches="Blue?").exists
        assert s(nameMatches="Blue?").exists
        assert not s(textMatches="^lue?").exists
        assert not s(textMatches="^Blue$").exists
        assert s(textMatches=r"^(Blue|Red).*").exists


def test_app_operation(c: wda.Client):
    c.session("com.apple.Preferences")
    appinfo = c.app_current()
    assert appinfo['bundleId'] == 'com.apple.Preferences'

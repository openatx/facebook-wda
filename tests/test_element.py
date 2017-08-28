# coding: utf-8
#

import time
import wda
from pytest import mark

c = wda.Client()

def setup_function():
    c.home()


def test_element_properties():
    with c.session('com.apple.mobilesafari', ['-u', 'https://www.github.com']) as s:
        time.sleep(1.0)
        u = None
        for e in s(id='URL').find_elements():
            if e.className.endswith('Button'):
                u = e
                break
        assert u.label == 'Address'
        assert 'github' in u.value.lower()
        assert u.displayed == True
        assert u.visible == True
        assert u.enabled == True
        assert type(u.bounds) is wda.Rect
        u.clear_text()
        u.set_text('status.github.com\n')
        assert 'status' in u.value


def test_element_tap_hold():
    s = c.session()
    s(name='Settings').tap_hold(2.0)
    assert s(classChain='**/Icon[`name == "Weather"`]/Button[`name == "DeleteButton"`]').get(2.0, raise_error=False)


def test_element_name_matches():
    s = c.session()
    assert s(nameMatches='^S.ttings?').exists


def test_element_scroll_visible():
    with c.session('com.apple.Preferences') as s:
        general = s(name='General')
        assert not general.get().visible
        general.scroll()
        assert general.get().visible
        time.sleep(1)


@mark.skip("using frequency is low")
def test_element_scroll_direction():
    with c.session('com.apple.Preferences') as s:
        s(className='Table').scroll('up', 0.1)

@mark.skip("using frequency is low")
def test_element_pinch():
    with c.session('com.apple.Maps') as s:
        def alert_callback(s):
            s.alert.accept()

        s.set_alert_callback(alert_callback)
        s(className='Button', name='Tracking').tap()
        time.sleep(5)
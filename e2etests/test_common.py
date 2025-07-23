# coding: utf-8
# 

import wda


def test_rect():
    r = wda.Rect(10, 20, 10, 30) # x=10, y=20, w=10, h=30
    assert r.left == 10
    assert r.right == 20
    assert r.bottom == 50
    assert r.top == 20
    assert r.x == 10 and r.y == 20 and r.width == 10 and r.height == 30
    assert r.center.x == 15 and r.center.y == 35
    assert r.origin.x == 10 and r.origin.y == 20
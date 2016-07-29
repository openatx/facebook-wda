# coding: utf-8

import wda


c = wda.Client()

def test_swipe():
    s = c.session('com.apple.Preferences')
    print s.window_size()

    x1, y1, x2, y2 = (200, 500, 200, 200)
    s.swipe(x1, y1, x2, y2, 500)


if __name__ == '__main__':
    test_swipe()

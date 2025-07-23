# coding: utf-8
#

import wda


def test_xpath(app: wda.Client):
    with app:
        app.xpath("//*[@label='蓝牙']").click()
        assert app.xpath('//*[@label="设置"]').wait()
        assert app.xpath('//*[@label="设置"]').get().label == "设置"

        # test __getattr__
        assert app.xpath('//*[@label="设置"]').label == "设置"
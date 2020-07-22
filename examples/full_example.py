# coding: utf-8
#
# 网易云音乐测试示例
#

import os
import time
import wda
import requests
from logzero import logger


bundle_id = 'com.apple.Preferences'

def test_preferences(c: wda.Client):
    print("Status:", c.status())
    print("Info:", c.info)
    print("BatteryInfo", c.battery_info())
    print("AppCurrent:", c.app_current())
    # page_source = c.source()
    # assert "</XCUIElementTypeApplication>" in page_source

    app = c.session(bundle_id)
    selector = app(label="蜂窝网络")
    el = selector.get() 
    el.click()
    print("Element bounds:", el.bounds)

    logger.info("Take screenshot: %s", app.screenshot())
    
    app.swipe_right()
    app.swipe_up()

    app(label="电池").scroll()
    app(label="电池").click()


def test_open_safari(c: wda.Client):
    """ session操作 """
    app = c.session("com.apple.mobilesafari")
    app.deactivate(3) # 后台3s
    app.close() # 关闭


def test_send_keys_callback(c: wda.Client):
    def _handle_alert_before_send_keys(urlpath: str):
        if not urlpath.endswith("/wda/keys"):
            return
        if c.alert.exists:
            c.alert.accept()
        print("callback called")

    c.register_callback(wda.Callback.HTTP_REQUEST_BEFORE, _handle_alert_before_send_keys)
    c.send_keys("hello callback")


def test_error_callback(c: wda.Client):
    def err_handler(client: wda.Client, err):
        if isinstance(err, wda.WDARequestError):
            print("ERROR:", err)
            return wda.Callback.RET_ABORT # 直接退出
            return wda.Callback.RET_CONTINUE # 忽略错误继续执行
            return wda.Callback.RET_RETRY # 重试一下

    c.register_callback(wda.Callback.ERROR, err_handler)
    c.send_keys("hello callback")


if __name__ == "__main__":
    c = wda.USBClient()
    # c.healthcheck() # 恢复WDA状态
    test_wait_device_back_online(c)
    # test_preferences(c)
    # test_open_safari(c)

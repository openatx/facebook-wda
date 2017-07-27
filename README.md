# python-wda
[![Build Status](https://travis-ci.org/openatx/facebook-wda.svg?branch=master)](https://travis-ci.org/openatx/facebook-wda)
[![PyPI](https://img.shields.io/pypi/v/facebook-wda.svg)](https://pypi.python.org/pypi/facebook-wda)
[![PyPI](https://img.shields.io/pypi/l/facebook-wda.svg)]()

Facebook WebDriverAgent Python Client Library (not official)

Most functions finished.

Recommended use this version of WebDriverAgent (already tested) [31 May 2017 a8def24ca67f8a74dd709b899c8ea539c9c488ea](https://github.com/facebook/WebDriverAgent/tree/a8def24ca67f8a74dd709b899c8ea539c9c488ea)

Implemented apis describe in <https://github.com/facebook/WebDriverAgent/wiki/Queries>

This library has been used in project atx <https://github.com/codeskyblue/AutomatorX>

## Installation
1. You need to start WebDriverAgent by yourself

	Follow the instructions in <https://github.com/facebook/WebDriverAgent>

	It is better to start with Xcode to prevent CodeSign issues.

	But it is also ok to start WDA with command line.

	```
	xcodebuild -project WebDriverAgent.xcodeproj -scheme WebDriverAgentRunner -destination 'platform=iOS Simulator,name=iPhone 6' test
	```

2. Install python wda client

	```
	pip install --pre facebook-wda
	```

## TCP connection over USB (optional)
You can use wifi network, it is very convinient, but not very stable enough.

I found a tools named `iproxy` which can forward device port to localhost, it\'s source code is here <https://github.com/libimobiledevice/libusbmuxd>

The usage is very simple `iproxy <local port> <remote port> [udid]`

## Configuration
```python
import wda

wda.DEBUG = False # default False
wda.HTTP_TIMEOUT = 60.0 # default 60.0 seconds
```

## How to use
Create a client

```py
import wda

# Enable debug will see http Request and Response
# wda.DEBUG = True
c = wda.Client('http://localhost:8100')
```

A `wda.WDAError` will be raised if communite with WDA went wrong.


Other APIs

```py
# Show status
print c.status()

# Press home button
c.home()

# Hit healthcheck
c.healthcheck()

# Get page source
c.source() # format XML
c.source(accessible=True) # default false, format JSON
```

Take screenshot, only can save format png

```py
c.screenshot('screen.png')
```

Open app

```py
with c.session('com.apple.Health') as s:
	print s.orientation
```

Same as

```py
s = c.session('com.apple.Health')
print s.orientation
s.close()
```

For web browser like Safari you can define page whit which will be opened:
```py
s = c.session('com.apple.mobilesafari', ['-u', 'https://www.google.com/ncr'])
print s.orientation
s.close()
```

Session operations

> Note: if element not found in 90s, RuntimeError will be raised

```py
# Current bundleId and sessionId
print s.bundle_id, s.id

# One of <PORTRAIT | LANDSCAPE>
print s.orientation # expect PORTRAIT

# Change orientation
s.orientation = wda.LANDSCAPE # there are many other directions

# Deactivate App for some time
s.deactivate(5.0) # 5s

# Get width and height
print s.window_size()
# Expect json output
# For example: {u'height': 736, u'width': 414}

# Simulate touch
s.tap(200, 200)

# Double touch
s.double_tap(200, 200)

# Simulate swipe, utilizing drag api
s.swipe(x1, y1, x2, y2, 0.5) # 0.5s

# tap hold
s.tap_hold(x, y, 1.0)

# Find elements
print s(text="Dashboard").exists

# Find elements with partial text
# the partial just for text、name、value and label. default is False
# print s(text="Dashbo", partial=True).exists # Deprecated
print s(textContains="Dashbo").exists

# Find with xpath and set value
d(xpath=u"//TextField").set_text("someone@163.com\n")

# Find second element, index from 0
print s(text="Dashboard")[1]

# Tap selected element
s(text="Dashboard", className='Button').tap()

# Tap and hold
s(text="Dashboard").tap_hold(2.0) # tapAndHold for 2.0s

# Set text
s(text="Name").set_text("Hello")

# Clear text
s(text="Name").clear_text()

# Scroll to visible
s(text="Name").scroll()

# Hide keyboard (not working in simulator)
s.keyboard.dismiss()

# Swipe
s(className="Image").swipe("left")

# Pinch
s(className="Map").pinch(2, 1) # scale=2, speed=1
s(className="Map").pinch(0.1, -1) # scale=0.1, speed=-1 (I donot very understand too)

# alert
print s.alert.exists
print s.alert.text
s.alert.accept()
s.alert.dismiss()
s.alert.wait(5) # if alert apper in 5 second it will return True,else return False (default 20.0)
s.alert.wait() # wait alert apper in 2 second

s.alert.buttons()
# example return: ["设置", "好"]

s.alert.click("设置")
# s.close() # kill app, no need to call in with
```

Properties

```py
e = s(text='Dashboard')
e.count # same as len(e)

# bool props
e.exists
e.accessible
e.displayed
e.enabled

# return namedtuple
e.bounds # ex: Rect(x=144, y=28, width=88.0, height=27.0)
e.bounds.x # expect 144

# other
e.text # ex: Dashboard
e.class_name # ex: XCUIElementTypeStaticText
```

## TODO
longTap not done pinch(not found in WDA)

TouchID

* Match Touch ID
* Do not match Touch ID

## Beta api

```
# elems()
els = s(className="Button").elems()
el = els[0]

# properies
print el.id # element id
print el.name # send http request to wda
print el.name # use cached value
print el.label
print el.className
print el.enabled
print el.accessible
print el.value
print el.bounds # Rect object

# functions
el.tap()
el.set_text('hello')
el.clear_text()

# get child elements
el = el.child(className="Button", text="Network").wait()
```

## How to handle alert message automaticly
For example

```python
import wda

s = wda.Client().session()

def _alert_callback():
    s.alert.accept()

wda.alert_callback = _alert_callback

# do operations, when alert popup, it will auto accept
s(type="Button").click()
```	

## iOS Build-in Apps
**苹果自带应用**

|   Name | Bundle ID          |
|--------|--------------------|
| iMovie | com.apple.iMovie |
| Apple Store | com.apple.AppStore |
| Weather | com.apple.weather |
| 相机Camera | com.apple.camera |
| iBooks | com.apple.iBooks |
| Health | com.apple.Health |
| Settings | com.apple.Preferences |
| Watch | com.apple.Bridge |
| Game Center | com.apple.gamecenter |
| Wallet | com.apple.Passbook |
| 电话 | com.apple.mobilephone |
| 备忘录 | com.apple.mobilenotes |
| 指南针 | com.apple.compass |
| 浏览器 | com.apple.mobilesafari |
| 日历 | com.apple.mobilecal |
| 信息 | com.apple.MobileSMS |
| 时钟 | com.apple.mobiletimer |
| 照片 | com.apple.mobileslideshow |
| 提醒事项 | com.apple.reminders |
| Desktop | com.apple.springboard (Start this will cause your iPhone reboot) |

**第三方应用 Thirdparty**

|   Name | Bundle ID          |
|--------|--------------------|
| 腾讯QQ | com.tencent.mqq |
| 微信 | com.tencent.xin |
| 部落冲突 | com.supercell.magic |
| 钉钉 | com.laiwang.DingTalk |
| Skype | com.skype.tomskype |
| Chrome | com.google.chrome.ios |


Another way to list apps installed on you phone is use `ideviceinstaller`
install with `brew install ideviceinstaller`

List apps with command

```sh
$ ideviceinstaller -l
```

## Reference
Source code

- [Router](https://github.com/facebook/WebDriverAgent/blob/master/WebDriverAgentLib/Commands/FBElementCommands.m#L62)
- [Alert](https://github.com/facebook/WebDriverAgent/blob/master/WebDriverAgentLib/Commands/FBAlertViewCommands.m#L25)

## Articles
* <https://testerhome.com/topics/5524> By [diaojunxiam](https://github.com/diaojunxian)

## Contributors
* [diaojunxian](https://github.com/diaojunxian)
* [iquicktest](https://github.com/iquicktest)

## DESIGN
[DESIGN](DESIGN.md)

## LICENSE
[MIT](LICENSE)


# python-wda
[![Build Status](https://travis-ci.org/openatx/facebook-wda.svg?branch=master)](https://travis-ci.org/openatx/facebook-wda)
[![PyPI](https://img.shields.io/pypi/v/facebook-wda.svg)](https://pypi.python.org/pypi/facebook-wda)
[![PyPI](https://img.shields.io/pypi/l/facebook-wda.svg)]()

Facebook WebDriverAgent Python Client Library (not official)

Most functions finished.

Implemented apis describe in <https://github.com/facebook/WebDriverAgent/wiki/Queries>

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

## How to use
Create a client

```py
import wda
c = wda.Client('http://localhost:8100')

# Show status
print c.status()

# Press home button
c.home()
```

Take screenshot

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

Session operations

```py
# One of <PORTRAIT | LANDSCAPE>
print s.orientation # expect PORTRAIT

# Get width and height
print s.window_size()
# Expect json output
# For example: {u'height': 736, u'width': 414}

# Simulate touch
s.tap(200, 200)

# Find elements
print s(text="Dashboard").exists

# Find second element, index from 0
print s(text="Dashboard")[1]

# Tap selected element
s(text="Dashboard", className='Button').tap()

# Set text
s(text="Name").set_text("Hello")

# Clear text
s(text="Name").clear_text()

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

# return json
e.rect # ex: {u'origin': {u'y': 0, u'x': 0}, u'size': {u'width': 85, u'height': 20}}

# other
e.text # ex: Dashboard
e.class_name # ex: XCUIElementTypeStaticText
```

## TODO
Alert operation not implemented, also longTap, drag, pinch(not found in WDA)

Design:

```py
print s.alert.text()
s.alert.accept()
s.alert.dismiss()
```

TouchID

* Match Touch ID
* Do not match Touch ID

## iOS Build-in Apps
|   Name | Bundle ID          |
|--------|--------------------|
| iMovie | com.apple.iMovie |
| Chrome | com.google.chrome.ios |
| Apple Store | com.apple.AppStore |
| Weather | com.apple.weather |
| Camera | com.apple.camera |
| iBooks | com.apple.iBooks |
| Health | com.apple.Health |
| Desktop | com.apple.springboard |

## Reference
[Source code](https://github.com/facebook/WebDriverAgent/blob/master/WebDriverAgentLib/Commands/FBElementCommands.m#L62)
 
## DESIGN
[DESIGN](DESIGN.md)

## LICENSE
[MIT](LICENSE)

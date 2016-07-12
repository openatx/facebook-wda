# python-wda
[![Build Status](https://travis-ci.org/codeskyblue/python-wda.svg?branch=master)](https://travis-ci.org/codeskyblue/python-wda)

Facebook WebDriverAgent Python Client Library (not official)

Not finished yet.

## Installation
1. You need to start WebDriverAgent by yourself

	Follow the instructions in <https://github.com/facebook/WebDriverAgent>

	And start WDA with command

	```
	xcodebuild -project WebDriverAgent.xcodeproj -scheme WebDriverAgentRunner -destination 'platform=iOS Simulator,name=iPhone 6' test
	```

2. Install python wda client

	```
	pip install --pre facebook-wda
	```

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
	# One of <PORTRAIT | LANDSCAPE>
	print s.orientation # expect PORTRAIT
	# Get width and height
	print s.window_size
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

# python-wda
Facebook WebDriverAgent Python Client Library (not official)

Not finished yet.

## Installation
1. You need to start WebDriverAgent by yourself

	Follow the instructions in <https://github.com/facebook/WebDriverAgent>

	And start WDA with command

	```
	xcodebuild -project WebDriverAgent.xcodeproj \
           -scheme WebDriverAgentRunner \
           -destination 'platform=iOS Simulator,name=iPhone 6' \
           test
    ```

2. Install python-wda (TODO)

	```
	pip install wda
	```

## How to use
```
import wda

c = wda.Client('http://localhost:8100')
print c.status()
```

## DESIGN
[DESIGN](DESIGN.md)

## LICENSE
[MIT](LICENSE)

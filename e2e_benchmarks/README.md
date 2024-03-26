# E2E Testing

## Overview
This directory contains end-to-end tests for the operator.
This will involve benchmark testing across different [WDA service versions](https://github.com/appium/WebDriverAgent/releases).

## Running the tests
The tests can be run using the `pytest -v -rsx '/Users/youngfreefjs/Desktop/code/github/facebook-wda/e2e_benchmarks/'` script.
This will install the WDA service versions, ensuring a swift identification of whether the client remains compatible and functional after an upgrade in the WDA service.

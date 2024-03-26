'''
WDA Custom Command Testing
source code here: https://github.com/appium/WebDriverAgent/blob/master/WebDriverAgentLib/Commands/FBCustomCommands.m#L38
WDA API document and example(not offical): https://documenter.getpostman.com/view/1837823/TVmMhJNB#573d11c5-c434-4753-b845-4a3afcc4b614
'''
import os
import pytest
import unittest
import jsonschema
import wda
from .constant import *

curPath = os.path.abspath(os.path.dirname(__file__))


class TestDevice(unittest.TestCase):

    def setUp(self):
        self.under_test_bundle_id = UNDER_TEST_BUNDLE_ID
        self.wda_client: wda.Client = wda.Client()
        self.app = self.wda_client.session(bundle_id=self.under_test_bundle_id)

    def tearDown(self):
        self.wda_client.close()

    '''
    Method: POST
    Endpoint: {{baseURL}}/session/{{sessionId}}/wda/deactivateApp
    Description: Put app into background and than put it back.
    '''
    def test_deactivate_app(self):
        self.app.deactivate(duration=1)


    '''
    Method: POST
    Endpoint: {{baseURL}}/session/{{sessionId}}/wda/keyboard/dismiss
    Description: Put the keyboard into the background.
    '''
    def test_keybord_dismiss(self):
        with pytest.raises(RuntimeError) as e:
            self.app.keyboard_dismiss()
    
    
    '''
    Method: POST
    Endpoint: {{baseURL}}/wda/lock
    Endpoint: {{baseURL}}/wda/unlock
    Description: Lock the device.
    '''
    def test_keybord_lock_and_unlock(self):
        self.app.lock()
        self.app.unlock()


    '''
    Method: GET
    Endpoint: {{baseURL}}/session/{{sessionId}}/wda/screen
    Description: UIKit scale factor
    Refs:
        https://developer.apple.com/library/archive/documentation/DeviceInformation/Reference/iOSDeviceCompatibility/Displays/Displays.html
    There is another way to get scale
        self._session_http.get("/wda/screen").value returns {"statusBarSize": {'width': 320, 'height': 20}, 'scale': 2}
    '''
    def test_scale(self):
        self.assertIsInstance(self.app.scale, int)
        
    
    '''
    Method: GET
    Endpoint: {{baseURL}}/wda/activeAppInfo
    Description: Return bundleId pid and etc. like:
    {'processArguments': {'env': {}, 'args': []}, 'name': '', 'pid': 19052, 'bundleId': 'com.test.cert.TestCert'}
    '''
    def test_active_app_info(self):
        except_json_schema = {"$schema":"http://json-schema.org/draft-07/schema#","type":"object","properties":
                              {"processArguments":{"type":"object","properties":{"env":{"type":"object",
                                "additionalProperties":False},"args":{"type":"array"}},"additionalProperties":False,
                                "required":["env","args"]},"name":{"type":"string"},"pid":{"type":"integer"},
                                "bundleId":{"type":"string"}},"additionalProperties":False,"required":
                                ["processArguments","name","pid","bundleId"]}
        self.assertTrue(jsonschema.Draft7Validator(except_json_schema).is_valid(self.app.app_current()))


    '''
    Method: POST
    Endpoint: {{baseURL}}/session/{{sessionId}}/wda/setPasteboard
    Description: Set paste board  board.
    '''
    def test_set_paste_board(self):
        self.app.set_clipboard('test')

    '''
    Method: POST
    Endpoint: {{baseURL}}/session/{{sessionId}}/wda/getPasteboard
    #NOTE: IS NOT USED. RETURN NULL.
    e.g:
    curl http://127.0.0.1:8100/session/3D28C745-5290-4787-948C-43C7A27E6146/wda/getPasteboard -X POST -v
    *   Trying 127.0.0.1:8100...
    * Connected to 127.0.0.1 (127.0.0.1) port 8100 (#0)
    > POST /session/3D28C745-5290-4787-948C-43C7A27E6146/wda/getPasteboard HTTP/1.1
    > Host: 127.0.0.1:8100
    > User-Agent: curl/7.86.0
    > Accept: */*
    > 
    * Mark bundle as not supporting multiuse
    < HTTP/1.1 400 Bad Request
    < Server: WebDriverAgent/1.0
    < Access-Control-Allow-Origin: *
    < Date: Thu, 21 Mar 2024 02:18:52 GMT
    < Access-Control-Allow-Headers: Content-Type, X-Requested-With
    < Accept-Ranges: bytes
    < Content-Length: 0
    < Connection: close
    < 
    * Closing connection 0
    '''
    @pytest.mark.skip('WDA API NOT USEFUL: {{baseURL}}/session/{{sessionId}}/wda/getPasteboard')
    def test_get_paste_board(self):
        '''Wait to PR merge: https://github.com/openatx/facebook-wda/pull/133/files'''
        ...


    '''
    Method: GET
    Endpoint: {{baseURL}}/wda/device/info
    Description: Return device info.
    Example Return:
    {"timeZone": "GMT+0800", "currentLocale": "zh_CN", "model": "iPhone", "uuid": 
    "25E3142B-303E-41FE-9F6A-2C303CB66FBC", "thermalState": 1, "userInterfaceIdiom": 0,
    "userInterfaceStyle": "light", "name": "iPhone", "isSimulator": False}
    '''
    def test_device_info(self):
        expect_schema = {"$schema":"http://json-schema.org/draft-07/schema#","type":"object",
                         "properties":{"timeZone":{"type":"string"},"currentLocale":{"type":"string"},
                        "model":{"type":"string"},"uuid":{"type":"string"},"thermalState":{"type":"integer"},
                        "userInterfaceIdiom":{"type":"integer"},"userInterfaceStyle":{"type":"string"},
                        "name":{"type":"string"},"isSimulator":{"type":"boolean"}},"additionalProperties":False,
                        "required":["timeZone","currentLocale","model","uuid","thermalState","userInterfaceIdiom",
                        "userInterfaceStyle","name","isSimulator"]}
        self.assertTrue(jsonschema.Draft7Validator(expect_schema).is_valid(self.app.device_info()))


    '''
    Method: GET
    Endpoint: {{baseURL}}/session/{{sessionId}}/wda/batteryInfo
    Description: Return device battery info.
    Example Return:
    {"level": 0.5799999833106995, "state": 2}
    '''
    def test_battery_info(self):
        import json
        except_json_schema = {"$schema":"http://json-schema.org/draft-07/schema#","type":"object",
                              "properties":{"level":{"type":"number"},"state":{"type":"integer"}},
                              "additionalProperties":False,"required":["level","state"]}
        self.assertTrue(jsonschema.Draft7Validator(except_json_schema).is_valid(self.app.battery_info()))


    '''
    Method: GET
    Endpoint: {{baseURL}}/wda/homescreen
    Description: back to home screen
    '''
    def test_homescreen(self):
        self.assertEqual(self.app.app_current().get('bundleId'), UNDER_TEST_BUNDLE_ID)
        self.app.home()
        self.assertEqual(self.app.app_current().get('bundleId'), HOME_SCREEN_BUNDLE_ID)


    '''
    Method: GET
    Endpoint: {{baseURL}}/wda/locked
    Description: check device is locked or not.
    '''
    def test_locked(self):
        self.assertFalse(self.app.locked())

'''
WDA Session Command Testing
API FBSessionCommands.m
source code here: https://github.com/appium/WebDriverAgent/blob/master/WebDriverAgentLib/Commands/FBSessionCommands.m
WDA API document and example(not offical): https://documenter.getpostman.com/view/1837823/TVmMhJNB#f94ebe16-ae2a-4098-879e-570a0138c7f4
'''
import os
import pytest
import unittest
import jsonschema
import wda
from .constant import *

curPath = os.path.abspath(os.path.dirname(__file__))


class TestSessionCommands(unittest.TestCase):

    def setUp(self):
        self.wda_client: wda.Client = wda.Client()
        # self.app = self.wda_client.session(bundle_id=self.under_test_bundle_id)
        self.temp_file_pic = os.path.join(curPath, 'temp_file_pic.png')

    def tearDown(self):
        self.wda_client.close()
        [os.remove(temp_file) for temp_file in [self.temp_file_pic] if os.path.exists(temp_file)]


    '''
     Method: POST 
     Endpoint: {{baseURL}}/session/{{sessionId}}/url
    '''
    @pytest.mark.skip("UNKNOW HOW TO TEST: [POST] {{baseURL}}/session/{{sessionId}}/url")
    def test_url(self):
        pass


    '''
     Method: POST 
     Endpoint: {{baseURL}}/session
    '''
    def test_create_session_id(self):
        before_create_session_id = self.wda_client.session_id
        self.assertIsNot(self.wda_client.session().session_id, before_create_session_id, None)
        client: wda.Client = wda.Client().session(bundle_id=UNDER_TEST_BUNDLE_ID)


    '''
     Method: POST 
     Endpoint: {{baseURL}}/session/{{sessionId}}/wda/apps/launch
    '''
    def test_launch_app(self):
        self.wda_client.app_activate(UNDER_TEST_BUNDLE_ID)
        self.wda_client.app_current().get('bundle_id') == UNDER_TEST_BUNDLE_ID


    '''
     Method: GET 
     Endpoint: {{baseURL}}/session/{{sessionId}}/wda/apps/list
    '''
    def test_app_list(self):
        self.wda_client.session(UNDER_TEST_BUNDLE_ID)
        self.assertIsInstance(self.wda_client.app_list(), list)
        self.assertEqual(self.wda_client.app_list()[0].get('bundleId'), UNDER_TEST_BUNDLE_ID)

    '''
     Method: POST 
     Endpoint: {{baseURL}}/session/{{sessionId}}/wda/apps/state
    '''
    def test_app_state(self):
        self.wda_client.session(UNDER_TEST_BUNDLE_ID)
        self.assertIsInstance(self.wda_client.app_state(UNDER_TEST_BUNDLE_ID), dict)
        self.assertEqual(self.wda_client.app_state(UNDER_TEST_BUNDLE_ID).get('value'), 4)

    def test_unknow_app_state(self):
        self.assertEqual(self.wda_client.app_state(UNKNOW_BUNDLE_ID).get('value'), 1)


    '''
     Method: POST 
     Endpoint: {{baseURL}}/session/{{sessionId}}/wda/apps/terminate
    '''
    def test_app_terminate(self):
        self.wda_client.app_terminate(UNDER_TEST_BUNDLE_ID)
        self.assertTrue(self.wda_client.app_state(UNDER_TEST_BUNDLE_ID).get('value') == 1)


    '''
     Method: GET 
     Endpoint: {{baseURL}}/status
    '''
    def test_status_command_return_schema(self):
        '''
        Current Origin Status Return:
        {
            "build": {
                "time": "Mar 18 2024 11:29:21",
                "productBundleIdentifier": "com.facebook.WebDriverAgentRunner"
            },
            "os": {
                "testmanagerdVersion": 28,
                "name": "iOS",
                "sdkVersion": "16.4",
                "version": "16.3.1"
            },
            "device": "iphone",
            "ios": {
                "ip": "XX.XX.XX.XX"
            },
            "message": "WebDriverAgent is ready to accept commands",
            "state": "success",
            "ready": true,
            "sessionId": "XXXXX"
        }
        '''
        self.wda_client.session(UNDER_TEST_BUNDLE_ID)
        expect_schema = {"$schema":"http://json-schema.org/draft-07/schema#","type":"object","properties":{"build":\
                        {"type":"object","properties":{"time":{"type":"string"},"productBundleIdentifier":\
                        {"type":"string"}},"additionalProperties":"false","required":["time",\
                        "productBundleIdentifier"]},"os":{"type":"object","properties":{"testmanagerdVersion"\
                        :{"type":"integer"},"name":{"type":"string"},"sdkVersion":{"type":"string"},"version":\
                        {"type":"string"}},"additionalProperties":"false","required":["testmanagerdVersion","name",\
                        "sdkVersion","version"]},"device":{"type":"string"},"ios":{"type":"object","properties":\
                        {"ip":{"type":"string"}},"additionalProperties":"false","required":["ip"]},"message":\
                        {"type":"string"},"state":{"type":"string"},"ready":{"type":"boolean"},"sessionId":\
                        {"type":"string"}},"additionalProperties":"false","required":["build","os","device","ios",\
                        "message","state","ready", "sessionId"]}

        self.assertTrue(jsonschema.Draft7Validator(expect_schema).is_valid(self.wda_client.status()))

    def test_status_command_state_and_ready(self):
        status = self.wda_client.status()
        assert all([status['state'] == 'success', status['ready'] is True])


    '''
     Method: GET 
     Endpoint: {{baseURL}}/session/{{sessionId}}
    '''
    @pytest.mark.skip('NOT IMPLEMENTED: [GET] {{baseURL}}/session/{{sessionId}}')
    def test_session_info(self):
        pass

    '''
     Method: DELETE 
     Endpoint: {{baseURL}}/session/{{sessionId}}
    '''
    def test_delete_session(self):
        self.wda_client.session(UNDER_TEST_BUNDLE_ID)
        assert self.wda_client.session_id is not None
        print(self.wda_client.close())

    '''
     Method: POST 
     Endpoint: {{baseURL}}/session/{{sessionId}}/wda/apps/activate
    '''
    def test_app_activate(self):
        self.wda_client.session()
        self.wda_client.app_activate(UNDER_TEST_BUNDLE_ID)
        self.assertEqual(self.wda_client.app_current().get('bundleId'), UNDER_TEST_BUNDLE_ID)


    '''
     Method: GET 
     Endpoint: {{baseURL}}/wda/healthcheck
    '''
    def test_health_check(self):
        health_check = self.wda_client.healthcheck()
        assert all([
            hasattr(health_check, 'value'),
            hasattr(health_check, 'sessionId'),
            health_check.get('value') == None,
            health_check.get('sessionId') == None
        ])
    
    def test_health_check_has_session_id(self):
        self.wda_client.session(UNDER_TEST_BUNDLE_ID)
        health_check = self.wda_client.healthcheck()
        assert all([
            hasattr(health_check, 'value'),
            hasattr(health_check, 'sessionId'),
            health_check.get('value') == None,
            health_check.get('sessionId') == self.wda_client.session_id
        ])

    '''
     Method: GET
     Endpoint: {{baseURL}}/session/{{sessionId}}/appium/settings
     Return Example:

     ```
     {
        "mjpegFixOrientation": false,
        "boundElementsByIndex": false,
        "mjpegServerFramerate": 10,
        "screenshotOrientation": "auto",
        "reduceMotion": false,
        "elementResponseAttributes": "type,label",
        "screenshotQuality": 3,
        "mjpegScalingFactor": 100,
        "keyboardPrediction": 0,
        "defaultActiveApplication": "auto",
        "mjpegServerScreenshotQuality": 25,
        "defaultAlertAction": "",
        "keyboardAutocorrection": 0,
        "useFirstMatch": false,
        "shouldUseCompactResponses": true,
        "customSnapshotTimeout": 15,
        "dismissAlertButtonSelector": "",
        "activeAppDetectionPoint": "64.00,64.00",
        "snapshotMaxDepth": 50,
        "waitForIdleTimeout": 10,
        "includeNonModalElements": false,
        "acceptAlertButtonSelector": "",
        "animationCoolOffTimeout": 2
    }
    ```
    '''
    def test_appium_settings(self):
        appium_settings = self.wda_client.appium_settings()
        expect_schema = {"$schema":"http://json-schema.org/draft-07/schema#","type":"object","properties":
                         {"mjpegFixOrientation":{"type":"boolean"},"boundElementsByIndex":{"type":"boolean"},
                          "mjpegServerFramerate":{"type":"integer"},"screenshotOrientation":{"type":"string"},
                          "reduceMotion":{"type":"boolean"},"elementResponseAttributes":{"type":"string"},
                          "screenshotQuality":{"type":"integer"},"mjpegScalingFactor":{"type":"integer"},
                          "keyboardPrediction":{"type":"integer"},"defaultActiveApplication":{"type":"string"},
                          "mjpegServerScreenshotQuality":{"type":"integer"},"defaultAlertAction":{"type":"string"},
                          "keyboardAutocorrection":{"type":"integer"},"useFirstMatch":{"type":"boolean"},
                          "shouldUseCompactResponses":{"type":"boolean"},"customSnapshotTimeout":{"type":"integer"},
                          "dismissAlertButtonSelector":{"type":"string"},"activeAppDetectionPoint":{"type":"string"},
                          "snapshotMaxDepth":{"type":"integer"},"waitForIdleTimeout":{"type":"integer"},
                          "includeNonModalElements":{"type":"boolean"},"acceptAlertButtonSelector":{"type":"string"},
                          "animationCoolOffTimeout":{"type":"integer"}},"additionalProperties":False,
                          "required":["mjpegFixOrientation","boundElementsByIndex","mjpegServerFramerate",
                            "screenshotOrientation","reduceMotion","elementResponseAttributes","screenshotQuality",
                            "mjpegScalingFactor","keyboardPrediction","defaultActiveApplication","mjpegServerScreenshotQuality",
                            "defaultAlertAction","keyboardAutocorrection","useFirstMatch","shouldUseCompactResponses",
                            "customSnapshotTimeout","dismissAlertButtonSelector","activeAppDetectionPoint","snapshotMaxDepth",
                            "waitForIdleTimeout","includeNonModalElements","acceptAlertButtonSelector","animationCoolOffTimeout"]} 
        self.assertTrue(jsonschema.Draft7Validator(expect_schema).is_valid(appium_settings))   


    '''
     Method: GET
     Endpoint: {{baseURL}}/wda/shutdown
    '''
    @pytest.mark.skip('NOT IMPLEMENTED: [GET] {{baseURL}}/wda/shutdown')
    def test_wda_shutdown(self):
        pass


    '''
     Method: GET
     Endpoint: {{baseURL}}/health
    '''
    @pytest.mark.skip('NOT IMPLEMENTED: [GET] {{baseURL}}/health')
    def test_health(self):
        pass

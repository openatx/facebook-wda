'''
WDA Session Command Testing
API FBSessionCommands.m
source code here: https://github.com/appium/WebDriverAgent/blob/master/WebDriverAgentLib/Commands/FBSessionCommands.m
WDA API document and example(not offical): https://documenter.getpostman.com/view/1837823/TVmMhJNB#f94ebe16-ae2a-4098-879e-570a0138c7f4
'''
import os
import unittest

# Jsonschema generate online: https://www.lddgo.net/string/generate-json-schema
import jsonschema

import wda

curPath = os.path.abspath(os.path.dirname(__file__))


class TestSessionCommands(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.wda_client: wda.Client = wda.Client()
        self.temp_file_pic = os.path.join(curPath, 'temp_file_pic.png')

    @classmethod
    def tearDownClass(self):
        [os.remove(temp_file) for temp_file in [self.temp_file_pic] if os.path.exists(temp_file)]


    # WDA /url command
    @unittest.skip("NOT IMPLEMENT YET")
    def test_url_command_return_type(self):
        pass


    # WDA POST /session command
    def test_create_session(self):
        self.assertIsInstance(self.wda_client.session(), wda.Session)

    def test_create_session_id(self):
        before_create_session_id = self.wda_client.session_id
        # self.assertIsNot(self.wda_client.session().session_id, before_create_session_id, None)
        client: wda.Client = wda.Client().session(bundle_id="com.test.cert.TestCert")
        client.open_url()


    # WDA /status command
    def test_status_command_return_type(self):
        self.assertIsInstance(self.wda_client.status(), dict)

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
            "sessionId": null
        }
        '''
        expect_schema = {"$schema":"http://json-schema.org/draft-07/schema#","type":"object","properties":{"build":\
                        {"type":"object","properties":{"time":{"type":"string"},"productBundleIdentifier":\
                        {"type":"string"}},"additionalProperties":"false","required":["time",\
                        "productBundleIdentifier"]},"os":{"type":"object","properties":{"testmanagerdVersion"\
                        :{"type":"integer"},"name":{"type":"string"},"sdkVersion":{"type":"string"},"version":\
                        {"type":"string"}},"additionalProperties":"false","required":["testmanagerdVersion","name",\
                        "sdkVersion","version"]},"device":{"type":"string"},"ios":{"type":"object","properties":\
                        {"ip":{"type":"string"}},"additionalProperties":"false","required":["ip"]},"message":\
                        {"type":"string"},"state":{"type":"string"},"ready":{"type":"boolean"},"sessionId":\
                        {"type":"null"}},"additionalProperties":"false","required":["build","os","device","ios",\
                        "message","state","ready"]}

        self.assertTrue(jsonschema.Draft7Validator(expect_schema).is_valid(self.wda_client.status()))

    def test_status_command_state_and_ready(self):
        status = self.wda_client.status()
        assert all([status['state'] == 'success', status['ready'] is True])


'''
WDA Screenshot Command Testing
source code here: https://github.com/appium/WebDriverAgent/blob/master/WebDriverAgentLib/Commands/FBScreenshotCommands.m
WDA API document and example(not offical): https://documenter.getpostman.com/view/1837823/TVmMhJNB#bf7cb0a1-cc3b-4eb5-a9ee-1e7e63b55df1
'''
import os
import unittest
from typing import List
import wda
from .constant import *

curPath = os.path.abspath(os.path.dirname(__file__))


class TestScreenshot(unittest.TestCase):

    def setUp(self):
        self.under_test_bundle_id = UNDER_TEST_BUNDLE_ID
        self.wda_client: wda.Client = wda.Client()
        self.app = self.wda_client.session(bundle_id=self.under_test_bundle_id)
        self.temp_file_pic = os.path.join(curPath, 'temp_file_pic.png')

    def tearDown(self):
        self.app.orientation = wda.PORTRAIT
        self.wda_client.close()
        [os.remove(temp_file) for temp_file in [self.temp_file_pic] if os.path.exists(temp_file)]


    '''
     Method: POST 
     Endpoint: {{baseURL}}/screenshot
    '''
    def test_screenshot(self):
        self.app.screenshot(self.temp_file_pic)
        assert os.path.exists(self.temp_file_pic)

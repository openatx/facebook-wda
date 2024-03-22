'''
WDA Orientation Command Testing
source code here: https://github.com/appium/WebDriverAgent/blob/master/WebDriverAgentLib/Commands/FBOrientationCommands.m
WDA API document and example(not offical): https://documenter.getpostman.com/view/1837823/TVmMhJNB#1ca27827-9931-4315-a6aa-141b6015ac04
'''
import os
import time
import pytest
import unittest
from typing import List
from collections.abc import Iterable
import wda
from .constant import *

curPath = os.path.abspath(os.path.dirname(__file__))


class TestOrientation(unittest.TestCase):

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
     Method: GET 
     Endpoint: {{baseURL}}/session/{{sessionId}}/orientation
    '''
    def test_orientation(self):
        assert self.app.orientation in ['PORTRAIT', 'LANDSCAPE']


    '''
     Method: POST 
     Endpoint: {{baseURL}}/session/{{sessionId}}/orientation
    '''
    def test_set_orientation(self):
        self.app.orientation = wda.LANDSCAPE
        time.sleep(1)
        assert self.app.orientation == 'LANDSCAPE'
    
    
    '''
     Method: GET 
     Endpoint: {{baseURL}}/session/{{sessionId}}/rotation
    '''
    @pytest.mark.skip('NOT IMPLEMENTED: [GET] {{baseURL}}/session/{{sessionId}}/rotation')
    def test_get_rotation(self):
        pass


    '''
     Method: POST 
     Endpoint: {{baseURL}}/session/{{sessionId}}/rotation
    '''
    @pytest.mark.skip('NOT IMPLEMENTED: [POST] {{baseURL}}/session/{{sessionId}}/rotation')
    def test_set_rotation(self):
        pass


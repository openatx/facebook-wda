'''
WDA Find Element Command Testing
source code here: https://github.com/appium/WebDriverAgent/blob/master/WebDriverAgentLib/Commands/FBElementCommands.m
WDA API document and example(not offical): https://documenter.getpostman.com/view/1837823/TVmMhJNB#56e19c88-8571-48d3-a9f1-8e9bd0cbae0d
'''
import os
import pytest
import unittest
from typing import List
from collections.abc import Iterable
import wda
from .constant import *

curPath = os.path.abspath(os.path.dirname(__file__))


class TestFindElement(unittest.TestCase):

    def setUp(self):
        self.under_test_bundle_id = UNDER_TEST_BUNDLE_ID
        self.wda_client: wda.Client = wda.Client()
        self.app = self.wda_client.session(bundle_id=self.under_test_bundle_id)
        self.temp_file_pic = os.path.join(curPath, 'temp_file_pic.png')

    def tearDown(self):
        self.wda_client.close()
        [os.remove(temp_file) for temp_file in [self.temp_file_pic] if os.path.exists(temp_file)]


    '''
     Method: GET 
     Endpoint: {{baseURL}}/session/{{sessionId}}/elements
    '''
    def test_elements(self):
        elements = self.app(text='IMG_BTN').find_elements()
        self.assertTrue(isinstance(elements, Iterable))  # 检查是否可迭代
        for element in elements:
            self.assertIsInstance(element, wda.Element) 

    def test_element_ids(self):
        elements = self.app(text='IMG_BTN').find_element_ids()
        self.assertTrue(isinstance(elements, Iterable))  # 检查是否可迭代
        for element in elements:
            self.assertIsInstance(element, str) 


    '''
     Method: GET 
     Endpoint: {{baseURL}}/session/{{sessionId}}/element/{{uuid}}/elements
    '''
    @pytest.mark.skip('NOT IMPLEMENTED: [GET] /session/{{sessionId}}/element/{{uuid}}/elements')
    def test_ele_elements(self):
        pass


    '''
     Method: GET 
     Endpoint: {{baseURL}}/session/{{sessionId}}/element
    '''
    @pytest.mark.skip('NOT IMPLEMENTED: [GET] {{baseURL}}/session/{{sessionId}}/element')
    def test_wda_element(self):
        pass


    '''
     Method: GET 
     Endpoint: {{baseURL}}/session/{{sessionId}}/wda/element/{{uuid}}/getVisibleCells
    
    Return Example:
    ```
        {'value': [{'ELEMENT': '31000000-0000-0000-996B-000000000000', 
        'element-6066-11e4-a52e-4f735466cecf': '31000000-0000-0000-996B-000000000000'}], 
        'sessionId': 'BC8DE836-6F48-4F7B-B540-FCEC97C06068', 'status': 0}
    ```
    '''
    @pytest.mark.skip('NOT IMPLEMENTED: [GET] {{baseURL}}/session/{{sessionId}}/wda/element/{{uuid}}/getVisibleCells')
    def test_wda_element(self):
        self.app(text='ListView').click()
        ele: wda.Element = self.app(label='LIST_CONTAINER').get(timeout=1)
        visible_cells_response = ele.http.get(f'/wda/element/{ele.id}/getVisibleCells')


    '''
     Method: GET 
     Endpoint: {{baseURL}}/session/{{sessionId}}/element/active
    '''
    @pytest.mark.skip('NOT IMPLEMENTED: [GET] {{baseURL}}/session/{{sessionId}}/element/active')
    def test_wda_active(self):
        pass

'''
WDA DEBUG Command Testing
source code here: https://github.com/appium/WebDriverAgent/blob/master/WebDriverAgentLib/Commands/FBDebugCommands.m
WDA API document and example(not offical): https://documenter.getpostman.com/view/1837823/TVmMhJNB#a17feaf2-237e-4fe7-8e2f-75f132420d26
'''
import os
import pytest
import unittest
import jsonschema
import wda
from lxml import etree
from .constant import *

curPath = os.path.abspath(os.path.dirname(__file__))

#TODO : 更新断言在apprelease后

class TestDebug(unittest.TestCase):

    def setUp(self):
        self.under_test_bundle_id = UNDER_TEST_BUNDLE_ID
        self.wda_client: wda.Client = wda.Client()
        self.app = self.wda_client.session(bundle_id=self.under_test_bundle_id)

    def tearDown(self):
        self.wda_client.close()

    
    '''
    Method: GET 
    Endpoint: {{baseURL}}/source
    Description: Fetch the source tree (DOM) of the current page.
    '''
    def test_source(self):
        self.app(text='ListView').click()
        source_tree_xml_str: str = self.app.source()
        xml_bytes = source_tree_xml_str.encode('utf-8')
        self.assertTrue(etree.fromstring(xml_bytes))


    '''
    Method: GET 
    Endpoint: {{baseURL}}/wda/accessibleSource
    '''
    def test_accessible_source(self):
        self.app(text='ListView').click()
        source = self.app.source(accessible=True)
        self.assertIsInstance(source, dict)
        assert 'name' in source, "'name' field is missing"
        assert 'type' in source, "'type' field is missing"
        assert 'children' in source, "'children' field is missing"
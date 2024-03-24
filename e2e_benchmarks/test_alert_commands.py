'''
WDA ALERT Command Testing
source code here: https://github.com/appium/WebDriverAgent/blob/master/WebDriverAgentLib/Commands/FBAlertViewCommands.m
WDA API document and example(not offical): https://documenter.getpostman.com/view/1837823/TVmMhJNB#c6d397f5-8ece-4f2c-8bfd-26e798f83cf2
'''
import os
import pytest
import unittest
import wda
from .constant import *

curPath = os.path.abspath(os.path.dirname(__file__))


class TestAlert(unittest.TestCase):

    def setUp(self):
        self.under_test_bundle_id = UNDER_TEST_BUNDLE_ID
        self.wda_client: wda.Client = wda.Client()
        self.app = self.wda_client.session(bundle_id=self.under_test_bundle_id)

    def tearDown(self):
        self.wda_client.close()


    '''
    Method: GET 
    Endpoint: {{baseURL}}/alert/text
    Description: Get the content of the Alert (only the content, not including options), 
    an exception(wda.exceptions.WDARequestError) will be thrown if no Alert is present.
    '''

    def test_alert_text_endpoint_confirmation(self):
        self.app(label='ACCEPT_OR_REJECT_ALERT').click()
        self.assertEqual('Confirmation\nDo you accept?', self.wda_client.alert.text)
    
    def test_alert_text_endpoint_when_no_alert(self):
        with pytest.raises(wda.exceptions.WDARequestError,  match="status=110, value={'error': \'no such alert', "\
                           "'message': 'An attempt was made to operate on a modal dialog when one was not open'}"):
            self.wda_client.alert.text


    '''
    Method: POST
    Endpoint: {{baseURL}}/session/{{sessionId}}/alert/text
    '''
    def test_alert_text_input(self):
        with pytest.raises(wda.exceptions.WDARequestError,  match="status=110, value={'error': \'no such alert', "\
                           "'message': 'An attempt was made to operate on a modal dialog when one was not open'}"):
            self.wda_client.alert.set_text('hello world')


    '''1
    Method: GET 
    Endpoint: {{baseURL}}/session/{{sessionId}}/wda/alert/buttons
    Description: Get buttons for all prompt alert buttons.
    '''
    def test_alert_text_button_endpoint_value(self):
        self.app(label=ALERT_ENUMS.CONFIRM.value).click()
        self.assertEqual(['Reject', 'Accept'], self.wda_client.alert.buttons())


    '''
    Method: POST 
    Endpoint: {{baseURL}}/alert/dismiss
    Description: Dimiss the alert which display.
    '''
    def test_alert_text_dimiss_endpoint(self):
        self.app(label=ALERT_ENUMS.CONFIRM.value).click()
        self.app(text='Reject').get(timeout=1)
        self.wda_client.alert.dismiss()
        try:
            self.app(text='Reject').get(timeout=1)
        except wda.exceptions.WDAElementNotFoundError:
            return
        raise AssertionError('Alert not dismissed')


    '''
    Method: POST 
    Endpoint: {{baseURL}}/alert/accept
    Description: Accept the alert which display.
    '''
    def test_alert_text_accept_endpoint(self):
        self.app(label=ALERT_ENUMS.CONFIRM.value).click()
        self.app.alert.accept()
        try:
            self.app(text='Accept').get(timeout=1)
        except wda.exceptions.WDAElementNotFoundError:
            return
        raise AssertionError('Alert not dismissed')

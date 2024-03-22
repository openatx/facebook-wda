'''
WDA Element Command Testing
source code here: https://github.com/appium/WebDriverAgent/blob/master/WebDriverAgentLib/Commands/FBElementCommands.m
WDA API document and example(not offical): https://documenter.getpostman.com/view/1837823/TVmMhJNB#f68f7fd9-3a08-4a0b-9253-f1bedf0ae926
'''
import os
import pytest
import unittest
import wda
from .constant import *

curPath = os.path.abspath(os.path.dirname(__file__))


class TestElement(unittest.TestCase):

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
     Endpoint: {{baseURL}}/session/{{sessionId}}/window/size
     Description: Fetch device window size.
    '''
    def test_window_size(self):
         assert hasattr(self.app.window_size(), 'width') and type(self.app.window_size().width) == int
         assert hasattr(self.app.window_size(), 'height') and type(self.app.window_size().height) == int


    '''
     Method: GET 
     Endpoint: {{baseURL}}/session/{{sessionId}}/element/{{uuid}}/enabled
     Description: Check element is enbaled or not.
    '''
    def test_btn_enable(self):
        assert self.app(text='ENABLED_BTN').enabled == True

    def test_btn_enable(self):
        assert self.app(text='DISABLED_BTN').enabled == False


    '''
     Method: GET 
     Endpoint: {{baseURL}}/session/{{sessionId}}/element/{{uuid}}/rect
    '''
    def test_rect(self):
        rect = self.app(text='ENABLED_BTN').bounds
        assert all([
            hasattr(rect, 'x') and type(rect.x) == int,
            hasattr(rect, 'y') and type(rect.y) == int,
            hasattr(rect, 'width') and type(rect.width) == int,
            hasattr(rect, 'height') and type(rect.height) == int,
        ])


    '''
     Method: GET 
     Endpoint: {{baseURL}}/session/{{sessionId}}/element/{{uuid}}/attribute/{{attribute_name}}
    '''
    def test_attribute_label(self):
        self.assertEqual(self.app(text='ENABLED_BTN').label, 'ENABLED_BTN')

    def test_attribute_invild(self):
        with pytest.raises(AttributeError, match="'Element' object has no attribute 'attribute'"):
            self.app(text='ENABLED_BTN').attribute('invalid_attribute_name')


    '''
     Method: GET 
     Endpoint: {{baseURL}}/session/{{sessionId}}/element/{{uuid}}/text
    '''
    def test_attribute_btn_text(self):
        self.assertEqual(self.app(text='ENABLED_BTN').text, 'ENABLED_BTN')

    def test_attribute_image_text(self):
        self.assertEqual(self.app(id='IMG_BTN').text, 'applogo')


    '''
     Method: GET 
     Endpoint: {{baseURL}}/session/{{sessionId}}/element/{{uuid}}/displayed
    '''
    def test_attribute_btn_displayed(self):
        self.assertEqual(self.app(text='ENABLED_BTN').displayed, True)

    def test_attribute_btn_not_displayed(self):
        self.assertEqual(self.app(text='HIDDEN_BTN').displayed, False)


    '''
     Method: GET 
     Endpoint: {{baseURL}}/session/{{sessionId}}/element/{{uuid}}/selected
    '''
    def test_btn_selected(self):
        self.assertEqual(self.app(text='CHECKED_BTN').selected(), True)

    def test_attribute_btn_not_displayed(self):
        self.assertEqual(self.app(text='UNCHECKED_BTN').selected(), False)


    '''
     Method: GET 
     Endpoint: {{baseURL}}/session/{{sessionId}}/element/{{uuid}}/name
     NOTE: Return element type.
    '''
    def test_btn_name(self):
        self.assertEqual(self.app(text='CHECKED_BTN').name, 'XCUIElementTypeButton')

    def test_img_name(self):
        self.assertEqual(self.app(text='IMG_BTN').name, 'XCUIElementTypeImage')


    '''
     Method: POST 
     Endpoint: {{baseURL}}/session/{{sessionId}}/element/{{uuid}}/value
    '''
    def test_input_text(self):
        self.app(id='INPUT_FIELD').set_text('test')
        self.assertEqual(self.app(id='INPUT_FIELD').value, 'test')


    '''
     Method: POST 
     Endpoint: {{baseURL}}/session/{{sessionId}}/element/{{uuid}}/click
    '''
    def test_input_click(self):
        input_text_val = 'test'
        self.app(id='INPUT_FIELD').set_text(input_text_val)
        assert self.app(id='INPUT_FIELD').value == input_text_val
        self.app(id='CLEAR_INPUT_BTN').click()
        assert self.app(id='INPUT_FIELD').value != input_text_val


    '''
     Method: POST 
     Endpoint: {{baseURL}}/session/{{sessionId}}/element/{{uuid}}/clear
    '''
    def test_input_clear(self):
        input_text_val = 'test'
        self.app(id='INPUT_FIELD').set_text(input_text_val)
        assert self.app(id='INPUT_FIELD').value == input_text_val
        self.app(id='INPUT_FIELD').clear_text()
        assert self.app(id='INPUT_FIELD').value != input_text_val


    '''
     Method: POST 
     Endpoint: {{baseURL}}/session/{{sessionId}}/element/{{uuid}}/screenshot
    '''
    def test_screenshot(self):
        self.app.screenshot(png_filename=self.temp_file_pic)
        assert os.path.exists(self.temp_file_pic)


    '''
     Method: POST 
     Endpoint: {{baseURL}}/session/{{sessionId}}/screenshot/{{uuid}}
     Description: screenshot for target element.
    '''
    @pytest.mark.skip('NOT IMPLEMENTED: [POST] {{baseURL}}/session/{{sessionId}}/screenshot/{{uuid}}')
    def test_screenshot_element(self):
        pass


    '''
     Method: POST 
     Endpoint: {{baseURL}}/session/{{sessionId}}/wda/element/{{uuid}}/accessible
    '''
    def test_ele_accessible_is_false(self):
        self.assertFalse(self.app(text='HIDDEN_BTN').accessible)

    def test_ele_accessible_is_true(self):
        self.assertTrue(self.app(text='ENABLED_BTN').accessible)


    '''
    Method: POST 
    Endpoint: {{baseURL}}/session/{{sessionId}}/wda/element/{{uuid}}/accessibilityContainer
    NOTE Swift accessibility Container is not useful, always return false.
    
    Example:
    ```
    import SwiftUI

    struct ContentView: View {
        var body: some View {
            HStack {
                Text("First Item")
                Divider()
                Text("Second Item")
            }
            .accessibilityElement(children: .combine)
            .accessibility(label: Text("Combined Items"))
        }
    }

    struct ContentView_Previews: PreviewProvider {
        static var previews: some View {
            ContentView()
        }
    }
    ```
    '''
    @pytest.mark.skip('WDA API NOT USEFUL: Not use in SwiftUI.')
    def test_ele_accessibilityContainer_is_true(self):
        self.assertFalse(self.app(id='Combined Items').accessibility_container)

    def test_ele_accessibilityContainer_is_false(self):
        self.assertFalse(self.app(id='ENABLED_BTN').accessibility_container)


    '''
    Method: POST 
    Endpoint: {{baseURL}}/session/{{sessionId}}/wda/element/{{uuid}}/swipe
    '''
    @pytest.mark.skip('NOT IMPLEMENTED')
    def test_ele_swipe_top(self):
        self.app(text="Go to List").click()
        self.app(text="Row1").click()


    '''
    Method: POST 
    Endpoint: {{baseURL}}/session/{{sessionId}}/wda/element/{{uuid}}/pinch
    '''
    @pytest.mark.skip('NOT IMPLEMENTED: [POST] {{baseURL}}/session/{{sessionId}}/wda/element/{{uuid}}/pinch')
    def test_pinch(self):
        ...


    '''
     Method: POST 
     Endpoint: {{baseURL}}/session/{{sessionId}}/wda/element/{{uuid}}/touchAndHold
    '''
    def test_touch_and_hold(self):
        try:
            self.app(text='OK').get(timeout=1)
        except wda.exceptions.WDAElementNotFoundError:
            pass
        self.app(text='LONG_TAP_ALERT').tap_hold(duration=2)
        self.assertTrue(self.app(text='LONG_TAP_ALERT_OK').get(timeout=1).displayed) 


    '''
     Method: POST 
     Endpoint: {{baseURL}}/session/{{sessionId}}/wda/element/{{uuid}}/dragfromtoforduration
    '''
    @pytest.mark.skip('NOT IMPLEMENTED: [POST] {{baseURL}}/session/{{sessionId}}/wda/element/{{uuid}}/dragfromtoforduration')
    def test_drag_from_to_for_duration(self):
      pass


    '''
    Method: POST 
    Endpoint: {{baseURL}}/session/{{sessionId}}/wda/dragfromtoforduration
    '''
    def test_app_drag_from_to_for_duration(self):
        self.app(text='ListView').click()
        self.assertTrue(self.app(text='Row1').get(timeout=1).displayed) 
        try:
            self.app(text='Row30').get(timeout=1)
        except wda.exceptions.WDAElementNotFoundError:
            pass
        self.app.swipe(500, 800, 500, 200, duration=0.5)
        self.assertTrue(self.app(text='Row30').get(timeout=1).displayed) 


    '''
     Method: POST 
     Endpoint: {{baseURL}}/session/{{sessionId}}/wda/pickerwheel/{{uuid}}/select
    '''
    @pytest.mark.skip('NOT IMPLEMENTED: [POST] {{baseURL}}/session/{{sessionId}}/wda/pickerwheel/{{uuid}}/select')
    def test_ele_select(self):
        pass


    '''
     Method: POST 
     Endpoint: {{baseURL}}/session/{{sessionId}}/wda/keys
    '''
    def test_wda_keys(self):
        self.app(text='INPUT_FIELD').click()
        self.app.send_keys('hello world')
        self.assertEqual(self.app(text='INPUT_FIELD').value, 'hello world')


    '''
     Method: POST 
     Endpoint: {{baseURL}}/session/{{sessionId}}/wda/element/{{uuid}}/forceTouch
    '''
    @pytest.mark.skip('NOT IMPLEMENTED: [POST] {{baseURL}}/session/{{sessionId}}/wda/element/{{uuid}}/forceTouch')
    def test_ele_force_touch(self):
        pass


    '''
     Method: POST 
     Endpoint: {{baseURL}}/session/{{sessionId}}/wda/doubleTap
    '''
    def test_ele_touble_tap(self):
        bounds = self.app(text='DOUBLE_TAP_ALERT').bounds
        x = int(bounds.x + bounds.width * 0.5)
        y = int(bounds.y + bounds.height * 0.5)
        self.app.double_tap(x, y)
        self.assertTrue(self.app(text='DOUBLE_TAP_ALERT_OK').get(timeout=1).displayed)


    '''
     Method: POST 
     Endpoint: {{baseURL}}/session/{{sessionId}}/wda/touchAndHold
    '''
    def test_wda_touch_and_hold(self):
        bounds = self.app(text='LONG_TAP_ALERT').bounds
        x = int(bounds.x + bounds.width * 0.5)
        y = int(bounds.y + bounds.height * 0.5)
        self.app.tap_hold(x, y, duration=2)
        self.assertTrue(self.app(text='LONG_TAP_ALERT_OK').get(timeout=1).displayed)

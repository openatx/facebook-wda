# WDA Server And Client Benchmark E2E Testing Report (V7.1.1)

## Overview
61 passed, 17 skipped, 1 warning in 173.98s (0:02:53) 

## 1. Test Environments
- WDA Version: [version 7.1.1 release by Appium.](https://github.com/appium/WebDriverAgent/releases/tag/v7.1.1)
- Platform: iPhone 13 Pro (iOS 16.3.1)

## 2. Test Results
platform darwin -- Python 3.7.9, pytest-7.4.4, pluggy-1.2.0

collected 78 items                                                                                                                                                                     

e2e_benchmarks/test_alert_commands.py::TestAlert::test_alert_text_accept_endpoint PASSED                                                                                         [  1%]
e2e_benchmarks/test_alert_commands.py::TestAlert::test_alert_text_button_endpoint_value PASSED                                                                                   [  2%]
e2e_benchmarks/test_alert_commands.py::TestAlert::test_alert_text_dimiss_endpoint PASSED                                                                                         [  3%]
e2e_benchmarks/test_alert_commands.py::TestAlert::test_alert_text_endpoint_confirmation PASSED                                                                                   [  5%]
e2e_benchmarks/test_alert_commands.py::TestAlert::test_alert_text_endpoint_when_no_alert PASSED                                                                                  [  6%]
e2e_benchmarks/test_alert_commands.py::TestAlert::test_alert_text_input PASSED                                                                                                   [  7%]
e2e_benchmarks/test_custom_commands.py::TestDevice::test_active_app_info PASSED                                                                                                  [  8%]
e2e_benchmarks/test_custom_commands.py::TestDevice::test_battery_info PASSED                                                                                                     [ 10%]
e2e_benchmarks/test_custom_commands.py::TestDevice::test_deactivate_app PASSED                                                                                                   [ 11%]
e2e_benchmarks/test_custom_commands.py::TestDevice::test_device_info PASSED                                                                                                      [ 12%]
e2e_benchmarks/test_custom_commands.py::TestDevice::test_get_paste_board SKIPPED (WDA API NOT USEFUL: {{baseURL}}/session/{{sessionId}}/wda/getPasteboard)                       [ 14%]
e2e_benchmarks/test_custom_commands.py::TestDevice::test_homescreen PASSED                                                                                                       [ 15%]
e2e_benchmarks/test_custom_commands.py::TestDevice::test_keybord_dismiss PASSED                                                                                                  [ 16%]
e2e_benchmarks/test_custom_commands.py::TestDevice::test_keybord_lock_and_unlock PASSED                                                                                          [ 17%]
e2e_benchmarks/test_custom_commands.py::TestDevice::test_locked PASSED                                                                                                           [ 19%]
e2e_benchmarks/test_custom_commands.py::TestDevice::test_scale PASSED                                                                                                            [ 20%]
e2e_benchmarks/test_custom_commands.py::TestDevice::test_set_paste_board PASSED                                                                                                  [ 21%]
e2e_benchmarks/test_custom_commands.py::TestDevice::test_timeouts PASSED                                                                                                         [ 23%]
e2e_benchmarks/test_debug_commands.py::TestDebug::test_accessible_source PASSED                                                                                                  [ 24%]
e2e_benchmarks/test_debug_commands.py::TestDebug::test_source PASSED                                                                                                             [ 25%]
e2e_benchmarks/test_element_commands.py::TestElement::test_app_drag_from_to_for_duration PASSED                                                                                  [ 26%]
e2e_benchmarks/test_element_commands.py::TestElement::test_attribute_btn_displayed PASSED                                                                                        [ 28%]
e2e_benchmarks/test_element_commands.py::TestElement::test_attribute_btn_not_displayed PASSED                                                                                    [ 29%]
e2e_benchmarks/test_element_commands.py::TestElement::test_attribute_btn_text PASSED                                                                                             [ 30%]
e2e_benchmarks/test_element_commands.py::TestElement::test_attribute_image_text PASSED                                                                                           [ 32%]
e2e_benchmarks/test_element_commands.py::TestElement::test_attribute_invild PASSED                                                                                               [ 33%]
e2e_benchmarks/test_element_commands.py::TestElement::test_attribute_label PASSED                                                                                                [ 34%]
e2e_benchmarks/test_element_commands.py::TestElement::test_btn_enable PASSED                                                                                                     [ 35%]
e2e_benchmarks/test_element_commands.py::TestElement::test_btn_name PASSED                                                                                                       [ 37%]
e2e_benchmarks/test_element_commands.py::TestElement::test_btn_selected PASSED                                                                                                   [ 38%]
e2e_benchmarks/test_element_commands.py::TestElement::test_drag_from_to_for_duration SKIPPED (NOT IMPLEMENTED: [POST] {{baseURL}}/session/{{sessionId}}/wda/element/{{uuid}}...) [ 39%]
e2e_benchmarks/test_element_commands.py::TestElement::test_ele_accessibilityContainer_is_false PASSED                                                                            [ 41%]
e2e_benchmarks/test_element_commands.py::TestElement::test_ele_accessibilityContainer_is_true SKIPPED (WDA API NOT USEFUL: Not use in SwiftUI.)                                  [ 42%]
e2e_benchmarks/test_element_commands.py::TestElement::test_ele_accessible_is_false PASSED                                                                                        [ 43%]
e2e_benchmarks/test_element_commands.py::TestElement::test_ele_accessible_is_true PASSED                                                                                         [ 44%]
e2e_benchmarks/test_element_commands.py::TestElement::test_ele_force_touch SKIPPED (NOT IMPLEMENTED: [POST] {{baseURL}}/session/{{sessionId}}/wda/element/{{uuid}}/forceTouch)   [ 46%]
e2e_benchmarks/test_element_commands.py::TestElement::test_ele_select SKIPPED (NOT IMPLEMENTED: [POST] {{baseURL}}/session/{{sessionId}}/wda/pickerwheel/{{uuid}}/select)        [ 47%]
e2e_benchmarks/test_element_commands.py::TestElement::test_ele_swipe_top SKIPPED (NOT IMPLEMENTED)                                                                               [ 48%]
e2e_benchmarks/test_element_commands.py::TestElement::test_ele_touble_tap PASSED                                                                                                 [ 50%]
e2e_benchmarks/test_element_commands.py::TestElement::test_img_name PASSED                                                                                                       [ 51%]
e2e_benchmarks/test_element_commands.py::TestElement::test_input_clear PASSED                                                                                                    [ 52%]
e2e_benchmarks/test_element_commands.py::TestElement::test_input_click PASSED                                                                                                    [ 53%]
e2e_benchmarks/test_element_commands.py::TestElement::test_input_text PASSED                                                                                                     [ 55%]
e2e_benchmarks/test_element_commands.py::TestElement::test_pinch SKIPPED (NOT IMPLEMENTED: [POST] {{baseURL}}/session/{{sessionId}}/wda/element/{{uuid}}/pinch)                  [ 56%]
e2e_benchmarks/test_element_commands.py::TestElement::test_rect PASSED                                                                                                           [ 57%]
e2e_benchmarks/test_element_commands.py::TestElement::test_screenshot PASSED                                                                                                     [ 58%]
e2e_benchmarks/test_element_commands.py::TestElement::test_screenshot_element SKIPPED (NOT IMPLEMENTED: [POST] {{baseURL}}/session/{{sessionId}}/screenshot/{{uuid}})            [ 60%]
e2e_benchmarks/test_element_commands.py::TestElement::test_touch_and_hold PASSED                                                                                                 [ 61%]
e2e_benchmarks/test_element_commands.py::TestElement::test_wda_keys PASSED                                                                                                       [ 62%]
e2e_benchmarks/test_element_commands.py::TestElement::test_wda_touch_and_hold PASSED                                                                                             [ 64%]
e2e_benchmarks/test_element_commands.py::TestElement::test_window_size PASSED                                                                                                    [ 65%]
e2e_benchmarks/test_find_element_commands.py::TestFindElement::test_ele_elements SKIPPED (NOT IMPLEMENTED: [GET] /session/{{sessionId}}/element/{{uuid}}/elements)               [ 66%]
e2e_benchmarks/test_find_element_commands.py::TestFindElement::test_element_ids PASSED                                                                                           [ 67%]
e2e_benchmarks/test_find_element_commands.py::TestFindElement::test_elements PASSED                                                                                              [ 69%]
e2e_benchmarks/test_find_element_commands.py::TestFindElement::test_wda_active SKIPPED (NOT IMPLEMENTED: [GET] {{baseURL}}/session/{{sessionId}}/element/active)                 [ 70%]
e2e_benchmarks/test_find_element_commands.py::TestFindElement::test_wda_element SKIPPED (NOT IMPLEMENTED: [GET] {{baseURL}}/session/{{sessionId}}/wda/element/{{uuid}}/getVi...) [ 71%]
e2e_benchmarks/test_orientation_commands.py::TestOrientation::test_get_rotation SKIPPED (NOT IMPLEMENTED: [GET] {{baseURL}}/session/{{sessionId}}/rotation)                      [ 73%]
e2e_benchmarks/test_orientation_commands.py::TestOrientation::test_orientation PASSED                                                                                            [ 74%]
e2e_benchmarks/test_orientation_commands.py::TestOrientation::test_set_orientation PASSED                                                                                        [ 75%]
e2e_benchmarks/test_orientation_commands.py::TestOrientation::test_set_rotation SKIPPED (NOT IMPLEMENTED: [POST] {{baseURL}}/session/{{sessionId}}/rotation)                     [ 76%]
e2e_benchmarks/test_screenshot_commands.py::TestScreenshot::test_screenshot PASSED                                                                                               [ 78%]
e2e_benchmarks/test_session_commands.py::TestSessionCommands::test_app_activate PASSED                                                                                           [ 79%]
e2e_benchmarks/test_session_commands.py::TestSessionCommands::test_app_list PASSED                                                                                               [ 80%]
e2e_benchmarks/test_session_commands.py::TestSessionCommands::test_app_state PASSED                                                                                              [ 82%]
e2e_benchmarks/test_session_commands.py::TestSessionCommands::test_app_terminate PASSED                                                                                          [ 83%]
e2e_benchmarks/test_session_commands.py::TestSessionCommands::test_appium_settings PASSED                                                                                        [ 84%]
e2e_benchmarks/test_session_commands.py::TestSessionCommands::test_create_session_id PASSED                                                                                      [ 85%]
e2e_benchmarks/test_session_commands.py::TestSessionCommands::test_delete_session PASSED                                                                                         [ 87%]
e2e_benchmarks/test_session_commands.py::TestSessionCommands::test_health SKIPPED (NOT IMPLEMENTED: [GET] {{baseURL}}/health)                                                    [ 88%]
e2e_benchmarks/test_session_commands.py::TestSessionCommands::test_health_check PASSED                                                                                           [ 89%]
e2e_benchmarks/test_session_commands.py::TestSessionCommands::test_health_check_has_session_id PASSED                                                                            [ 91%]
e2e_benchmarks/test_session_commands.py::TestSessionCommands::test_launch_app PASSED                                                                                             [ 92%]
e2e_benchmarks/test_session_commands.py::TestSessionCommands::test_session_info SKIPPED (NOT IMPLEMENTED: [GET] {{baseURL}}/session/{{sessionId}})                               [ 93%]
e2e_benchmarks/test_session_commands.py::TestSessionCommands::test_status_command_return_schema PASSED                                                                           [ 94%]
e2e_benchmarks/test_session_commands.py::TestSessionCommands::test_status_command_state_and_ready PASSED                                                                         [ 96%]
e2e_benchmarks/test_session_commands.py::TestSessionCommands::test_unknow_app_state PASSED                                                                                       [ 97%]
e2e_benchmarks/test_session_commands.py::TestSessionCommands::test_url SKIPPED (UNKNOW HOW TO TEST: [POST] {{baseURL}}/session/{{sessionId}}/url)                                [ 98%]
e2e_benchmarks/test_session_commands.py::TestSessionCommands::test_wda_shutdown SKIPPED (NOT IMPLEMENTED: [GET] {{baseURL}}/wda/shutdown)                                        [100%]

=================================================================================== warnings summary ===================================================================================
e2e_benchmarks/test_debug_commands.py::TestDebug::test_source
  /Library/Frameworks/Python.framework/Versions/3.7/lib/python3.7/unittest/case.py:703: FutureWarning: The behavior of this method will change in future versions. Use specific 'len(elem)' or 'elem is not None' test instead.
    if not expr:

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=============================================================================== short test summary info ================================================================================
SKIPPED [1] e2e_benchmarks/test_custom_commands.py:127: WDA API NOT USEFUL: {{baseURL}}/session/{{sessionId}}/wda/getPasteboard
SKIPPED [1] e2e_benchmarks/test_element_commands.py:256: NOT IMPLEMENTED: [POST] {{baseURL}}/session/{{sessionId}}/wda/element/{{uuid}}/dragfromtoforduration
SKIPPED [1] e2e_benchmarks/test_element_commands.py:212: WDA API NOT USEFUL: Not use in SwiftUI.
SKIPPED [1] e2e_benchmarks/test_element_commands.py:299: NOT IMPLEMENTED: [POST] {{baseURL}}/session/{{sessionId}}/wda/element/{{uuid}}/forceTouch
SKIPPED [1] e2e_benchmarks/test_element_commands.py:280: NOT IMPLEMENTED: [POST] {{baseURL}}/session/{{sessionId}}/wda/pickerwheel/{{uuid}}/select
SKIPPED [1] e2e_benchmarks/test_element_commands.py:224: NOT IMPLEMENTED
SKIPPED [1] e2e_benchmarks/test_element_commands.py:234: NOT IMPLEMENTED: [POST] {{baseURL}}/session/{{sessionId}}/wda/element/{{uuid}}/pinch
SKIPPED [1] e2e_benchmarks/test_element_commands.py:168: NOT IMPLEMENTED: [POST] {{baseURL}}/session/{{sessionId}}/screenshot/{{uuid}}
SKIPPED [1] e2e_benchmarks/test_find_element_commands.py:51: NOT IMPLEMENTED: [GET] /session/{{sessionId}}/element/{{uuid}}/elements
SKIPPED [1] e2e_benchmarks/test_find_element_commands.py:87: NOT IMPLEMENTED: [GET] {{baseURL}}/session/{{sessionId}}/element/active
SKIPPED [1] e2e_benchmarks/test_find_element_commands.py:76: NOT IMPLEMENTED: [GET] {{baseURL}}/session/{{sessionId}}/wda/element/{{uuid}}/getVisibleCells
SKIPPED [1] e2e_benchmarks/test_orientation_commands.py:54: NOT IMPLEMENTED: [GET] {{baseURL}}/session/{{sessionId}}/rotation
SKIPPED [1] e2e_benchmarks/test_orientation_commands.py:63: NOT IMPLEMENTED: [POST] {{baseURL}}/session/{{sessionId}}/rotation
SKIPPED [1] e2e_benchmarks/test_session_commands.py:256: NOT IMPLEMENTED: [GET] {{baseURL}}/health
SKIPPED [1] e2e_benchmarks/test_session_commands.py:140: NOT IMPLEMENTED: [GET] {{baseURL}}/session/{{sessionId}}
SKIPPED [1] e2e_benchmarks/test_session_commands.py:33: UNKNOW HOW TO TEST: [POST] {{baseURL}}/session/{{sessionId}}/url
SKIPPED [1] e2e_benchmarks/test_session_commands.py:247: NOT IMPLEMENTED: [GET] {{baseURL}}/wda/shutdown
================================================================ 61 passed, 17 skipped, 1 warning in 173.98s (0:02:53) =================================================================
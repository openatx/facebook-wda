# WDA Server And Client Benchmark E2E Testing Report (V7.1.1)

## 1. Test Environments
- WDA Version: [version 7.1.1 release by Appium.](https://github.com/appium/WebDriverAgent/releases/tag/v7.1.1)
- Platform: iPhone 12 Pro Max (iOS 16.3.1)

## 2. Test Results
platform darwin -- Python 3.7.9, pytest-7.4.4, pluggy-1.2.0

| File | Test Method | Result |
|------|-------------|--------|
| `test_alert_commands.py` | `TestAlert::test_alert_text_accept_endpoint` | <span style="color: #90EE90;">PASSED</span> |
| `test_alert_commands.py` | `TestAlert::test_alert_text_button_endpoint_value` | <span style="color: #90EE90;">PASSED</span> |
| `test_alert_commands.py` | `TestAlert::test_alert_text_dimiss_endpoint` | <span style="color: #90EE90;">PASSED</span> |
| `test_alert_commands.py` | `TestAlert::test_alert_text_endpoint_confirmation` | <span style="color: #90EE90;">PASSED</span> |
| `test_alert_commands.py` | `TestAlert::test_alert_text_endpoint_when_no_alert` | <span style="color: #90EE90;">PASSED</span> |
| `test_alert_commands.py` | `TestAlert::test_alert_text_input` | <span style="color: yellow;">SKIPPED (NOT IMPLEMENTED)</span> |
| `test_custom_commands.py` | `TestDevice::test_active_app_info` | <span style="color: #90EE90;">PASSED</span> |
| `test_custom_commands.py` | `TestDevice::test_battery_info` | <span style="color: #90EE90;">PASSED</span> |
| `test_custom_commands.py` | `TestDevice::test_deactivate_app` | <span style="color: #90EE90;">PASSED</span> |
| `test_custom_commands.py` | `TestDevice::test_device_info` | <span style="color: #90EE90;">PASSED</span> |
| `test_custom_commands.py` | `TestDevice::test_get_paste_board` | <span style="color: yellow;">SKIPPED (WDA API NOT USEFUL)</span> |
| `test_custom_commands.py` | `TestDevice::test_homescreen` | <span style="color: #90EE90;">PASSED</span> |
| `test_custom_commands.py` | `TestDevice::test_keybord_dismiss` | <span style="color: #90EE90;">PASSED</span> |
| `test_custom_commands.py` | `TestDevice::test_keybord_lock_and_unlock` | <span style="color: #90EE90;">PASSED</span> |
| `test_custom_commands.py` | `TestDevice::test_locked` | <span style="color: #90EE90;">PASSED</span> |
| `test_custom_commands.py` | `TestDevice::test_scale` | <span style="color: #90EE90;">PASSED</span> |
| `test_custom_commands.py` | `TestDevice::test_set_paste_board` | <span style="color: #90EE90;">PASSED</span> |
| `test_debug_commands.py` | `TestDebug::test_accessible_source` | <span style="color: #90EE90;">PASSED</span> |
| `test_debug_commands.py` | `TestDebug::test_source` | <span style="color: #90EE90;">PASSED</span> |
| `test_element_commands.py` | `TestElement::test_app_drag_from_to_for_duration` | <span style="color: #90EE90;">PASSED</span> |
| `test_element_commands.py` | `TestElement::test_attribute_btn_displayed` | <span style="color: #90EE90;">PASSED</span> |
| `test_element_commands.py` | `TestElement::test_attribute_btn_not_displayed` | <span style="color: #90EE90;">PASSED</span> |
| `test_element_commands.py` | `TestElement::test_attribute_btn_text` | <span style="color: #90EE90;">PASSED</span> |
| `test_element_commands.py` | `TestElement::test_attribute_image_text` | <span style="color: #90EE90;">PASSED</span> |
| `test_element_commands.py` | `TestElement::test_attribute_invild` | <span style="color: #90EE90;">PASSED</span> |
| `test_element_commands.py` | `TestElement::test_attribute_label` | <span style="color: #90EE90;">PASSED</span> |
| `test_element_commands.py` | `TestElement::test_btn_enable` | <span style="color: #90EE90;">PASSED</span> |
| `test_element_commands.py` | `TestElement::test_btn_name` | <span style="color: #90EE90;">PASSED</span> |
| `test_element_commands.py` | `TestElement::test_btn_selected` | <span style="color: #90EE90;">PASSED</span> |
| `test_element_commands.py` | `TestElement::test_drag_from_to_for_duration` | <span style="color: yellow;">SKIPPED (NOT IMPLEMENTED)</span> |
| `test_element_commands.py` | `TestElement::test_ele_accessibilityContainer_is_false` | <span style="color: #90EE90;">PASSED</span> |
| `test_element_commands.py` | `TestElement::test_ele_accessibilityContainer_is_true` | <span style="color: yellow;">SKIPPED (WDA API NOT USEFUL)</span> |
| `test_element_commands.py` | `TestElement::test_ele_accessible_is_false` | <span style="color: #90EE90;">PASSED</span> |
| `test_element_commands.py` | `TestElement::test_ele_accessible_is_true` | <span style="color: #90EE90;">PASSED</span> |
| `test_element_commands.py` | `TestElement::test_ele_force_touch` | <span style="color: yellow;">SKIPPED (NOT IMPLEMENTED)</span> |
| `test_element_commands.py` | `TestElement::test_ele_select` | <span style="color: yellow;">SKIPPED (NOT IMPLEMENTED)</span> |
| `test_element_commands.py` | `TestElement::test_ele_swipe_top` | <span style="color: yellow;">SKIPPED (NOT IMPLEMENTED)</span> |
| `test_element_commands.py` | `TestElement::test_ele_touble_tap` | <span style="color: #90EE90;">PASSED</span> |
| `test_element_commands.py` | `TestElement::test_img_name` | <span style="color: #90EE90;">PASSED</span> |
| `test_element_commands.py` | `TestElement::test_input_clear` | <span style="color: #90EE90;">PASSED</span> |
| `test_element_commands.py` | `TestElement::test_input_click` | <span style="color: #90EE90;">PASSED</span> |
| `test_element_commands.py` | `TestElement::test_input_text` | <span style="color: #90EE90;">PASSED</span> |
| `test_element_commands.py` | `TestElement::test_pinch` | <span style="color: yellow;">SKIPPED (NOT IMPLEMENTED)</span> |
| `test_element_commands.py` | `TestElement::test_rect` | <span style="color: #90EE90;">PASSED</span> |
| `test_element_commands.py` | `TestElement::test_screenshot` | <span style="color: #90EE90;">PASSED</span> |
| `test_element_commands.py` | `TestElement::test_screenshot_element` | <span style="color: yellow;">SKIPPED (NOT IMPLEMENTED)</span> |
| `test_element_commands.py` | `TestElement::test_touch_and_hold` | <span style="color: #90EE90;">PASSED</span> |
| `test_element_commands.py` | `TestElement::test_wda_keys` | <span style="color: #90EE90;">PASSED</span> |
| `test_element_commands.py` | `TestElement::test_wda_touch_and_hold` | <span style="color: #90EE90;">PASSED</span> |
| `test_element_commands.py` | `TestElement::test_window_size` | <span style="color: #90EE90;">PASSED</span> |
| `test_find_element_commands.py` | `TestFindElement::test_ele_elements` | <span style="color: yellow;">SKIPPED (NOT IMPLEMENTED)</span> |
| `test_find_element_commands.py` | `TestFindElement::test_element_ids` | <span style="color: #90EE90;">PASSED</span> |
| `test_find_element_commands.py` | `TestFindElement::test_elements` | <span style="color: #90EE90;">PASSED</span> |
| `test_find_element_commands.py` | `TestFindElement::test_wda_active` | <span style="color: yellow;">SKIPPED (NOT IMPLEMENTED)</span> |
| `test_find_element_commands.py` | `TestFindElement::test_wda_element` | <span style="color: yellow;">SKIPPED (NOT IMPLEMENTED)</span> |
| `test_orientation_commands.py` | `TestOrientation::test_get_rotation` | <span style="color: yellow;">SKIPPED (NOT IMPLEMENTED)</span> |
| `test_orientation_commands.py` | `TestOrientation::test_orientation` | <span style="color: #90EE90;">PASSED</span> |
| `test_orientation_commands.py` | `TestOrientation::test_set_rotation` | <span style="color: yellow;">SKIPPED (NOT IMPLEMENTED)</span> |
| `test_screenshot_commands.py` | `TestScreenshot::test_screenshot` | <span style="color: #90EE90;">PASSED</span> |
| `test_session_commands.py` | `TestSessionCommands::test_app_activate` | <span style="color: #90EE90;">PASSED</span> |
| `test_session_commands.py` | `TestSessionCommands::test_app_list` | <span style="color: #90EE90;">PASSED</span> |
| `test_session_commands.py` | `TestSessionCommands::test_app_state` | <span style="color: #90EE90;">PASSED</span> |
| `test_session_commands.py` | `TestSessionCommands::test_app_terminate` | <span style="color: #90EE90;">PASSED</span> |
| `test_session_commands.py` | `TestSessionCommands::test_appium_settings` | <span style="color: #90EE90;">PASSED</span> |
| `test_session_commands.py` | `TestSessionCommands::test_create_session_id` | <span style="color: #90EE90;">PASSED</span> |
| `test_session_commands.py` | `TestSessionCommands::test_delete_session` | <span style="color: #90EE90;">PASSED</span> |
| `test_session_commands.py` | `TestSessionCommands::test_health` | <span style="color: yellow;">SKIPPED (NOT IMPLEMENTED)</span> |
| `test_session_commands.py` | `TestSessionCommands::test_health_check` | <span style="color: #90EE90;">PASSED</span> |
| `test_session_commands.py` | `TestSessionCommands::test_health_check_has_session_id` | <span style="color: #90EE90;">PASSED</span> |
| `test_session_commands.py` | `TestSessionCommands::test_launch_app` | <span style="color: #90EE90;">PASSED</span> |
| `test_session_commands.py` | `TestSessionCommands::test_session_info` | <span style="color: yellow;">SKIPPED (NOT IMPLEMENTED)</span> |
| `test_session_commands.py` | `TestSessionCommands::test_status_command_return_schema` | <span style="color: #90EE90;">PASSED</span> |
| `test_session_commands.py` | `TestSessionCommands::test_status_command_state_and_ready` | <span style="color: #90EE90;">PASSED</span> |
| `test_session_commands.py` | `TestSessionCommands::test_unknow_app_state` | <span style="color: #90EE90;">PASSED</span> |
| `test_session_commands.py` | `TestSessionCommands::test_url` | <span style="color: yellow;">SKIPPED (UNKNOW HOW TO TEST)</span> |
| `test_session_commands.py` | `TestSessionCommands::test_wda_shutdown` | <span style="color: yellow;">SKIPPED (NOT IMPLEMENTED)</span> |

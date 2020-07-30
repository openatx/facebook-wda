#

__all__ = ['AppiumSettings', 'AlertAction']


import enum

class AppiumSettings(str, enum.Enum):
    """
    {'boundElementsByIndex': False,
    'shouldUseCompactResponses': True,
    'mjpegServerFramerate': 10,
    'snapshotMaxDepth': 50,
    'screenshotOrientation': 'auto',
    'activeAppDetectionPoint': '64.00,64.00',
    'acceptAlertButtonSelector': '',
    'snapshotTimeout': 15,
    'elementResponseAttributes': 'type,label',
    'keyboardPrediction': 0,
    'screenshotQuality': 2,
    'keyboardAutocorrection': 0,
    'useFirstMatch': False,
    'reduceMotion': False,
    'defaultActiveApplication': 'auto',
    'mjpegScalingFactor': 100,
    'mjpegServerScreenshotQuality': 25,
    'dismissAlertButtonSelector': '',
    'includeNonModalElements': False}
    """
    AcceptAlertButtonSelector = "acceptAlertButtonSelector"
    DismissAlertButtonSelector = "dismissAlertButtonSelector"



# default_alert_accept_selector = "**/XCUIElementTypeButton[`label IN {'允许','好','仅在使用应用期间','暂不'}`]"
# default_alert_dismiss_selector = "**/XCUIElementTypeButton[`label IN {'不允许','暂不'}`]"


class AlertAction(str, enum.Enum):
    ACCEPT = "accept"
    DISMISS = "dismiss"


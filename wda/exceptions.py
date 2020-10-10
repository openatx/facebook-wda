import json
from os import stat


JSONDecodeError = json.decoder.JSONDecodeError if hasattr(
    json.decoder, "JSONDecodeError") else ValueError


class MuxError(Exception):
    """ Mutex error """


class MuxConnectError(MuxError, ConnectionError):
    """ Error when MessageType: Connect """


class WDAError(Exception):
    """ base wda error """


class WDABadGateway(WDAError):
    """ bad gateway """


class WDAEmptyResponseError(WDAError):
    """ response body is empty """


class WDAElementNotFoundError(WDAError):
    """ element not found """


class WDAElementNotDisappearError(WDAError):
    """ element not disappera """


class WDARequestError(WDAError):
    def __init__(self, status, value):
        self.status = status
        self.value = value

    def __str__(self):
        return 'WDARequestError(status=%d, value=%s)' % (self.status,
                                                         self.value)


class WDAKeyboardNotPresentError(WDARequestError):
    # {'error': 'invalid element state', 
    #  'message': 'Error Domain=com.facebook.WebDriverAgent Code=1 
    #     "The on-screen keyboard must be present to send keys" 
    #     UserInfo={NSLocalizedDescription=The on-screen keyboard must be present to send keys}',
    #  'traceback': ''})

    @staticmethod
    def check(v: dict):
        if v.get('error') == 'invalid element state' and \
                'keyboard must be present to send keys' in v.get('message', ''):
            return True
        return False


class WDAInvalidSessionIdError(WDARequestError):
    """
    "value" : {
        "error" : "invalid session id",
        "message" : "Session does not exist",
    """
    @staticmethod
    def check(v: dict):
        if v.get('error') == 'invalid session id':
            return True
        return False


class WDAPossiblyCrashedError(WDARequestError):
    @staticmethod
    def check(v: dict):
        if "possibly crashed" in v.get('message', ''):
            return True
        return False


class WDAUnknownError(WDARequestError):
    """ error: unknown error, message: *** - """
    @staticmethod
    def check(v: dict):
        return v.get("error") == "unknown error"

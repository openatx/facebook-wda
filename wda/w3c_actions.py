# coding: utf-8

from typing import Any, Dict, List, Optional, Union


class FingerMovement:
    def __init__(self):
        self.__data: Dict[str, Any] = {
            "type": "pointerMove"
        }
    
    @property
    def data(self) -> Dict[str, Any]:
        return self.__data
    
    def with_xy(self, x: Union[int, float], y: Union[int, float]) -> "FingerMovement":
        self.__data["x"] = x
        self.__data["y"] = y
        return self
    
    def with_origin(self, element_uid: Optional[str]=None) -> "FingerMovement":
        if element_uid is not None:
            self.__data["origin"] = element_uid
        return self
    
    def with_duration(self, second: Optional[float]=None) -> "FingerMovement":
        if second is not None:
            self.__data["duration"] = second * 1000
        return self


class FingerAction:
    def __init__(self):
        self.__data: List[Dict[str, Any]] = []

    @property
    def data(self) -> List[Dict[str, Any]]:
        return self.__data
    
    def move(self, movement: FingerMovement) -> "FingerAction":
        self.__data.append(movement.data)
        return self
    
    def down(self) -> "FingerAction":
        self.__data.append({"type": "pointerDown"})
        return self
    
    def up(self) -> "FingerAction":
        self.__data.append({"type": "pointerUp"})
        return self
    
    def pause(self, second: float=0.5) -> "FingerAction":
        self.__data.append({"type": "pause", "duration": second * 1000})
        return self


class W3CActions:
    def __init__(self):
        self.__data: List[Dict[str, Any]] = []
    
    @property
    def data(self) -> List[Dict[str, Any]]:
        return self.__data

    def send_keys(self, text: str) -> "W3CActions":
        keyboard: Dict[str, Any] = {
            "type": "key",
            "id": f"keyboard{len(self.__data)}",
            "actions": [
                (a for a in [
                    {"type": "keyDown", "value": v},
                    {"type": "keyUp", "value": v}
                ]) for v in text
            ]
        }
        self.__data.append(keyboard)
        return self
    
    def inject_touch_actions(self, *actions: FingerAction) -> "W3CActions":
        for action in actions:
            pointer: Dict[str, Any] = {
                "type": "pointer",
                "id": f"finger{len(self.__data)}",
                "parameters": {
                    "pointerType": "touch"
                },
                "actions": action.data
            }
            self.__data.append(pointer)
        return self
    
    def tap(self, x: Union[int, float], y: Union[int, float], element_uid: Optional[str]=None) -> "W3CActions":
        movement = FingerMovement().with_xy(x, y).with_origin(element_uid)
        action = FingerAction().move(movement).down().pause(0.1).up()
        self.inject_touch_actions(action)
        return self
    
    def press(self, x: Union[int, float], y: Union[int, float],
              element_uid: Optional[str]=None, second: float=2.0) -> "W3CActions":
        movement = FingerMovement().with_xy(x, y).with_origin(element_uid)
        action = FingerAction().move(movement).down().pause(second).up()
        self.inject_touch_actions(action)
        return self
    
    def swipe(self, from_x: Union[int, float], from_y: Union[int, float],
              to_x: Union[int, float], to_y: Union[int, float], element_uid: Optional[str]=None,
              press_seconds: float=0.25, swipe_seconds: Optional[float]=None, hold_seconds: float=0.25) -> "W3CActions":
        movement_from = FingerMovement().with_xy(from_x, from_y).with_origin(element_uid)
        movement_to = FingerMovement().with_xy(to_x, to_y).with_origin(element_uid).with_duration(swipe_seconds)
        action = FingerAction().move(movement_from).down().pause(press_seconds).move(movement_to).pause(hold_seconds).up()
        self.inject_touch_actions(action)
        return self

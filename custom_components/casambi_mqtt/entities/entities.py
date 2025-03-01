from dataclasses import dataclass
from typing import ClassVar, List

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class UnitControlType:
    name: str
    value: int


@dataclass_json
@dataclass
class UnitControl:
    default: int
    length: int
    offset: int
    readonly: bool
    type: UnitControlType


@dataclass_json
@dataclass
class UnitType:
    id: int
    manufacturer: str
    mode: str
    model: str
    stateLength: int
    controls: List[UnitControl]


@dataclass_json
@dataclass
class UnitState:
    dimmer: int | None
    # more states...


@dataclass_json
@dataclass
class Unit:
    address: str
    device_id: int
    is_on: bool
    name: str
    online: bool
    state: UnitState
    uuid: str
    unit_type: UnitType

    TYPE_LIGHT: ClassVar[str] = "LIGHT"
    TYPE_SWITCH: ClassVar[str] = "SWITCH"
    TYPE_UNKNOWN: ClassVar[str] = "UNKNOWN"

    def type(self) -> str:
        if len([u for u in self.unit_type.controls if u.type.name == "DIMMER"]) > 0:
            return self.TYPE_LIGHT
        if "switch" in self.unit_type.mode.lower():
            return self.TYPE_SWITCH
        return self.TYPE_UNKNOWN


@dataclass_json
@dataclass
class Scene:
    scene_id: int
    name: str

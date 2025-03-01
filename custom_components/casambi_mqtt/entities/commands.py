import abc
import json
from dataclasses import asdict, dataclass
from typing import ClassVar, Self


@dataclass
class BaseCommand(abc.ABC):
    @abc.abstractmethod
    def _action(self) -> str:
        pass

    def to_json(self) -> str:
        data = asdict(self)
        data.update({"action": self._action()})
        return json.dumps(data)

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        data = json.loads(json_str)
        fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {key: value for key, value in data.items() if key in fields}
        return cls(**filtered_data)


@dataclass
class SetLevel(BaseCommand):
    address: str
    value: int
    ACTION: ClassVar[str] = "SET_LEVEL"

    def _action(self) -> str:
        return self.ACTION


@dataclass
class TurnOn(BaseCommand):
    address: str
    ACTION: ClassVar[str] = "TURN_ON"

    def _action(self) -> str:
        return self.ACTION


@dataclass
class PublishEntities(BaseCommand):
    ACTION: ClassVar[str] = "PUBLISH_ENTITIES"

    def _action(self) -> str:
        return self.ACTION


@dataclass
class SetScene(BaseCommand):
    scene_id: int
    ACTION: ClassVar[str] = "SET_SCENE"

    def _action(self) -> str:
        return self.ACTION

from enum import Enum

import mypy


class HookType(Enum):
    NONE = 0
    GENERAL_SETUP = 1
    GENERAL_SHUTDOWN = 2
    FILE_SETUP = 3
    FILE_SHUTDOWN = 4
    FUNCTION_SETUP = 5
    FUNCTION_SHUTDOWN = 6

    @classmethod
    def getType(cls, id: int) -> 'HookType':
        return HookType(cls._value2member_map_.get(id,(cls.NONE)))

    def __str__(self) -> str:
        return str(self.name)


class Hook:
    def __init__(self, hook_type: HookType, data: dict) -> None:
        self.type: HookType = hook_type

        attributes: dict[str, str] = {}
        commands: list[str] = []
        description: str = ""

        if data != {}:
            if "attributes" in data:
                if type(data["attributes"]) == list:
                    attributes = {i: "" for i in list(dict(data["attributes"]).keys())}
                else:
                    attributes = dict(data["attributes"])
            commands = list(data["commands"] if "commands" in data.keys() else [])
            description = str(data["description"] if "description" in data.keys() else "")

        self.attributes: dict[str, str] = attributes
        self.commands: list[str] = commands
        self.description: str = description

    # def __dict__(self) -> dict[str, dict[str, str] | list[str] | str]:
    #     return {
    #         "attributes": self.attributes,
    #         "commands": self.commands,
    #         "description": self.description
    #     }

    def toDict(self) ->  dict[str, dict[str, str] | list[str] | str]:
        result: dict[str, dict[str, str] | list[str] | str] = {}
        if self.attributes != {}:
            result["attributes"] = self.attributes
        if self.commands != []:
            result["commands"] = self.commands
        if self.description != "":
            result["description"] = self.description
        return result

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Hook):
            return NotImplemented

        return (
            self.type == other.type
            and self.attributes == other.attributes
            and self.commands == other.commands
            and self.description == other.description
        )

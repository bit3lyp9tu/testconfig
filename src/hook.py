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

    def getType(self, id: int) -> Enum:
        match id:
            case 1:
                return HookType.GENERAL_SETUP
            case 2:
                return HookType.GENERAL_SHUTDOWN
            case 3:
                return HookType.FILE_SETUP
            case 4:
                return HookType.FILE_SHUTDOWN
            case 5:
                return HookType.FUNCTION_SETUP
            case 6:
                return HookType.FUNCTION_SHUTDOWN
            case _:
                return HookType.NONE

    def __str__(self) -> str:
        return str(self.name)

    def __eq__(self, hook_type) -> bool:
        return self.value == hook_type.value

class Hook:
    def __init__(self, hook_type: HookType, data: dict) -> None:
        self.type: HookType = hook_type

        attributes: dict[str, str] = {}
        commands: list[str] = []
        description: str = ""

        if data != {}:
            if "attributes" in data.keys():
                if type(data["attributes"]) == list:
                    attributes = {i: "" for i in list(dict(data["commands"]).keys())}
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

    def __eq__(self, hook_type) -> bool:
        return self.type == hook_type.type and self.attributes == hook_type.attributes and self.commands == hook_type.commands and self.description == hook_type.description

    # def overrideWith(self, hook: 'Hook') -> 'Hook':
    #     if self.type == hook.type:
    #         return

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


class Layer:
    def __init__(self) -> None:
        self.data: dict = {}

    def toData(self) -> dict:
        return self.data

class GeneralLayer(Layer):
    def __init__(self, setup: Hook, shutdown: Hook) -> None:
        super().__init__()
        self.general_setup: Hook = setup
        self.general_shutdown: Hook = shutdown

        self.general_shutdown.attributes.update(setup.attributes)

        self.data["general_setup"] = self.general_setup.toDict()
        self.data["general_shutdown"] = self.general_shutdown.toDict()

class FileLayer(GeneralLayer):
    def __init__(self, general_layer: GeneralLayer, language: str, setup: Hook, shutdown: Hook) -> None:
        super().__init__(
            general_layer.general_setup,
            general_layer.general_shutdown
        )

        self.file_setup: Hook = setup
        self.file_setup.attributes.update(self.general_setup.attributes)

        self.file_shutdown: Hook = shutdown
        self.file_shutdown.attributes.update(self.file_setup.attributes)

        self.data["file_setup"] = {
            language: self.file_setup.toDict()
        }
        self.data["file_shutdown"] = {
            language: self.file_shutdown.toDict()
        }

class FunctionLayer(FileLayer):
    def __init__(self, file_layer: FileLayer, language: str, file: str, setup: Hook, shutdown: Hook) -> None:
        super().__init__(
            GeneralLayer(file_layer.general_setup, file_layer.general_shutdown),
            language,
            file_layer.file_setup,
            file_layer.file_shutdown
        )

        self.function_setup: Hook = setup
        self.function_setup.attributes.update(self.file_setup.attributes)

        self.function_shutdown: Hook = shutdown
        self.function_shutdown.attributes.update(self.function_setup.attributes)

        self.data["function_setup"] = {
            language: {
                file: self.function_setup.toDict()
            }
        }
        self.data["function_shutdown"] = {
            language: {
                file: self.function_shutdown.toDict()
            }
        }

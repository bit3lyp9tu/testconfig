from enum import Enum

from collections import defaultdict

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

    def getChildData(self) -> dict:
        return {
            "attribute": self.attributes
        }

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


def to_dict(d):
    if isinstance(d, defaultdict):
        return {k: to_dict(v) for k, v in d.items()}
    return d


def deep_merge(base: dict, override: dict) -> dict:
    result = base.copy()
    for k, v in override.items():
        if (
            k in result
            and isinstance(result[k], dict)
            and isinstance(v, dict)
        ):
            result[k] = deep_merge(result[k], v)
        else:
            result[k] = v
    return result


class Layer:
    def __init__(self) -> None:
        self.data: dict = defaultdict(dict)

    def finalize(self) -> None:
        if "general_setup" not in self.data:
            self.data["general_setup"] = {}

        if "general_shutdown" not in self.data:
            self.data["general_shutdown"] = {}

        if "file_setup" not in self.data:
            self.data["file_setup"] = {}

        if "file_shutdown" not in self.data:
            self.data["file_shutdown"] = {}

        if "function_setup" not in self.data:
            self.data["function_setup"] = {}

        if "function_shutdown" not in self.data:
            self.data["function_shutdown"] = {}

    def merge(self, data: dict) -> None:
        self.data = deep_merge(self.data, data)

    def toData(self) -> dict:
        self.finalize()
        return to_dict(self.data)

    # def __getitem__(self, key):
    #     return self.data[key]

class GeneralLayer(Layer):
    def __init__(self, setup: Hook, shutdown: Hook) -> None:
        super().__init__()
        self.finalize()

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

        self.file_setup: Hook = Hook(setup.type, {"attributes": self.general_setup.attributes, "commands": setup.commands})
        self.file_setup.attributes.update(setup.attributes)

        self.file_shutdown: Hook = shutdown
        self.file_shutdown.attributes.update(self.file_setup.attributes)

        self.data["file_setup"][language] = self.file_setup.toDict()
        self.data["file_shutdown"][language] = self.file_shutdown.toDict()


class FunctionLayer(FileLayer):
    def __init__(self, file_layer: FileLayer, language: str, file: str, setup: Hook, shutdown: Hook) -> None:
        super().__init__(
            GeneralLayer(file_layer.general_setup, file_layer.general_shutdown),
            language,
            file_layer.file_setup,
            file_layer.file_shutdown
        )

        self.function_setup: Hook = Hook(setup.type, {"attributes": self.file_setup.attributes, "commands": setup.commands})
        self.function_setup.attributes.update(setup.attributes)

        self.function_shutdown: Hook = shutdown
        self.function_shutdown.attributes.update(self.function_setup.attributes)

        self.data.setdefault("function_setup", {}).setdefault(language, {})[file] = self.function_setup.toDict()
        self.data.setdefault("function_shutdown", {}).setdefault(language, {})[file] = self.function_shutdown.toDict()


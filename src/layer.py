import mypy

from collections import defaultdict

from .hook import HookType, Hook


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
        for member in HookType.__members__:
            hook_name = member.lower()
            if hook_name != "none" and hook_name not in self.data:
                self.data[hook_name] = {}

    def merge(self, data: dict) -> None:
        self.data = deep_merge(self.data, data)

    def toData(self) -> dict:
        self.finalize()
        return to_dict(self.data)

    def updateData(self, data, *keys) -> None:
        d = self.data
        for key in keys[:-1]:
            d = d.setdefault(key, {})
        d[keys[-1]] = data


class GeneralLayer(Layer):
    def __init__(self, setup: Hook, shutdown: Hook) -> None:
        super().__init__()
        self.finalize()

        self.general_setup: Hook = setup
        self.general_shutdown: Hook = shutdown

        self.general_shutdown.attributes.update(setup.attributes)

        self.updateData(self.general_setup.toDict(), "general_setup")
        self.updateData(self.general_shutdown.toDict(), "general_shutdown")


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

        self.updateData(self.file_setup.toDict(), "file_setup", language)
        self.updateData(self.file_shutdown.toDict(), "file_shutdown", language)


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

        self.updateData(self.function_setup.toDict(), "function_setup", language, file)
        self.updateData(self.function_shutdown.toDict(), "function_shutdown", language, file)


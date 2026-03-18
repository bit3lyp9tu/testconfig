from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[2]

# print(ROOT)

spec = importlib.util.spec_from_file_location("config_parser", ROOT / "src/config_parser.py")
config_parser = importlib.util.module_from_spec(spec) # type: ignore
spec.loader.exec_module(config_parser) # type: ignore

spec = importlib.util.spec_from_file_location("hook", ROOT / "src/hook.py")
hook = importlib.util.module_from_spec(spec) # type: ignore
spec.loader.exec_module(hook) # type: ignore

spec = importlib.util.spec_from_file_location("layer", ROOT / "src/layer.py")
layer = importlib.util.module_from_spec(spec) # type: ignore
spec.loader.exec_module(layer) # type: ignore


def complex_test():
    mainConfig1 = config_parser.MainConfig("../tests/configs/config1.yaml")

    general_layer = layer.GeneralLayer(
        mainConfig1.getHookGeneral(hook.HookType.GENERAL_SETUP),
        mainConfig1.getHookGeneral(hook.HookType.GENERAL_SHUTDOWN)
    )

    for language in mainConfig1.getLanguages():
        if language in mainConfig1.getLanguages() and mainConfig1.content[language] != None:

            file_layer = layer.FileLayer(
                general_layer,
                language,
                mainConfig1.getHookFile(hook.HookType.FILE_SETUP, language),
                mainConfig1.getHookFile(hook.HookType.FILE_SHUTDOWN, language)
            )

            for script in mainConfig1.getScripts(language):
                if script in mainConfig1.content[language] and mainConfig1.content[language][script] != None:

                    function_layer = layer.FunctionLayer(
                        file_layer,
                        language,
                        script,
                        mainConfig1.getHookFunction(hook.HookType.FUNCTION_SETUP, language, script),
                        mainConfig1.getHookFunction(hook.HookType.FUNCTION_SHUTDOWN, language, script)
                    )
                    file_layer.merge(function_layer.toData())
            general_layer.merge(file_layer.toData())

        else:
            general_layer.merge({
                "file_setup": {language: {}},
                "file_shutdown": {language: {}},
                "function_setup": {language: {}},
                "function_shutdown": {language: {}},
            })

    return layer.to_dict(general_layer.toData()) == {
        "general_setup": {
            "attributes": {
                "path": "a_random_path"
            }
        },
        "general_shutdown": {
            "attributes": {
                "path": "a_random_path"
            }
        },
        "file_setup": {
            "python": {
                "attributes": {
                    "path": "new_path_overrides_old_one"
                },
                "commands": [
                    "echo OVERRIDDEN"
                ]
            },
            "php": {},
            "cpp": {}
        },
        "file_shutdown": {
            "python": {
                "attributes": {
                    "path": "new_path_overrides_old_one"
                },
                "commands": [
                    "echo SHUTDOWN"
                ]
            },
            "php": {},
            "cpp": {}
        },
        "function_setup": {
            "python": {
                "tests/code/test.py": {
                    "attributes": {
                        "path": "src/tests",
                        "target": "add"
                    }
                }
            },
            "php": {},
            "cpp": {}
        },
        "function_shutdown": {
            "python": {
                "tests/code/test.py": {
                    "attributes": {
                        "path": "src/tests",
                        "target": "add"
                    }
                }
            },
            "php": {},
            "cpp": {}
        }
    }

import os

import mypy
import pytest

from pathlib import Path

from collections import defaultdict

from src.config_parser import MainConfig
from src.hook import HookType
from src.layer import GeneralLayer, FileLayer, FunctionLayer, to_dict


mainConfig1: MainConfig = MainConfig("../tests/configs/config1.yaml")
mainConfig2: MainConfig = MainConfig("../tests/configs/config2.yaml")
mainConfig3: MainConfig = MainConfig("../tests/configs/config3.yaml")

mainConfig5: MainConfig = MainConfig("../tests/configs/config5.yaml")

def test_mainConfig_path() -> None:
    """
    Test the path attribute of the MainConfig class.
    """
    result = mainConfig1.path
    assert result == "../tests/configs/config1.yaml"
    result2 = mainConfig2.path
    assert result2 == "../tests/configs/config2.yaml"

def test_mainConfig_content_type() -> None:
    """
    Test the content attribute type of the MainConfig class.
    """
    result = type(mainConfig1.content)
    assert result == dict
    result2 = type(mainConfig2.content)
    assert result2 == dict

def test_mainConfig_content_languages() -> None:
    """
    Test the content attribute languages.
    """
    result = mainConfig1.getLanguages()
    assert set(result) == {
        "python",
        "php",
        "cpp"
    }
    result2 = mainConfig2.getLanguages()
    assert set(result2) == {
        "python"
    }

def test_mainConfig_content_scripts() -> None:
    """
    Test the content attribute scripts.
    """
    result = mainConfig1.getScripts("python")
    assert set(result) == {
        "tests/code/test.py"
    }
    result = mainConfig1.getScripts("php")
    assert set(result) == set({})
    result2 = mainConfig2.getScripts("python")
    assert set(result2) == {
        "tests/code/test.py"
    }

def test_mainConfig_content_functions() -> None:
    """
    Test the content attribute functions.
    """
    result = list(mainConfig1.getFunctionsBody("python", "tests/code/test.py").keys())
    assert result ==  ["add", "subtract", "multiply"]

    result2 = list(mainConfig2.getFunctionsBody("python", "tests/code/test.py").keys())
    assert result2 ==  []
    result2 = list(mainConfig2.getFunctionsBody("python", "tests/code/file_does_not_exists.py").keys())
    assert result2 ==  []

    result = list(mainConfig1.getFunctionsBody("java", "tests/code/test.jar").keys())
    assert result ==  []

def test_get_code_file_name() -> None:
    """
    Test the getter for the code file name
    """
    result = mainConfig1._getCodeFile("python", "tests/code/test.py", "multiply")
    assert result == ""
    result = mainConfig5._getCodeFile("python", "tests/code/test.py", "complex_test")
    assert result == "tests/configs/config5.py"

def test_mainConfig_content_functions_content_data() -> None:
    """
    Test the content attribute test data.
    """
    result = mainConfig1.getFunction("python", "tests/code/test.py", "add")
    assert result == [
        '1,2,3 -> 6',
        '4,5,6 -> 15',
        '-1,1,1 -> 1',
        '10,-10,5 -> 5',
        '0.5,0.5,0.5 -> 1.5',
        '0.5,-0.5,0.5 -> 0.5'
    ]
    result1 = mainConfig1.getFunction("python", "tests/code/test.py", "multiply")
    assert result1 == []
    result2 = mainConfig2.getFunction("python", "tests/code/test.py", "")
    assert result2 == []
    result2 = mainConfig2.getFunction("python", "tests/code/test.py", "not_a _function")
    assert result2 == []

def test_mainConfig_content_functions_content_csv_path() -> None:
    """
    Test the content attribute csv path.
    """
    assert not mainConfig1.isPointingToCsvFile("python", "tests/code/test.py", "add")
    assert mainConfig1.isPointingToCsvFile("python", "tests/code/test.py", "multiply")
    assert not mainConfig2.isPointingToCsvFile("python", "tests/code/test.py", "not_a_function")
    assert not mainConfig2.isPointingToCsvFile("python", "tests/code/file_does_not_exists.py", "not_a_function")

def test_is_code_file_valid() -> None:
    """
    Test if a code file exists and is in the valid prog language.
    """
    assert mainConfig5._isCodeFileValid(
        "tests/code/test.py",
        "tests/configs/config5.py"
    )

def test_typifying_test_case_line() -> None:
    """
    Test the typifying function for the test case line
    """
    result = mainConfig1._typifyTestCaseToList("1,-2,3")
    assert result == [1, -2, 3]
    result2 = mainConfig1._typifyTestCaseToList("1.1,2.2,-3.3")
    assert result2 == [1.1, 2.2, -3.3]
    result3 = mainConfig1._typifyTestCaseToList("hello,world,!")
    assert result3 == ["hello", "world", "!"]

def test_mainConfig_content_functions_content_data_list() -> None:
    """
    Test the content attribute data list.
    """
    result = mainConfig1.getTestData("python", "tests/code/test.py", "add")
    assert result == [
        ([1,2,3], [6]),
        ([4,5,6], [15]),
        ([-1,1,1], [1]),
        ([10,-10,5], [5]),
        ([0.5,0.5,0.5], [1.5]),
        ([0.5,-0.5,0.5], [0.5])
    ]
    result2 = mainConfig1.getTestData("python", "tests/code/test.py", "multiply")
    assert result2 == [
        ([7,8,9], [504]),
        ([10,11,12], [1320]),
        ([-1,10,1], [-10]),
        ([0.5,10.0,-1.0], [-5.0])
    ]
    result5 = mainConfig5.getTestData("python", "tests/code/test.py", "addAll")
    assert result5 == [
        ([1,2,3,4,5,6], [21])
    ]

DATA_GENERAL_LAYER3 = {
    'general_setup': {
        'attributes': {
            'general': 'general_variable',
        },
        'commands': [
            'echo $general 1',
            'echo $file 1',
            'echo $function 1',
        ],
    },
    'general_shutdown': {
        'attributes': {
            'general': 'general_variable',
        },
        'commands': [
            'echo $general 1b',
            'echo $file 1b',
            'echo $function 1b',
        ],
    },
    'file_setup': {},
    'file_shutdown': {},
    'function_setup': {},
    'function_shutdown': {},
}

DATA_FILE_LAYER3 = {
    'file_setup': {
        'python': {
            'attributes': {
                'general': 'general_variable',
                'file': 'file_variable'
            },
            'commands': [
                'echo $general 2',
                'echo $file 2',
                'echo $function 2',
            ],
        },
    },
    'file_shutdown': {
        'python': {
            'attributes': {
                'general': 'general_variable',
                'file': 'file_variable'
            },
            'commands': [
                'echo $general 2b',
                'echo $file 2b',
                'echo $function 2b',
            ],
        },
    },
    'general_setup': {
        'attributes': {
            'general': 'general_variable',
        },
        'commands': [
            'echo $general 1',
            'echo $file 1',
            'echo $function 1',
        ],
    },
    'general_shutdown': {
        'attributes': {
            'general': 'general_variable',
        },
        'commands': [
            'echo $general 1b',
            'echo $file 1b',
            'echo $function 1b',
        ],
    },
    'function_setup': {},
    'function_shutdown': {},
}

DATA_FUNCTION_LAYER3 = {
    'function_setup': {
        'python': {
            'tests/code/test.py': {
                'attributes': {
                    'general': 'general_variable',
                    'file': 'file_variable',
                    'function': 'function_variable',
                },
                'commands': [
                    'echo $general 3',
                    'echo $file 3',
                    'echo $function 3',
                ],
            },
        },
    },
    'function_shutdown': {
        'python': {
            'tests/code/test.py': {
                'attributes': {
                    'general': 'general_variable',
                    'file': 'file_variable',
                    'function': 'function_variable',
                },
                'commands': [
                    'echo $general 3b',
                    'echo $file 3b',
                    'echo $function 3b',
                ],
            },
        },
    },
    'file_setup': {
        'python': {
            'attributes': {
                'general': 'general_variable',
                'file': 'file_variable'
            },
            'commands': [
                'echo $general 2',
                'echo $file 2',
                'echo $function 2',
            ],
        },
    },
    'file_shutdown': {
        'python': {
            'attributes': {
                'general': 'general_variable',
                'file': 'file_variable'
            },
            'commands': [
                'echo $general 2b',
                'echo $file 2b',
                'echo $function 2b',
            ],
        },
    },
    'general_setup': {
        'attributes': {
            'general': 'general_variable',
        },
        'commands': [
            'echo $general 1',
            'echo $file 1',
            'echo $function 1',
        ],
    },
    'general_shutdown': {
        'attributes': {
            'general': 'general_variable',
        },
        'commands': [
            'echo $general 1b',
            'echo $file 1b',
            'echo $function 1b',
        ],
    }
}

DATA_CONFIG1 = {
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

DATA_CONFIG4 = {
    'file_setup': {
        'cpp': {},
        'php': {
            # 'commands': [
            #     'ls -a invalid_path',
            # ],
        },
        'python': {
            'commands': [
                'ls -a invalid_path',
            ],
        },
    },
    'file_shutdown': {
        'cpp': {},
        'php': {},
        'python': {},
    },
    'function_setup': {
        'cpp': {},
        'php': {
            'tests/code/test.php': {},
        },
        'python': {
            'tests/code/test.py': {},
        },
    },
    'function_shutdown': {
        'cpp': {},
        'php': {
            'tests/code/test.php': {},
        },
        'python': {
            'tests/code/test.py': {},
        },
    },
    'general_setup': {
        'commands': [
            '$invalid_path',
        ],
    },
    'general_shutdown': {},
}

def test_mainConfig_hooks_all() -> None:
    """
    Test if hooks getter returns all hooks from config file
    """
    mainConfig3 = MainConfig("../tests/configs/config3.yaml")

    general_layer = GeneralLayer(
        mainConfig3.getHookGeneral(HookType.GENERAL_SETUP),
        mainConfig3.getHookGeneral(HookType.GENERAL_SHUTDOWN)
    )
    assert general_layer.toData() == DATA_GENERAL_LAYER3

    file_layer = FileLayer(
        general_layer,
        "python",
        mainConfig3.getHookFile(HookType.FILE_SETUP, "python"),
        mainConfig3.getHookFile(HookType.FILE_SHUTDOWN, "python")
    )
    assert file_layer.toData() == DATA_FILE_LAYER3

    function_layer = FunctionLayer(
        file_layer,
        "python",
        "tests/code/test.py",
        mainConfig3.getHookFunction(HookType.FUNCTION_SETUP, "python", "tests/code/test.py"),
        mainConfig3.getHookFunction(HookType.FUNCTION_SHUTDOWN, "python", "tests/code/test.py")
    )
    assert function_layer.toData() == DATA_FUNCTION_LAYER3

    mainConfig4 = MainConfig("../tests/configs/config4.yaml")
    assert mainConfig4.getHooks() == DATA_CONFIG4


def test_mainConfig_hook_layers_in_loop() -> None:
    """
    Test hook layers in loop
    """

    general_layer = GeneralLayer(
        mainConfig1.getHookGeneral(HookType.GENERAL_SETUP),
        mainConfig1.getHookGeneral(HookType.GENERAL_SHUTDOWN)
    )

    for language in mainConfig1.getLanguages():
        if language in mainConfig1.getLanguages() and mainConfig1.content[language] != None:

            file_layer = FileLayer(
                general_layer,
                language,
                mainConfig1.getHookFile(HookType.FILE_SETUP, language),
                mainConfig1.getHookFile(HookType.FILE_SHUTDOWN, language)
            )

            for script in mainConfig1.getScripts(language):
                if script in mainConfig1.content[language] and mainConfig1.content[language][script] != None:

                    function_layer = FunctionLayer(
                        file_layer,
                        language,
                        script,
                        mainConfig1.getHookFunction(HookType.FUNCTION_SETUP, language, script),
                        mainConfig1.getHookFunction(HookType.FUNCTION_SHUTDOWN, language, script)
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

    assert to_dict(general_layer.toData()) == DATA_CONFIG1


def test_mainConfig_hooks() -> None:
    """
    Test full hooks getter
    """
    mainConfig4 = MainConfig("../tests/configs/config3.yaml")

    assert mainConfig4.getHooks() == DATA_FUNCTION_LAYER3

    result = mainConfig1.getHooks()
    assert result == DATA_CONFIG1
    result3 = mainConfig3.getHooks()
    assert result3 == DATA_FUNCTION_LAYER3


def test_mainConfig_hooks_general_setup() -> None:
    """
    Test import general setup
    """
    result = mainConfig1.getHookGeneral(HookType.GENERAL_SETUP)
    assert result.type == HookType.GENERAL_SETUP
    assert result.attributes == {"path": "a_random_path"}
    assert result.commands == []
    assert result.description == ""

    result3 = mainConfig3.getHookGeneral(HookType.GENERAL_SETUP)
    assert result3.toDict() == {
        "attributes": {
            "general": "general_variable"
        },
        "commands": [
            "echo $general 1",
            "echo $file 1",
            "echo $function 1"
        ]
    }

def test_mainConfig_hooks_general_shutdown() -> None:
    """
    Test import general shutdown
    """
    result = mainConfig1.getHookGeneral(HookType.GENERAL_SHUTDOWN)
    assert result.type == HookType.GENERAL_SHUTDOWN
    assert result.attributes == {}
    assert result.commands == []
    assert result.description == ""

    result3 = mainConfig3.getHookGeneral(HookType.GENERAL_SHUTDOWN)
    assert result3.toDict() == {
        "commands": [
            "echo $general 1b",
            "echo $file 1b",
            "echo $function 1b"
        ]
    }

def test_mainConfig_hooks_file_setup() -> None:
    """
    Test import file setup
    """
    result = mainConfig1.getHookFile(HookType.FILE_SETUP, "python")
    assert result.type == HookType.FILE_SETUP
    assert result.attributes == {"path": "new_path_overrides_old_one"}
    assert result.commands == ["echo OVERRIDDEN"]
    assert result.description == ""

    result3 = mainConfig3.getHookFile(HookType.FILE_SETUP, "python")
    assert result3.toDict() == {
        "attributes": {
            "file": "file_variable"
        },
        "commands": [
            "echo $general 2",
            "echo $file 2",
            "echo $function 2"
        ]
    }

def test_mainConfig_hooks_file_shutdown() -> None:
    """
    Test import file shutdown
    """
    result = mainConfig1.getHookFile(HookType.FILE_SHUTDOWN, "python")
    assert result.type == HookType.FILE_SHUTDOWN
    assert result.attributes == {}
    assert result.commands == [
        "echo SHUTDOWN"
    ]
    assert result.description == ""

    result3 = mainConfig3.getHookFile(HookType.FILE_SHUTDOWN, "python")
    assert result3.toDict() == {
        "commands": [
            "echo $general 2b",
            "echo $file 2b",
            "echo $function 2b"
        ]
    }

def test_mainConfig_hooks_function_setup() -> None:
    """
    Test import function setup
    """
    result = mainConfig1.getHookFunction(HookType.FUNCTION_SETUP, "python", "tests/code/test.py")
    assert result.type == HookType.FUNCTION_SETUP
    assert result.attributes == {"path": "src/tests", "target": "add"}
    assert result.commands == []
    assert result.description == ""

    result3 = mainConfig3.getHookFunction(HookType.FUNCTION_SETUP, "python", "tests/code/test.py")
    assert result3.toDict() == {
        "attributes": {
            "function": "function_variable"
        },
        "commands": [
            "echo $general 3",
            "echo $file 3",
            "echo $function 3"
        ]
    }

def test_mainConfig_hooks_function_shutdown() -> None:
    """
    Test import function shutdown
    """
    result = mainConfig1.getHookFunction(HookType.FUNCTION_SHUTDOWN, "python", "tests/code/test.py")
    assert result.type == HookType.FUNCTION_SHUTDOWN
    assert result.attributes == {}
    assert result.commands == []
    assert result.description == ""

    result3 = mainConfig3.getHookFunction(HookType.FUNCTION_SHUTDOWN, "python", "tests/code/test.py")
    assert result3.toDict() == {
        "commands": [
            "echo $general 3b",
            "echo $file 3b",
            "echo $function 3b"
        ]
    }

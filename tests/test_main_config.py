import os

import mypy
import pytest

from pathlib import Path

from src.config_parser import MainConfig
from src.hook import HookType


mainConfig1: MainConfig = MainConfig("../tests/configs/config1.yaml")
mainConfig2: MainConfig = MainConfig("../tests/configs/config2.yaml")

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

def test_mainConfig_hooks_all() -> None:
    """
    Test if hooks getter returns all hooks from config file
    """
    result = mainConfig1.getHooks()
    assert result == {
        "general_setup": {
            "attributes": {
                "path": "a_random_path"
            }
        },
        "general_shutdown": {},
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
                "tests/code/test.py": {}
            },
            "php": {},
            "cpp": {}
        }
    }


def test_mainConfig_hooks_general_setup() -> None:
    """
    Test import general setup
    """
    result = mainConfig1.getHookGeneral(HookType.GENERAL_SETUP)
    assert result.type == HookType.GENERAL_SETUP
    assert result.attributes == {"path": "a_random_path"}
    assert result.commands == []
    assert result.description == ""

def test_mainConfig_hooks_general_shutdown() -> None:
    """
    Test import general shutdown
    """
    result = mainConfig1.getHookGeneral(HookType.GENERAL_SHUTDOWN)
    assert result.type == HookType.GENERAL_SHUTDOWN
    assert result.attributes == {}
    assert result.commands == []
    assert result.description == ""

def test_mainConfig_hooks_file_setup() -> None:
    """
    Test import file setup
    """
    result = mainConfig1.getHookFile(HookType.FILE_SETUP, "python")
    assert result.type == HookType.FILE_SETUP
    assert result.attributes == {"path": "new_path_overrides_old_one"}
    assert result.commands == ["echo OVERRIDDEN"]
    assert result.description == ""

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

def test_mainConfig_hooks_function_setup() -> None:
    """
    Test import function setup
    """
    result = mainConfig1.getHookFunction(HookType.FUNCTION_SETUP, "python", "tests/code/test.py")
    assert result.type == HookType.FUNCTION_SETUP
    assert result.attributes == {"path": "src/tests", "target": "add"}
    assert result.commands == []
    assert result.description == ""

def test_mainConfig_hooks_function_shutdown() -> None:
    """
    Test import function shutdown
    """
    result = mainConfig1.getHookFunction(HookType.FUNCTION_SHUTDOWN, "python", "tests/code/test.py")
    assert result.type == HookType.FUNCTION_SHUTDOWN
    assert result.attributes == {}
    assert result.commands == []
    assert result.description == ""

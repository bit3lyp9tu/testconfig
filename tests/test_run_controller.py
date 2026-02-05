import mypy
import pytest

from src.config_parser import *
from src.file_builder import RunController, Writer
from src.hook import HookType


test_runs1 = RunController("../tests/configs/config1.yaml", "../tests/configs/lang1")
def test_run_controller() -> None:
    """
    Basic test for RunController class
    """
    assert test_runs1.langConfigs.keys() == {
        "../tests/configs/lang1/python.yaml",
        "../tests/configs/lang1/php.yaml"
    }
    assert test_runs1.langConfigs["../tests/configs/lang1/php.yaml"].content == {
        "config": None,
        "unit-test": None,
        "hooks": None
    }

def test_run_controller_run_hook() -> None:
    """
    Test specific hook command
    """
    out_lang, err_code = Writer.runHook(test_runs1.getJoinedHook(HookType.FILE_SETUP, "python"))
    assert out_lang == [
        "OVERRIDDEN"
    ]
    assert err_code == 0

def test_run_controller_join_hook() -> None:
    """
    Test the joiner of main config and lang config
    """
    joined_hook  = test_runs1.getJoinedHook(HookType.NONE, "")
    assert joined_hook.toDict() == {}
def test_run_controller_join_hook_general_setup() -> None:
    """
    Test the general setup hook joiner of main config and lang config
    """
    # TODO: needs to be tested without language parameter
    hook_general_setup = test_runs1.getJoinedHook(HookType.GENERAL_SETUP, "python")
    assert hook_general_setup.toDict() == {
        "attributes": {
            "path": "a_random_path",
            "env_name": ""
        },
        "commands": [
            "echo Setting up environment"
        ],
        "description": "Setup the environment before running the tests"
    }
def test_run_controller_join_hook_general_shutdown() -> None:
    """
    Test the general shutdown hook joiner of main config and lang config
    """
    # TODO: needs to be tested without language parameter
    hook_general_shutdown = test_runs1.getJoinedHook(HookType.GENERAL_SHUTDOWN, "python")
    assert hook_general_shutdown.toDict() == {
        "attributes": {"path_old": "", "path": "a_random_path"},
        "commands": ["echo 'Closing down environment' in $path"],
        "description": "Close down the environment after running the tests"
    }
def test_run_controller_join_hook_file_setup() -> None:
    """
    Test the file setup hook joiner of main config and lang config
    """
    hook_file_setup = test_runs1.getJoinedHook(HookType.FILE_SETUP, "python")
    assert hook_file_setup.toDict() == {
        "attributes": {
            "path": "new_path_overrides_old_one"
        },
        "commands": [
            "echo OVERRIDDEN"
        ]
    }
    hook_file_setup = test_runs1.getJoinedHook(HookType.FILE_SETUP, "")
    assert hook_file_setup.toDict() == {}


def test_run_controller_join_hook_file_shutdown() -> None:
    """
    Test the file shutdown hook joiner of main config and lang config
    """
    hook_file_shutdown = test_runs1.getJoinedHook(HookType.FILE_SHUTDOWN, "python")
    assert hook_file_shutdown.toDict() == {
        "attributes": {
            "path": "new_path_overrides_old_one"
        },
        "commands": [
            "echo SHUTDOWN"
        ]
    }
def test_run_controller_join_hook_function_setup() -> None:
    """
    Test the function setup hook joiner of main config and lang config
    """

    result = test_runs1.mainConfig.getHooks()
    assert result["function_setup"] == {
        "php": {},
        "cpp": {},
        "python": {
            "tests/code/test.py": {
                "attributes": {
                    "path": "src/tests",
                    "target": "add"
                }
            }
        }
    }

    hook_function_setup = test_runs1.getJoinedHook(HookType.FUNCTION_SETUP, "python", "tests/code/test.py")
    assert hook_function_setup.toDict() == {
        "attributes": {
            "path": "src/tests",
            "target": "add"
        }
    }
    hook_function_setup = test_runs1.getJoinedHook(HookType.FUNCTION_SETUP, "")
    assert hook_function_setup.toDict() == {}

def test_run_controller_join_hook_function_shutdown() -> None:
    """
    Test the function shutdown hook joiner of main config and lang config
    """
    hook_function_shutdown = test_runs1.getJoinedHook(HookType.FUNCTION_SHUTDOWN, "python", "tests/code/test.py")
    assert hook_function_shutdown.toDict() == {
        "attributes": {
            "path": "src/tests",
            "target": "add"
        },
        "description": "none"
    }

test_runs3 = RunController("../tests/configs/config3.yaml", "../tests/configs/lang3")
def test_run_controller_check_environment_scope() -> None:
    """
    Test if scope of environmental variables is correct
    """

    out_file, _ = Writer.runHook(test_runs3.getJoinedHook(HookType.GENERAL_SETUP, "python"))
    assert out_file == [
        "general_variable 1",
        "Missing environment variable: [$file]",
        "Missing environment variable: [$function]",
    ]
    out_file, _ = Writer.runHook(test_runs3.getJoinedHook(HookType.FILE_SETUP, "python"))
    assert out_file == [
        "general_variable 2",
        "file_variable 2",
        "Missing environment variable: [$function]",
    ]
    out_file, _ = Writer.runHook(test_runs3.getJoinedHook(HookType.FUNCTION_SETUP, "python", "tests/code/test.py"))
    assert out_file == [
        "general_variable 3",
        "file_variable 3",
        "function_variable 3"
    ]
    out_file, _ = Writer.runHook(test_runs3.getJoinedHook(HookType.FUNCTION_SHUTDOWN, "python", "tests/code/test.py"))
    assert out_file == [
        "general_variable 3b",
        "file_variable 3b",
        "function_variable 3b"
    ]
    out_file, _ = Writer.runHook(test_runs3.getJoinedHook(HookType.FILE_SHUTDOWN, "python"))
    assert out_file == [
        "general_variable 2b",
        "file_variable 2b",
        "Missing environment variable: [$function]",
    ]
    out_file, _ = Writer.runHook(test_runs3.getJoinedHook(HookType.GENERAL_SHUTDOWN, "python"))
    assert out_file == [
        "general_variable 1b",
        "Missing environment variable: [$file]",
        "Missing environment variable: [$function]",
    ]

def test_run_controller_start() -> None:
    """
    Test the start function of the run controller
    """

    # assert test_runs1.start("src", keep_scripts=True) == [
    #     "[Hook] load general setup...",
    #     "Setting up environment",
    #     "Language Config file found: [../tests/configs/lang1/php.yaml]",
    #     "[Hook] load file setup...",
    #     "[Hook] load file shutdown...",
    #     "Language Config file found: [../tests/configs/lang1/python.yaml]",
    #     "[Hook] load file setup...",
    #     "OVERRIDDEN",
    #     "[Hook] load function setup...",
    #     "[File Manager] generate script file [src/demo_file.py]...",
    #     "[File Manager] execute script file [src/demo_file.py]...",
    #     "",
    #     "[Hook] load function shutdown...",
    #     "[Hook] load file shutdown...",
    #     "SHUTDOWN",
    #     "[Hook] load general shutdown...",
    #     "'Closing down environment' in a_random_path",
    # ]

    # assert test_runs3.start("src") == [
    #     "[Hook] load general setup...",
    #     "general_variable 1",
    #     "[ERROR] Missing environment variable: [$file]",
    #     "[ERROR] Missing environment variable: [$function]",
    #     "Language Config file found: [../tests/configs/lang3/python.yaml]",
    #     "[Hook] load file setup...",
    #     "general_variable 2",
    #     "file_variable 2",
    #     "[ERROR] Missing environment variable: [$function]",
    #     "[Hook] load function setup...",
    #     "general_variable 3",
    #     "file_variable 3",
    #     "function_variable 3",
    #     "[File Manager] generate script file [src/demo_file.py]...",
    #     "[File Manager] execute script file [src/demo_file.py]...",
    #     "[Hook] load function shutdown...",
    #     "general_variable 3b",
    #     "file_variable 3b",
    #     "function_variable 3b",
    #     "[Hook] load file shutdown...",
    #     "general_variable 2b",
    #     "file_variable 2b",
    #     "[ERROR] Missing environment variable: [$function]",
    #     "[Hook] load general shutdown...",
    #     "general_variable 1b",
    #     "[ERROR] Missing environment variable: [$file]",
    #     "[ERROR] Missing environment variable: [$function]",
    # ]

    # test_runs2 = RunController("../tests/configs/config2.yaml", "../tests/configs/lang2")
    # assert test_runs2.start("src") == [
    #     '[Hook] load general setup...',
    #     'the stored path is',
    #     'Language Config file found: [../tests/configs/lang2/python.yaml]',
    #     '[Hook] load file setup...',
    #     '[Hook] load function setup...',
    #     '[File Manager] generate script file [src/demo_file.py]...',
    #     '[File Manager] execute script file [src/demo_file.py]...',
    #     '[Hook] load function shutdown...',
    #     '[Hook] load file shutdown...',
    #     '[Hook] load general shutdown...',
    # ]

test_runs4 = RunController("../tests/configs/config4.yaml", "../tests/configs/lang4")
def test_strange_bug() -> None:
    """
    Test strange bug - commands appear where they should not
    """

    results = {}

    results["python/general_setup"] = test_runs4.getJoinedHook(HookType.GENERAL_SETUP, "python").toDict()
    results["python/file_setup"] = test_runs4.getJoinedHook(HookType.FILE_SETUP, "python").toDict()
    results["python/function_setup"] = test_runs4.getJoinedHook(HookType.FUNCTION_SETUP, "python").toDict()
    results["python/function_shutdown"] = test_runs4.getJoinedHook(HookType.FUNCTION_SHUTDOWN, "python").toDict()
    results["python/file_shutdown"] = test_runs4.getJoinedHook(HookType.FILE_SHUTDOWN, "python").toDict()
    results["python/general_shutdown"] = test_runs4.getJoinedHook(HookType.GENERAL_SHUTDOWN, "python").toDict()

    results["php/general_setup"] = test_runs4.getJoinedHook(HookType.GENERAL_SETUP, "php").toDict()
    results["php/file_setup"] = test_runs4.getJoinedHook(HookType.FILE_SETUP, "php").toDict()
    results["php/function_setup"] = test_runs4.getJoinedHook(HookType.FUNCTION_SETUP, "php").toDict()
    results["php/function_shutdown"] = test_runs4.getJoinedHook(HookType.FUNCTION_SHUTDOWN, "php").toDict()
    results["php/file_shutdown"] = test_runs4.getJoinedHook(HookType.FILE_SHUTDOWN, "php").toDict()
    results["php/general_shutdown"] = test_runs4.getJoinedHook(HookType.GENERAL_SHUTDOWN, "php").toDict()

    # assert results == {

    # }

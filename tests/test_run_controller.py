import mypy
import pytest

from src.file_builder import RunController, ScriptBuilder
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
    out_lang, err_code = ScriptBuilder().runHook(test_runs1.getJoinedHook(HookType.FILE_SETUP, "python"))
    assert out_lang == [
        "OVERRIDDEN",
        ""
    ]
    assert err_code == 0
def test_run_controller_join_hook_general_setup() -> None:
    """
    Test the general setup hook joiner of main config and lang config
    """
    # TODO: needs to be tested without language parameter
    hook_general_setup = test_runs1.getJoinedHook(HookType.GENERAL_SETUP, "python")
    assert hook_general_setup.toDict() == {
        "attributes": {
            "path": "a_random_path"
        }
    }
def test_run_controller_join_hook_general_shutdown() -> None:
    """
    Test the general shutdown hook joiner of main config and lang config
    """
    # TODO: needs to be tested without language parameter
    hook_general_shutdown = test_runs1.getJoinedHook(HookType.GENERAL_SHUTDOWN, "python")
    assert hook_general_shutdown.toDict() == {
        "attributes": {"path_old": ""},
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
def test_run_controller_join_hook_file_shutdown() -> None:
    """
    Test the file shutdown hook joiner of main config and lang config
    """
    hook_file_shutdown = test_runs1.getJoinedHook(HookType.FILE_SHUTDOWN, "python")
    assert hook_file_shutdown.toDict() == {
        "commands": [
            "echo SHUTDOWN"
        ]
    }
def test_run_controller_join_hook_function_setup() -> None:
    """
    Test the function setup hook joiner of main config and lang config
    """
    hook_function_setup = test_runs1.getJoinedHook(HookType.FUNCTION_SETUP, "python", "tests/code/test.py")
    assert hook_function_setup.toDict() == {
        "attributes": {
            "path": "src/tests",
            "target": "add"
        }
    }
def test_run_controller_join_hook_function_shutdown() -> None:
    """
    Test the function shutdown hook joiner of main config and lang config
    """
    hook_function_shutdown = test_runs1.getJoinedHook(HookType.FUNCTION_SHUTDOWN, "python", "tests/code/test.py")
    assert hook_function_shutdown.toDict() == {
        "description": "none"
    }


def test_run_controller_start() -> None:
    """
    Test the start function of the run controller
    """
    assert test_runs1.start("src", keep_scripts=True) == [
        "[Hook] load general setup...",
        "Language Config file found: [../tests/configs/lang1/php.yaml]",
        "[Hook] load file setup...",
        "[Hook] load file shutdown...",
        "Language Config file found: [../tests/configs/lang1/python.yaml]",
        "[Hook] load file setup...",
        "OVERRIDDEN",
        "",
        "[Hook] load function setup...",
        "[File Manager] generate script file [src/demo_file.py]...",
        "[File Manager] execute script file [src/demo_file.py]...",
        "",
        "[Hook] load function shutdown...",
        "[Hook] load file shutdown...",
        "SHUTDOWN",
        "",
        "[Hook] load general shutdown...",
        "'Closing down environment' in new_path_overrides_old_one",
        ""
    ]

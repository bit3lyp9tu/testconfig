import mypy
import pytest

from src.file_builder import ScriptBuilder
from src.hook import Hook, HookType


def test_run_command_executor() -> None:
    """
    Test the command executor for running scripts
    """
    script_builder = ScriptBuilder([])
    assert script_builder.runCommand("") == ([], 0)
    assert script_builder.runCommand("ls -a") == ([
        ".",
        "..",
        ".git",
        ".gitignore",
        ".mypy_cache",
        ".pytest_cache",
        "README.md",
        "env",
        "pytest.ini",
        "run.sh",
        "src",
        "test_report.txt",
        "tests",
        "tips.md",
        "todo.md",
        ""
    ], 0)
    assert script_builder.runCommand("echo Hello World!") == ([
        "Hello World!",
        ""
    ], 0)
    assert script_builder.runCommand("echo $path", {"path": "example_path"}) == ([
        "example_path",
        ""
    ], 0)

def test_run_command_executor_with_error() -> None:
    """
    Test the command executor for running scripts with an error
    """
    script_builder = ScriptBuilder([])
    assert script_builder.runCommand("ls -a invalid_path") == ([
        "ls: cannot access 'invalid_path': No such file or directory",
        ""
    ], 2)

def test_run_hook_command() -> None:
    """
    Test run hook
    """
    script_builder = ScriptBuilder([])
    assert script_builder.runHook(Hook(HookType.GENERAL_SETUP, {
        "commands": ["echo Hello World!", "echo Test"]
    })) == ([
        "Hello World!",
        "",
        "Test",
        ""
    ], 0)
    assert script_builder.runHook(Hook(HookType.GENERAL_SETUP, {
        "commands": ["ls -a invalid_path", "echo Test"]
    })) == ([
        "ls: cannot access 'invalid_path': No such file or directory",
        "",
        "Test",
        "",
    ], 2)

import re

import mypy
import pytest

from src.file_builder import Writer
from src.hook import Hook, HookType


def test_run_command_executor() -> None:
    """
    Test the command executor for running scripts
    """
    assert Writer.runCommand("") == ([], 0)
    assert set(Writer.runCommand("ls -a")[0]) == {
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
    }
    assert Writer.runCommand("echo Hello World!") == ([
        "Hello World!",
        ""
    ], 0)
    assert Writer.runCommand("echo $path", {"path": "example_path"}) == ([
        "example_path",
        ""
    ], 0)

def test_run_command_executor_with_error() -> None:
    """
    Test the command executor for running scripts with an error
    """
    assert Writer.runCommand("ls -a invalid_path") == ([
        "ls: cannot access 'invalid_path': No such file or directory",
        ""
    ], 2)

    assert Writer.runCommand("echo $var_does_not_exist") == ([
        f"[ERROR] Missing environment variable: [$var_does_not_exist]"
    ], 1)

def test_run_hook_command() -> None:
    """
    Test run hook
    """
    assert Writer.runHook(Hook(HookType.GENERAL_SETUP, {
        "commands": ["echo Hello World!", "echo Test"]
    })) == ([
        "Hello World!",
        "Test"
    ], 0)
    assert Writer.runHook(Hook(HookType.GENERAL_SETUP, {
        "commands": ["ls -a invalid_path", "echo Test"]
    })) == ([
        "ls: cannot access 'invalid_path': No such file or directory",
        "Test"
    ], 2)

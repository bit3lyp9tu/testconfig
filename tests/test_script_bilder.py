import re

import mypy
import pytest

from src.file_builder import Writer, CommandRunner
from src.hook import Hook, HookType


def test_run_command_executor() -> None:
    """
    Test the command executor for running scripts
    """
    assert CommandRunner.runCommand("") == ([], 0)
    assert set(CommandRunner.runCommand("ls -a")[0]) == {
        ".",
        "..",
        ".git",
        ".gitignore",
        ".mypy_cache",
        ".pytest_cache",
        "README.md",
        "classes.dot",
        "classes_src.dot",
        "env",
        "packages.dot",
        "packages.svg",
        "packages_src.dot",
        "pytest.ini",
        "run.sh",
        "src",
        "test_report.txt",
        "tests",
        "tips.md",
        "todo.md",
        ""
    }
    assert CommandRunner.runCommand("echo Hello World!") == ([
        "Hello World!",
        ""
    ], 0)
    assert CommandRunner.runCommand("echo $path", {"path": "example_path"}) == ([
        "example_path",
        ""
    ], 0)

def test_run_command_executor_with_error() -> None:
    """
    Test the command executor for running scripts with an error
    """
    assert CommandRunner.runCommand("ls -a invalid_path") == ([
        "ls: cannot access 'invalid_path': No such file or directory",
        ""
    ], 2)

    assert CommandRunner.runCommand("echo $var_does_not_exist") == ([
        f"Missing environment variable: [$var_does_not_exist]"
    ], 1)

    assert CommandRunner.runCommand("sjdjhgdhjdjdfjfd") == ([
        "/bin/sh: 1: sjdjhgdhjdjdfjfd: not found",
        ""
    ], 127)

def test_run_hook_command() -> None:
    """
    Test run hook
    """
    assert CommandRunner.runHook(Hook(HookType.GENERAL_SETUP, {
        "commands": ["echo Hello World!", "echo Test"]
    })) == ([
        "Hello World!",
        "Test"
    ], 0)
    assert CommandRunner.runHook(Hook(HookType.GENERAL_SETUP, {
        "commands": ["ls -a invalid_path", "echo Test"]
    })) == ([
        "ls: cannot access 'invalid_path': No such file or directory",
        "Test"
    ], 2)

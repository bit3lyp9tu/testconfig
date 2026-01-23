import mypy
import pytest

from src.file_builder import CodeBuilder, ScriptBuilder, RunController
from src.config_parser import MainConfig, LangConfig, Hook, HookType


cb = CodeBuilder("configs/test.yaml", "configs/lang/python.yaml")

def test_build_import() -> None:
    """
    Test import getter
    """
    result = cb.getImports("python")
    assert result == [
        "import sys",
        "import tests.test"
    ]

def test_build_function_head() -> None:
    """
    Test function head getter
    """
    result = cb.getFunctionHead("python", "add", [1,2,3], [6])
    assert result == "if tests.test.add(1,2,3) != 6:"

def test_build_function_body() -> None:
    """
    Test function body getter
    """
    result = cb.getFunctionBody("python", "add", [1,2,3], [6])
    assert result == [
        "\tprint('[FAIL] tests.test.add(1,2,3) != 6')",
        "\tsys.exit(1)"
    ]

def test_build_function() -> None:
    """
    Test function getter
    """
    result = cb.getFunction("python", "add", [1,2,3], [6])
    assert result == [
        "if tests.test.add(1,2,3) != 6:",
        "\tprint('[FAIL] tests.test.add(1,2,3) != 6')",
        "\tsys.exit(1)",
        ""
    ]

def test_build_all_tests_of_function() -> None:
    """
    Test get all test of function
    """
    result = cb.getAllTestsOfFunction("python", "subtract")
    assert result == [
        "if tests.test.subtract(10,5) != 5:",
        "\tprint('[FAIL] tests.test.subtract(10,5) != 5')",
        "\tsys.exit(1)",
        ""
    ]

def test_build_all_tests() -> None:
    """
    Test build all tests getter
    """
    result = cb.getAllTests("python")
    assert result == [
        'import sys',
        'import tests.test',
        '',
        'if tests.test.add(1,2,3) != 6:',
        "\tprint('[FAIL] tests.test.add(1,2,3) != 6')",
        '\tsys.exit(1)',
        '',
        'if tests.test.add(4,5,6) != 15:',
        "\tprint('[FAIL] tests.test.add(4,5,6) != 15')",
        '\tsys.exit(1)',
        '',
        'if tests.test.add(-1,1,1) != 1:',
        "\tprint('[FAIL] tests.test.add(-1,1,1) != 1')",
        '\tsys.exit(1)',
        '',
        'if tests.test.add(10,-10,5) != 5:',
        "\tprint('[FAIL] tests.test.add(10,-10,5) != 5')",
        '\tsys.exit(1)',
        '',
        'if tests.test.add(0.5,0.5,0.5) != 1.5:',
        "\tprint('[FAIL] tests.test.add(0.5,0.5,0.5) != 1.5')",
        '\tsys.exit(1)',
        '',
        'if tests.test.add(0.5,-0.5,0.5) != 0.5:',
        "\tprint('[FAIL] tests.test.add(0.5,-0.5,0.5) != 0.5')",
        '\tsys.exit(1)',
        '',
        'if tests.test.subtract(10,5) != 5:',
        "\tprint('[FAIL] tests.test.subtract(10,5) != 5')",
        '\tsys.exit(1)',
        '',
        'if tests.test.multiply(7,8,9) != 504:',
        "\tprint('[FAIL] tests.test.multiply(7,8,9) != 504')",
        '\tsys.exit(1)',
        '',
        'if tests.test.multiply(10,11,12) != 1320:',
        "\tprint('[FAIL] tests.test.multiply(10,11,12) != 1320')",
        '\tsys.exit(1)',
        '',
        'if tests.test.multiply(-1,10,1) != -10:',
        "\tprint('[FAIL] tests.test.multiply(-1,10,1) != -10')",
        '\tsys.exit(1)',
        '',
        'if tests.test.multiply(0.5,10,-1) != -5.0:',
        "\tprint('[FAIL] tests.test.multiply(0.5,10,-1) != -5.0')",
        '\tsys.exit(1)',
        '',
    ]

test_runs = RunController("configs/test.yaml", "configs/lang")
def test_run_controller() -> None:
    """
    Basic test for RunController class
    """
    assert test_runs.langConfigs.keys() == {
        "configs/lang/python.yaml",
        "configs/lang/php.yaml"
    }
    assert test_runs.langConfigs["configs/lang/php.yaml"].content == {
        "config": None,
        "unit-test": None,
        "hooks": None
    }

def test_run_command_executor() -> None:
    """
    Test the command executor for running scripts
    """
    script_builder = ScriptBuilder([])
    assert script_builder.runCommand("ls -a") == ([
        ".",
        "..",
        "env",
        ".mypy_cache",
        ".pytest_cache",
        "pytest.ini",
        "README.md",
        "run.sh",
        "src",
        "tests",
        "tips.md",
        ""
    ], 0)
    assert script_builder.runCommand("echo Hello World!") == ([
        "Hello World!",
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
tester = RunController("configs/test.yaml", "configs/lang")
def test_run_controller_run_hook() -> None:
    """
    Test specific hook command
    """
    out_lang, err_code = ScriptBuilder().runHook(tester.getJoinedHook(HookType.FILE_SETUP, "python"))
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
    hook_general_setup = tester.getJoinedHook(HookType.GENERAL_SETUP, "python")
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
    hook_general_shutdown = tester.getJoinedHook(HookType.GENERAL_SHUTDOWN, "python")
    assert hook_general_shutdown.toDict() == {
        "attributes": {"path_old": ""},
        "commands": ["echo 'Closing down environment' in $path"],
        "description": "Close down the environment after running the tests"
    }
def test_run_controller_join_hook_file_setup() -> None:
    """
    Test the file setup hook joiner of main config and lang config
    """
    hook_file_setup = tester.getJoinedHook(HookType.FILE_SETUP, "python")
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
    hook_file_shutdown = tester.getJoinedHook(HookType.FILE_SHUTDOWN, "python")
    assert hook_file_shutdown.toDict() == {
        "commands": [
            "echo SHUTDOWN"
        ]
    }
def test_run_controller_join_hook_function_setup() -> None:
    """
    Test the function setup hook joiner of main config and lang config
    """
    hook_function_setup = tester.getJoinedHook(HookType.FUNCTION_SETUP, "python", "src/tests/test.py")
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
    hook_function_shutdown = tester.getJoinedHook(HookType.FUNCTION_SHUTDOWN, "python", "src/tests/test.py")
    assert hook_function_shutdown.toDict() == {
        "description": "none"
    }


def test_run_controller_start() -> None:
    """
    Test the start function of the run controller
    """
    assert tester.start("src", keep_scripts=True) == [
        "[Hook] load general setup...",
        "Language Config file found: [configs/lang/php.yaml]",
        "[Hook] load file setup...",
        "[Hook] load file shutdown...",
        "Language Config file found: [configs/lang/python.yaml]",
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
        "'Closing down environment' in $path",
        ""
    ]

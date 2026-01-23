import mypy
import pytest

from src.config_parser import MainConfig, LangConfig, Hook, HookType


mainConfig: MainConfig = MainConfig("configs/test.yaml")

def test_mainConfig_path() -> None:
    """
    Test the path attribute of the MainConfig class.
    """
    result = mainConfig.path
    assert result == "configs/test.yaml"

def test_mainConfig_content_type() -> None:
    """
    Test the content attribute type of the MainConfig class.
    """
    result = type(mainConfig.content)
    assert result == dict

def test_mainConfig_content_languages() -> None:
    """
    Test the content attribute languages.
    """
    result = mainConfig.getLanguages()
    assert set(result) == {
        "python",
        "php",
        "cpp"
    }

def test_mainConfig_content_scripts() -> None:
    """
    Test the content attribute scripts.
    """
    result = mainConfig.getScripts("python")
    assert set(result) == {
        "src/tests/test.py"
    }
    result = mainConfig.getScripts("php")
    assert set(result) == set({})

def test_mainConfig_content_functions() -> None:
    """
    Test the content attribute functions.
    """
    result = list(mainConfig.getFunctionsBody("python", "src/tests/test.py").keys())
    assert result ==  ["add", "subtract", "multiply"]

def test_mainConfig_content_functions_content_data() -> None:
    """
    Test the content attribute test data.
    """
    result = mainConfig.getFunctionsBody("python", "src/tests/test.py")["add"]
    assert result == [
        '1,2,3 -> 6',
        '4,5,6 -> 15',
        '-1,1,1 -> 1',
        '10,-10,5 -> 5',
        '0.5,0.5,0.5 -> 1.5',
        '0.5,-0.5,0.5 -> 0.5'
    ]

def test_mainConfig_content_functions_content_csv_path() -> None:
    """
    Test the content attribute csv path.
    """
    assert not mainConfig.isPointingToCsvFile("python", "src/tests/test.py", "add")
    assert mainConfig.isPointingToCsvFile("python", "src/tests/test.py", "multiply")

def test_typifying_test_case_line() -> None:
    """
    Test the typifying function for the test case line
    """
    result = mainConfig._typifyTestCaseToList("1,-2,3")
    assert result == [1, -2, 3]
    result2 = mainConfig._typifyTestCaseToList("1.1,2.2,-3.3")
    assert result2 == [1.1, 2.2, -3.3]
    result3 = mainConfig._typifyTestCaseToList("hello,world,!")
    assert result3 == ["hello", "world", "!"]

def test_mainConfig_content_functions_content_data_list() -> None:
    """
    Test the content attribute data list.
    """
    result = mainConfig.getTestData("python", "src/tests/test.py", "add")
    assert result == [
        ([1,2,3], [6]),
        ([4,5,6], [15]),
        ([-1,1,1], [1]),
        ([10,-10,5], [5]),
        ([0.5,0.5,0.5], [1.5]),
        ([0.5,-0.5,0.5], [0.5])
    ]
    result2 = mainConfig.getTestData("python", "src/tests/test.py", "multiply")
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
    result = mainConfig.getHooks()
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
                "src/tests/test.py": {
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
                "src/tests/test.py": {}
            },
            "php": {},
            "cpp": {}
        }
    }


def test_mainConfig_hooks_general_setup() -> None:
    """
    Test import general setup
    """
    result = mainConfig.getHookGeneral(HookType.GENERAL_SETUP)
    assert result.type == HookType.GENERAL_SETUP
    assert result.attributes == {"path": "a_random_path"}
    assert result.commands == []
    assert result.description == ""

def test_mainConfig_hooks_general_shutdown() -> None:
    """
    Test import general shutdown
    """
    result = mainConfig.getHookGeneral(HookType.GENERAL_SHUTDOWN)
    assert result.type == HookType.GENERAL_SHUTDOWN
    assert result.attributes == {}
    assert result.commands == []
    assert result.description == ""

def test_mainConfig_hooks_file_setup() -> None:
    """
    Test import file setup
    """
    result = mainConfig.getHookFile(HookType.FILE_SETUP, "python")
    assert result.type == HookType.FILE_SETUP
    assert result.attributes == {"path": "new_path_overrides_old_one"}
    assert result.commands == ["echo OVERRIDDEN"]
    assert result.description == ""

def test_mainConfig_hooks_file_shutdown() -> None:
    """
    Test import file shutdown
    """
    result = mainConfig.getHookFile(HookType.FILE_SHUTDOWN, "python")
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
    result = mainConfig.getHookFunction(HookType.FUNCTION_SETUP, "python", "src/tests/test.py")
    assert result.type == HookType.FUNCTION_SETUP
    assert result.attributes == {"path": "src/tests", "target": "add"}
    assert result.commands == []
    assert result.description == ""

def test_mainConfig_hooks_function_shutdown() -> None:
    """
    Test import function shutdown
    """
    result = mainConfig.getHookFunction(HookType.FUNCTION_SHUTDOWN, "python", "src/tests/test.py")
    assert result.type == HookType.FUNCTION_SHUTDOWN
    assert result.attributes == {}
    assert result.commands == []
    assert result.description == ""


langConfig = LangConfig("configs/lang/python.yaml")
def test_langConfig_config_variable_infix_char() -> None:
    """
    Test Config variable infix char getter
    """
    result = langConfig.getVariableInfixChar()
    assert result == "%"

def test_langConfig_config_variables() -> None:
    """
    Test Config variables getter
    """
    result = langConfig.getVariables()
    assert result == {
        "import_module": "%module%",
        "function_name": "%function_name%",
        "parameters": "%parameters%",
        "expected_result": "%expected_result%",
        "calculated_result": "%calculated_result%"
    }

def test_langConfig_header_data() -> None:
    """
    Test HeaderData getter.
    """
    result = langConfig.getHeaderData()
    assert result == [
        "import sys",
        "import %module%"
    ]

def test_langConfig_syntax_scheme() -> None:
    """
    Test TestSyntaxScheme getter.
    """
    result = langConfig.getTestSyntaxScheme()
    assert result == {
        "is_equal_test": "if %module%.%function_name%(%parameters%) == %expected_result%:",
        "is_unequal_test": "if %module%.%function_name%(%parameters%) != %expected_result%:",
    }

def test_langConfig_fail_message() -> None:
    """
    Test FailMessage getter
    """
    result = langConfig.getFailMessages()
    assert result == [
        "\tprint('[FAIL] %module%.%function_name%(%parameters%) != %expected_result%')",
        "\tsys.exit(1)"
    ]

def test_langConfig_hook_type_validator() -> None:
    """
    Test if all hook types in lang config file are valid
    """
    result = langConfig.hasValidHookTypes()
    assert result == True

def test_langConfig_hook_getter() -> None:
    """
    Test hook getter
    """
    result = langConfig.getHook(HookType.GENERAL_SETUP)
    assert result.type == HookType.GENERAL_SETUP
    assert result.attributes == {"env_name": ""}
    # assert result.commands == [
    #     "echo 'Installing Modules'",
    #     "source $env_name/bin/activate",
    #     "pip install -r src/requirements.txt >/dev/null 2>&1"
    # ]
    assert result.description == "Setup the environment before running the tests"

    result = langConfig.getHook(HookType.FUNCTION_SHUTDOWN)
    assert result.type == HookType.FUNCTION_SHUTDOWN
    assert result.attributes == {}
    assert result.commands == []
    assert result.description == "none"

def test_langConfig_config_execution_command() -> None:
    """
    Test config execution command getter
    """
    result = langConfig.getExecutionCommand("demo_file.py")
    assert result == "env/bin/python3 demo_file.py"

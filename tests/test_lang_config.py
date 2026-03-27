import mypy
import pytest

from src.config_parser import LangConfig
from src.hook import HookType


langConfig1 = LangConfig("../tests/configs/lang1/python.yaml")
langConfig2 = LangConfig("../tests/configs/lang2/python.yaml")

def test_langConfig_config_variable_infix_char() -> None:
    """
    Test Config variable infix char getter
    """
    result = langConfig1.getVariableInfixChar()
    assert result == "%"

def test_langConfig_config_variables() -> None:
    """
    Test Config variables getter
    """
    result = langConfig1.getVariables()
    assert result == {
        "import_module": "%module%",
        "function_name": "%function_name%",
        "generic_hash": "%generic_hash%",
        "file_path": "%file_path%",
        "function_index": "%function_index%",
        "parameters": "%parameters%",
        "expected_result": "%expected_result%",
        "module_name": "%module_name%",
        "calculated_result": "%calculated_result%",
        "custom_test_case": "%custom_test_case%"
    }

def test_syntax_scheme() -> None:
    """
    Test Syntax Scheme getter
    """
    result = langConfig1.getSyntaxScheme()
    assert result.keys() == {
        "header_data",
        "import_head",
        "single_test_code",
        "if_success",
        "if_failure"
    }

def test_langConfig_header_data() -> None:
    """
    Test HeaderData getter.
    """
    result = langConfig1.getHeaderData()
    assert result == [
        'import sys',
        'from pathlib import Path',
        'import importlib.util',
        '',
        'ROOT = Path(__file__).resolve().parents[1]',
        'sys.path.insert(0, str(ROOT))'
    ]
    result2 = langConfig2.getHeaderData()
    assert result2 == []

    result = LangConfig("../tests/configs/lang1/php.yaml").getHeaderData()
    assert result == []

    # result = LangConfig("../tests/configs/lang2/python.yaml").getHeaderData()
    # assert result == []

def test_import_head() -> None:
    """
    Test import head getter
    """
    result = LangConfig("../tests/configs/lang1/python.yaml").getImportHead()
    assert result == [
        'spec = importlib.util.spec_from_file_location("%module_name%", ROOT / "%file_path%")',
        '%module_name% = importlib.util.module_from_spec(spec) # type: ignore',
        'spec.loader.exec_module(%module_name%) # type: ignore'
    ]

def test_langConfig_footer_data() -> None:
    """
    Test Footer Data getter
    """
    langConfig4 = LangConfig("../tests/configs/lang4/php.yaml")
    result = langConfig4.getFooterData()
    assert result == [
        "",
        "?>"
    ]

    result = LangConfig("../tests/configs/lang1/php.yaml").getFooterData()
    assert result == []

def test_langConfig_syntax_scheme() -> None:
    """
    Test TestSyntaxScheme getter.
    """
    result = langConfig1.getTestSyntaxScheme()
    assert result == {
        "is_equal_test": {
            "scheme": "if %module_name%.%function_name%(%parameters%) == %expected_result%:"
        },
        "is_unequal_test": {
            "custom_scheme": "if %module_name%.%custom_test_case%:",
            "scheme": "if %module_name%.%function_name%(%parameters%) != %expected_result%:"
        },
    }

def test_langConfig_fail_message() -> None:
    """
    Test FailMessage getter
    """
    result = langConfig1.getDefaultFailMessages()
    assert result == [
        "\tprint('[FAIL] %file_path%#%function_name%(%parameters%) != %expected_result%')",
        "\tsys.exit(1)"
    ]
    result = langConfig1.getCustomFailMessages()
    assert result == [
        "\tprint('[FAIL] %custom_test_case%')"
    ]

def test_langConfig_hook_type_validator() -> None:
    """
    Test if all hook types in lang config file are valid
    """
    result = langConfig1.hasValidHookTypes()
    assert result == True

def test_langConfig_hook_getter() -> None:
    """
    Test hook getter
    """
    result = langConfig1.getHook(HookType.GENERAL_SETUP)
    assert result.type == HookType.GENERAL_SETUP
    assert result.attributes == {"env_name": ""}
    # assert result.commands == [
    #     "echo 'Installing Modules'",
    #     "source $env_name/bin/activate",
    #     "pip install -r src/requirements.txt >/dev/null 2>&1"
    # ]
    assert result.description == "Setup the environment before running the tests"

    result = langConfig1.getHook(HookType.FUNCTION_SHUTDOWN)
    assert result.type == HookType.FUNCTION_SHUTDOWN
    assert result.attributes == {}
    assert result.commands == []
    assert result.description == "none"

def test_langConfig_config_execution_command() -> None:
    """
    Test config execution command getter
    """
    result = langConfig1.getExecutionCommand("demo_file.py")
    assert result == "env/bin/python3 demo_file.py"

    result = LangConfig("../tests/configs/lang1/php.yaml").getExecutionCommand("")
    assert result == ""

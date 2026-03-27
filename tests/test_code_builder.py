import glob
import mypy
import pytest

from pathlib import Path

from src.config_parser import MainConfig, LangConfig
from src.file_builder import Script


cb = Script(MainConfig("../tests/configs/config1.yaml"), LangConfig( "../tests/configs/lang1/python.yaml"))
cb5 = Script(MainConfig("../tests/configs/config5.yaml"), LangConfig( "../tests/configs/lang1/python.yaml"))
cb5_2 = Script(MainConfig("../tests/configs/config5.yaml"), LangConfig( "../tests/configs/lang1/python.yaml"))


def test_hash_getter() -> None:
    """
    Test hash string getter.
    """
    assert Script.hash_string("") == "46b9dd2b"
    assert Script.hash_string("hello") == "1234075a"
    assert Script.hash_string("tests/code/test.py") == "81174737"

def test_build_import() -> None:
    """
    Test import getter
    """
    result = cb.getImports("python")
    assert result == [
        'import sys',
        'from pathlib import Path',
        'import importlib.util',
        '',
        'ROOT = Path(__file__).resolve().parents[1]',
        'sys.path.insert(0, str(ROOT))'
    ]

def test_build_function_head() -> None:
    """
    Test function head getter
    """
    result = cb.getFunctionHead("python", "test_module", "add", "[1,2,3]", "[6]")
    assert result == "if test_module.add([1,2,3]) != [6]:"

def test_build_function_body() -> None:
    """
    Test function body getter
    """
    result = cb.getFunctionBody("python", "add", "[1,2,3]", "[6]")
    assert result == [
        "\tprint('[FAIL] tests/code/test.py#add([1,2,3]) != [6]')",
        "\tsys.exit(1)"
    ]

def test_build_function_custom() -> None:
    """
    Test custom function getter
    """
    result = cb.getFunctionCustom("addAll", "[1,2,3,4,5,6]", "[21]", "addAll(x_n)==y_n")
    assert result == "addAll([1,2,3,4,5,6])==[21]"
    result = cb5.getFunctionCustom("getParam", "[5]", "[6]", "AClass(x_n).function()==y_n")
    assert result == "AClass([5]).getParam()==[6]"

def test_reference_head() -> None:
    """
    Test reference head getter
    """

    assert cb5.mainConfig._isCodeFileValid("tests/code/test.py", "tests/configs/config5.py")

    assert not cb5.mainConfig.hasCustomVariable("python", "VAR_cd44d591")
    result = cb5.getReferenceHead("python", "tests/code/test.py", "complex_test")
    assert cb5.mainConfig.hasCustomVariable("python", "VAR_cd44d591")

    assert result == ([
        'spec = importlib.util.spec_from_file_location("VAR_cd44d591", ROOT / "tests/configs/config5.py")',
        'VAR_cd44d591 = importlib.util.module_from_spec(spec) # type: ignore',
        'spec.loader.exec_module(VAR_cd44d591) # type: ignore',
        "",
    ], "VAR_cd44d591")

    result2 = cb5.getReferenceHead("python", "tests/code/test.py", "complex_test")
    assert cb5.mainConfig.hasCustomVariable("python", "VAR_cd44d591")
    assert result2 == ([], "VAR_cd44d591")

def test_build_function() -> None:
    """
    Test function getter
    """
    result = cb5_2.getFunction("python", "tests/code/test.py", "add", "[1,2,3]", "[6]")
    assert result == [
        'spec = importlib.util.spec_from_file_location("VAR_81174737", ROOT / "tests/code/test.py")',
        'VAR_81174737 = importlib.util.module_from_spec(spec) # type: ignore',
        'spec.loader.exec_module(VAR_81174737) # type: ignore',
        "",
        "if VAR_81174737.add([1,2,3]) != [6]:",
        "\tprint('[FAIL] tests/code/test.py#VAR_81174737.add([1,2,3]) != [6]')",
        "\tsys.exit(1)",
        ""
    ]
    result = cb5_2.getFunction("python", "tests/code/test.py", "addAll", "[1,2,3,4,5,6]", "[21]", "if VAR_81174737.addAll(x_n) != y_n:")
    # TODO: fix this test case to pass
    # assert result == [
    #     "if VAR_81174737.addAll([1,2,3,4,5,6]) != [21]:",
    #     "\tprint('[FAIL] if VAR_81174737.addAll([1,2,3,4,5,6]) != [21]:')",
    #     ""
    # ]
    result = cb5_2.getFunction("python", "tests/code/test.py", "getParam", "[5]", "[6]", "if VAR_81174737.AClass(x_n).function()==y_n:")
    # TODO: fix this test case to pass
    # assert result == [
    #     "if VAR_81174737.AClass([5]).getParam()==[6]:",
    #     "\tprint('[FAIL] if VAR_81174737.AClass([5]).getParam()==[6]:')",
    #     ""
    # ]

    assert cb5_2.mainConfig.custom_module_variables == {
        'cpp': [],
        'php': [],
        'python': [
            'VAR_81174737'
        ],
    }

    result = cb5_2.getFunction("python", "tests/code/test.py", "complex_test", "[]", "[True]")
    assert cb5_2.mainConfig.custom_module_variables == {
        'cpp': [],
        'php': [],
        'python': [
            'VAR_81174737',
            'VAR_cd44d591'
        ],
    }
    assert result == [
        'spec = importlib.util.spec_from_file_location("VAR_cd44d591", ROOT / "tests/configs/config5.py")',
        'VAR_cd44d591 = importlib.util.module_from_spec(spec) # type: ignore',
        'spec.loader.exec_module(VAR_cd44d591) # type: ignore',
        "",
        "if VAR_cd44d591.complex_test([]) != [True]:",
        "\tprint('[FAIL] tests/code/test.py#VAR_cd44d591.complex_test([]) != [True]')",
        "\tsys.exit(1)",
        '',
    ]

def test_build_all_tests_of_function() -> None:
    """
    Test get all test of function
    """
    result = cb.getAllTestsOfFunction("python", "tests/code/test.py", "subtract")
    assert result == [
        'spec = importlib.util.spec_from_file_location("VAR_81174737", ROOT / '
        '"tests/code/test.py")',
        'VAR_81174737 = importlib.util.module_from_spec(spec) # type: ignore',
        'spec.loader.exec_module(VAR_81174737) # type: ignore',
        '',
        "if VAR_81174737.subtract(10, 5) != 5:",
        "\tprint('[FAIL] tests/code/test.py#VAR_81174737.subtract(10, 5) != 5')",
        "\tsys.exit(1)",
        ""
    ]
    cb5.mainConfig.clearAllCustomVariables()
    result5 = cb5.getAllTestsOfFunction("python", "tests/code/test.py", "addAll")
    assert result5 == [
        'spec = importlib.util.spec_from_file_location("VAR_81174737", ROOT / '
        '"tests/code/test.py")',
        'VAR_81174737 = importlib.util.module_from_spec(spec) # type: ignore',
        'spec.loader.exec_module(VAR_81174737) # type: ignore',
        '',
        'if VAR_81174737.addAll(1,2,3,4,5,6)==21:',
        "\tprint('[FAIL] addAll(1,2,3,4,5,6)==21')",
        ''
    ]
    assert cb5.mainConfig.custom_module_variables == {
        'cpp': [],
        'php': [],
        'python': [
            'VAR_81174737'
        ],
    }
    result5 = cb5.getAllTestsOfFunction("python", "tests/code/test.py", "complex_test")
    assert result5 == [
        'spec = importlib.util.spec_from_file_location("VAR_cd44d591", ROOT / '
        '"tests/configs/config5.py")',
        'VAR_cd44d591 = importlib.util.module_from_spec(spec) # type: ignore',
        'spec.loader.exec_module(VAR_cd44d591) # type: ignore',
        '',
        'if VAR_cd44d591.complex_test() != True:',
        "\tprint('[FAIL] tests/code/test.py#VAR_cd44d591.complex_test() != True')",
        '\tsys.exit(1)',
        ''
    ]

def test_build_all_tests_python() -> None:
    """
    Test build all tests getter for python
    """
    result = cb.getAllTests("python")
    assert result == [
        'import sys',
        'from pathlib import Path',
        'import importlib.util',
        '',
        'ROOT = Path(__file__).resolve().parents[1]',
        'sys.path.insert(0, str(ROOT))',
        '',
        '',
        'spec = importlib.util.spec_from_file_location("VAR_81174737", ROOT / '
        '"tests/code/test.py")',
        'VAR_81174737 = importlib.util.module_from_spec(spec) # type: ignore',
        'spec.loader.exec_module(VAR_81174737) # type: ignore',
        '',
        'if VAR_81174737.add(1, 2, 3) != 6:',
        "\tprint('[FAIL] tests/code/test.py#VAR_81174737.add(1, 2, 3) != 6')",
        '\tsys.exit(1)',
        '',
        'if VAR_81174737.add(4, 5, 6) != 15:',
        "\tprint('[FAIL] tests/code/test.py#VAR_81174737.add(4, 5, 6) != 15')",
        '\tsys.exit(1)',
        '',
        'if VAR_81174737.add(-1, 1, 1) != 1:',
        "\tprint('[FAIL] tests/code/test.py#VAR_81174737.add(-1, 1, 1) != 1')",
        '\tsys.exit(1)',
        '',
        'if VAR_81174737.add(10, -10, 5) != 5:',
        "\tprint('[FAIL] tests/code/test.py#VAR_81174737.add(10, -10, 5) != 5')",
        '\tsys.exit(1)',
        '',
        'if VAR_81174737.add(0.5, 0.5, 0.5) != 1.5:',
        "\tprint('[FAIL] tests/code/test.py#VAR_81174737.add(0.5, 0.5, 0.5) != "
        "1.5')",
        '\tsys.exit(1)',
        '',
        'if VAR_81174737.add(0.5, -0.5, 0.5) != 0.5:',
        "\tprint('[FAIL] tests/code/test.py#VAR_81174737.add(0.5, -0.5, 0.5) != "
        "0.5')",
        '\tsys.exit(1)',
        '',
        'if VAR_81174737.subtract(10, 5) != 5:',
        "\tprint('[FAIL] tests/code/test.py#VAR_81174737.subtract(10, 5) != 5')",
        '\tsys.exit(1)',
        '',
        'if VAR_81174737.multiply(7,8,9) != 504:',
        "\tprint('[FAIL] tests/code/test.py#VAR_81174737.multiply(7,8,9) != 504')",
        '\tsys.exit(1)',
        '',
        'if VAR_81174737.multiply(10,11,12) != 1320:',
        "\tprint('[FAIL] tests/code/test.py#VAR_81174737.multiply(10,11,12) != "
        "1320')",
        '\tsys.exit(1)',
        '',
        'if VAR_81174737.multiply(-1,10,1) != -10:',
        "\tprint('[FAIL] tests/code/test.py#VAR_81174737.multiply(-1,10,1) != "
        "-10')",
        '\tsys.exit(1)',
        '',
        'if VAR_81174737.multiply(0.5,10,-1) != -5.0:',
        "\tprint('[FAIL] tests/code/test.py#VAR_81174737.multiply(0.5,10,-1) != "
        "-5.0')",
        '\tsys.exit(1)',
        '',
    ]


cb4 = Script(MainConfig("../tests/configs/config4.yaml"), LangConfig( "../tests/configs/lang4/php.yaml"))
def test_build_all_tests_php() -> None:
    """
    Test build all tests getter for php
    """
    result = cb4.getAllTests("php")
    assert result == [
        '<?php',
        "include 'tests/code/test.php';",
        '',
        '',
        '',
        '',
        'if (add(1, 2, 3) != 6) {throw new Exception("Test Failed");}',
        '',
        'if (add(4, 5, 6) != 15) {throw new Exception("Test Failed");}',
        '',
        'if (add(-1, 1, 1) != 1) {throw new Exception("Test Failed");}',
        '',
        'if (add(10, -10, 5) != 5) {throw new Exception("Test Failed");}',
        '',
        'if (add(0.5, 0.5, 0.5) != 1.5) {throw new Exception("Test Failed");}',
        '',
        'if (add(0.5, -0.5, 0.5) != 0.5) {throw new Exception("Test Failed");}',
        '',
        'if (subtract(10, 5) != 5) {throw new Exception("Test Failed");}',
        '',
        'if (multiply(7,8,9) != 504) {throw new Exception("Test Failed");}',
        '',
        'if (multiply(10,11,12) != 1320) {throw new Exception("Test Failed");}',
        '',
        'if (multiply(-1,10,1) != -10) {throw new Exception("Test Failed");}',
        '',
        'if (multiply(0.5,10,-1) != -5.0) {throw new Exception("Test Failed");}',
        '',
        '',
        '?>',
    ]

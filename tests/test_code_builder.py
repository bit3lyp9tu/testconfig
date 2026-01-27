import mypy
import pytest

from src.file_builder import CodeBuilder


cb = CodeBuilder("../tests/configs/config1.yaml", "../tests/configs/lang1/python.yaml")

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
        'module_path = ROOT / "tests/code/test.py"',
        '',
        'spec = importlib.util.spec_from_file_location("test_module",module_path)',
        'test_module = importlib.util.module_from_spec(spec) # type: ignore',
        'spec.loader.exec_module(test_module) # type: ignore',
    ]

def test_build_function_head() -> None:
    """
    Test function head getter
    """
    result = cb.getFunctionHead("python", "add", [1,2,3], [6])
    assert result == "if test_module.add(1,2,3) != 6:"

def test_build_function_body() -> None:
    """
    Test function body getter
    """
    result = cb.getFunctionBody("python", "add", [1,2,3], [6])
    assert result == [
        "\tprint('[FAIL] tests/code/test.py#add(1,2,3) != 6')",
        "\tsys.exit(1)"
    ]

def test_build_function() -> None:
    """
    Test function getter
    """
    result = cb.getFunction("python", "add", [1,2,3], [6])
    assert result == [
        "if test_module.add(1,2,3) != 6:",
        "\tprint('[FAIL] tests/code/test.py#add(1,2,3) != 6')",
        "\tsys.exit(1)",
        ""
    ]

def test_build_all_tests_of_function() -> None:
    """
    Test get all test of function
    """
    result = cb.getAllTestsOfFunction("python", "subtract")
    assert result == [
        "if test_module.subtract(10,5) != 5:",
        "\tprint('[FAIL] tests/code/test.py#subtract(10,5) != 5')",
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
        'from pathlib import Path',
        'import importlib.util',
        '',
        'ROOT = Path(__file__).resolve().parents[1]',
        'module_path = ROOT / "tests/code/test.py"',
        '',
        'spec = importlib.util.spec_from_file_location("test_module",module_path)',
        'test_module = importlib.util.module_from_spec(spec) # type: ignore',
        'spec.loader.exec_module(test_module) # type: ignore',
        '',
        'if test_module.add(1,2,3) != 6:',
        "\tprint('[FAIL] tests/code/test.py#add(1,2,3) != 6')",
        '\tsys.exit(1)',
        '',
        'if test_module.add(4,5,6) != 15:',
        "\tprint('[FAIL] tests/code/test.py#add(4,5,6) != 15')",
        '\tsys.exit(1)',
        '',
        'if test_module.add(-1,1,1) != 1:',
        "\tprint('[FAIL] tests/code/test.py#add(-1,1,1) != 1')",
        '\tsys.exit(1)',
        '',
        'if test_module.add(10,-10,5) != 5:',
        "\tprint('[FAIL] tests/code/test.py#add(10,-10,5) != 5')",
        '\tsys.exit(1)',
        '',
        'if test_module.add(0.5,0.5,0.5) != 1.5:',
        "\tprint('[FAIL] tests/code/test.py#add(0.5,0.5,0.5) != 1.5')",
        '\tsys.exit(1)',
        '',
        'if test_module.add(0.5,-0.5,0.5) != 0.5:',
        "\tprint('[FAIL] tests/code/test.py#add(0.5,-0.5,0.5) != 0.5')",
        '\tsys.exit(1)',
        '',
        'if test_module.subtract(10,5) != 5:',
        "\tprint('[FAIL] tests/code/test.py#subtract(10,5) != 5')",
        '\tsys.exit(1)',
        '',
        'if test_module.multiply(7,8,9) != 504:',
        "\tprint('[FAIL] tests/code/test.py#multiply(7,8,9) != 504')",
        '\tsys.exit(1)',
        '',
        'if test_module.multiply(10,11,12) != 1320:',
        "\tprint('[FAIL] tests/code/test.py#multiply(10,11,12) != 1320')",
        '\tsys.exit(1)',
        '',
        'if test_module.multiply(-1,10,1) != -10:',
        "\tprint('[FAIL] tests/code/test.py#multiply(-1,10,1) != -10')",
        '\tsys.exit(1)',
        '',
        'if test_module.multiply(0.5,10,-1) != -5.0:',
        "\tprint('[FAIL] tests/code/test.py#multiply(0.5,10,-1) != -5.0')",
        '\tsys.exit(1)',
        '',
    ]

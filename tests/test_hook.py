import mypy
import pytest

from src.hook import Hook, HookType


def test_hook_eq() -> None:
    """
    Test equal magic method of hook
    """
    assert Hook(HookType.GENERAL_SETUP, {}) != Hook(HookType.GENERAL_SHUTDOWN, {})
    assert Hook(HookType.GENERAL_SETUP, {}) != ""

    result = Hook(HookType.GENERAL_SETUP, {"attributes": ["aa", "bb", "cc"]})
    assert result.toDict() == {
        "attributes": {
            "a": "",
            "b": "",
            "c": ""
        }
    }

import os

import mypy
import pytest

from pathlib import Path

from src.config_parser import ConfigStructure
from src.hook import HookType


cs = ConfigStructure()

def test_config_structure_add_general() -> None:
    """
    Test adding new data into general
    """
    cs.addGeneral(HookType.GENERAL_SETUP, {
        'attributes': {
            'general': 'general_variable',
        },
        'commands': [
            'echo $general',
            'echo $file',
            'echo $function',
        ],
    })
    assert cs.data == {
        'general_setup': {
            'attributes': {
                'general': 'general_variable',
            },
            'commands': [
                'echo $general',
                'echo $file',
                'echo $function',
            ],
        },
        'general_shutdown': {
            'attributes': {
                'general': 'general_variable',
            }
        },
        'file_setup': {},
        'file_shutdown': {},
        'function_setup': {},
        'function_shutdown': {},
    }
    cs.addGeneral(HookType.GENERAL_SHUTDOWN, {
        'attributes': {
            'general': 'general_variable_override',
        },
        'commands': [
            'echo $general',
            'echo $file',
            'echo $function',
            'echo test'
        ],
    })
    assert cs.data == {
        'general_setup': {
            'attributes': {
                'general': 'general_variable',
            },
            'commands': [
                'echo $general',
                'echo $file',
                'echo $function',
            ],
        },
        'general_shutdown': {
            'attributes': {
                'general': 'general_variable_override',
            },
            'commands': [
                'echo $general',
                'echo $file',
                'echo $function',
                'echo test'
            ],
        },
        'file_setup': {},
        'file_shutdown': {},
        'function_setup': {},
        'function_shutdown': {},
    }

    cs2 = ConfigStructure()
    cs2.addGeneral(HookType.GENERAL_SETUP, {
        'attributes': {
                'general': 'general_variable',
            },
            'commands': [
                'echo $general',
                'echo $file',
                'echo $function',
        ],
    })
    assert cs2.data == {
        'general_setup': {
            'attributes': {
                'general': 'general_variable',
            },
            'commands': [
                'echo $general',
                'echo $file',
                'echo $function',
            ],
        },
        'general_shutdown': {
            'attributes': {
                'general': 'general_variable',
            }
        },
        'file_setup': {},
        'file_shutdown': {},
        'function_setup': {},
        'function_shutdown': {},
    }

    cs3 = ConfigStructure()
    cs3.addGeneral(HookType.GENERAL_SHUTDOWN, {
        'attributes': {
                'general': 'general_variable',
            },
            'commands': [
                'echo $general',
                'echo $file',
                'echo $function',
            ],
    })
    assert cs3.data == {
        'general_setup': {},
        'general_shutdown': {
            'attributes': {
                'general': 'general_variable',
            },
            'commands': [
                'echo $general',
                'echo $file',
                'echo $function',
            ],
        },
        'file_setup': {},
        'file_shutdown': {},
        'function_setup': {},
        'function_shutdown': {},
    }

def test_config_structure_add_file() -> None:
    """
    Test adding new data into file
    """
    cs.addFile(HookType.FILE_SETUP, "python", {
        'attributes': {
            'general': 'general_variable',
            'file': 'file_variable'
        },
        'commands': [
            'echo $general',
            'echo $file',
            'echo $function',
        ],
    })
    assert cs.data == {
        'general_setup': {
            'attributes': {
                'general': 'general_variable',
            },
            'commands': [
                'echo $general',
                'echo $file',
                'echo $function',
            ],
        },
        'general_shutdown': {
            'attributes': {
                'general': 'general_variable_override',
            },
            'commands': [
                'echo $general',
                'echo $file',
                'echo $function',
                'echo test'
            ],
        },
        'file_setup': {
            'python': {
                'attributes': {
                    'general': 'general_variable',
                    'file': 'file_variable'
                },
                'commands': [
                    'echo $general',
                    'echo $file',
                    'echo $function',
                ],
            },
        },
        'file_shutdown': {
            'python': {
                'attributes': {
                    'general': 'general_variable',
                    'file': 'file_variable'
                },
            }
        },
        'function_setup': {},
        'function_shutdown': {},
    }

def test_config_structure_add_function() -> None:
    """
    Test adding new data into function
    """
    cs.addFunction(HookType.FUNCTION_SETUP, "python", "tests/code/test.py", {
        'attributes': {
            'general': 'general_variable',
            'file': 'file_variable',
            'function': 'function_variable',
        },
        'commands': [
            'echo $general',
            'echo $file',
            'echo $function',
        ],
    })
    assert cs.data == {
        'general_setup': {
            'attributes': {
                'general': 'general_variable',
            },
            'commands': [
                'echo $general',
                'echo $file',
                'echo $function',
            ],
        },
        'general_shutdown': {
            'attributes': {
                'general': 'general_variable_override',
            },
            'commands': [
                'echo $general',
                'echo $file',
                'echo $function',
                'echo test'
            ],
        },
        'file_setup': {
            'python': {
                'attributes': {
                    'general': 'general_variable',
                    'file': 'file_variable'
                },
                'commands': [
                    'echo $general',
                    'echo $file',
                    'echo $function',
                ],
            },
        },
        'file_shutdown': {
            'python': {
                'attributes': {
                    'general': 'general_variable',
                    'file': 'file_variable'
                }
            },
        },
        'function_setup': {
            'python': {
                'tests/code/test.py': {
                    'attributes': {
                        'general': 'general_variable',
                        'file': 'file_variable',
                        'function': 'function_variable',
                    },
                    'commands': [
                        'echo $general',
                        'echo $file',
                        'echo $function',
                    ],
                },
            },
        },
        'function_shutdown': {
                        'python': {
                'tests/code/test.py': {
                    'attributes': {
                        'general': 'general_variable',
                        'file': 'file_variable',
                        'function': 'function_variable',
                    }
                },
            },
        },
    }

def test_config_structure_overriding() -> None:
    """
    Test if config structure gets correctly overridden
    """
    cs3_2 = ConfigStructure()
    cs3_2.addGeneral(HookType.GENERAL_SETUP, {
        'attributes': {
            'general': 'general_variable',
        },
        'commands': [
            'echo $general',
            'echo $file',
            'echo $function',
        ],
    })
    cs3_2.addGeneral(HookType.GENERAL_SHUTDOWN, {
        'commands': [
            'echo $general',
            'echo $file',
            'echo $function',
        ],
    })
    assert cs3_2.data == {
        "general_setup": {
            'attributes': {
                'general': 'general_variable',
            },
            'commands': [
                'echo $general',
                'echo $file',
                'echo $function',
            ],
        },
        "general_shutdown": {
            'attributes': {
                'general': 'general_variable',
            },
            'commands': [
                'echo $general',
                'echo $file',
                'echo $function',
            ],
        },
        "file_setup": {},
        "file_shutdown": {},
        "function_setup": {},
        "function_shutdown": {}
    }


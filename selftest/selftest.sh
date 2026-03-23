#!/bin/bash

env/bin/python3 -m src.prototype \
            --config ../selftest/config.yaml \
            --lang_config_dict ../selftest/lang \
            --test_path selftest \
            --debug_level 0 \
            --keep_script_files true

#!/bin/bash

source env/bin/activate
pip install -r src/requirements.txt >/dev/null 2>&1

env/bin/python3 src/config_parser.py

echo "Build File"
env/bin/python3 src/prototype.py
# sleep 1
echo "Run File"
chmod +x ./src/demofile.py
env/bin/python3 ./src/demofile.py
echo ---
rm ./src/demofile.py

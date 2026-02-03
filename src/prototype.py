import sys
import argparse

from pathlib import Path

from file_builder import Writer, RunController, LogLevel

LOG4 = LogLevel(4, "[FATAL]", "dark_orange3")

parser = argparse.ArgumentParser(description='Run pre configured test suites.')

parser.add_argument(
    "-c", "--config", help="set the main .yaml configuration file", type=str, default="configs/test.yaml"
)
parser.add_argument(
    "-l", "--lang_config_dict",
    help="set the directory for language specific configurations .yaml files", type=str, default="configs/lang"
)
parser.add_argument(
    "-t", "--test_path", help="set the directory for the test suite", type=str, default="src"
)
parser.add_argument(
    "-k", "--keep_script_files", help="keep the generated script files from being deleted after execution", type=bool, default=True
)
parser.add_argument(
    "-r", "--report", help="set the name of the output file for the test report", type=str, default="test_report.txt"
)

args = parser.parse_args()

tester = RunController(args.config, args.lang_config_dict)
Writer(tester.start(args.test_path, bool(args.keep_script_files))).write(args.report)
# try:
# except Exception as e:
#     print(f"{e}")

# python3 test.py (./test.py oder source pip install test)
# -> innerhalb des python codes:
#   -> generiert er als erstes das skript
#   -> führt es dann mit subprocess oder so aus
# -> INNERHALB dieser test.py
# print(f"[FAIL] {testname} failed")

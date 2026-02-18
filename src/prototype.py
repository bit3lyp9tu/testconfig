import sys
import argparse

from pathlib import Path

from file_builder import Writer
from run_controller import RunController
from log_level import LogLevel, LogLevels


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
parser.add_argument(
    "-d", "--debug_level", help="choose between different log levels (the higher the number, the more detailed the output)", type=int, default=0
)

args = parser.parse_args()

LOGS = LogLevels(
    args.debug_level,
    LogLevel(1, "[INFO]", "dodger_blue2"),
    LogLevel(2, "[WARN]", "yellow1"),
    LogLevel(3, "[ERROR]", "bright_red"),
    LogLevel(4, "[FATAL]", "black on red")
)

try:
    tester = RunController(
        args.config,
        args.lang_config_dict,
        LOGS
    )
    Writer(
        tester.start(
            args.test_path,
            bool(args.keep_script_files)
        )
    ).write(args.report, False)

except Exception as e:
    LOGS.print(4, f"{e}")

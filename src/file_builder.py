import os
import re

import subprocess

from contextlib import contextmanager

from rich import print
from rich.progress import Progress
from rich.traceback import install

from config_parser import MainConfig, LangConfig
from hook import Hook

class Script:
    def __init__(self, config: MainConfig, lang_config: LangConfig) -> None:
        self.mainConfig: MainConfig = config
        self.langConfig: LangConfig = lang_config

    def getImports(self, language: str) -> list[str]:
        result: list[str] = []

        script_path = self.mainConfig.getScripts(language)[0]

        variables = self.langConfig.getVariables()
        infix = self.langConfig.getVariableInfixChar()

        modules = self.langConfig.getHeaderData()
        for module in modules:
            header = module.replace(
                variables["file_path"].replace(infix, ""),
                script_path
            ).replace(
                infix,
                ""
            )
            result.append(header)

        return result

    def getFunctionHead(self, language: str, function_name: str, parameters: list[str|int|float], expected_result: list[str|int|float]) -> str:
        variables = self.langConfig.getVariables()

        scheme = self.langConfig.getTestSyntaxScheme()["is_unequal_test"]
        test_header = scheme.replace(
            f"{variables["function_name"]}",
            function_name
        ).replace(
            f"{variables["parameters"]}",
            ",".join(str(i) for i in parameters)
        ).replace(
            f"{variables["expected_result"]}",
            str(expected_result[0])
        )
        return test_header

    def getFunctionBody(self, language: str, function_name: str, parameters: list[str|int|float], expected_result: list[str|int|float]) -> list[str]:
        result: list[str] = []

        script_path = self.mainConfig.getScripts(language)[0]

        fail_msg_lines = self.langConfig.getFailMessages()

        variables = self.langConfig.getVariables()

        for fail_msg in fail_msg_lines:
            test_body = fail_msg.replace(
                f"{variables["file_path"]}",
                script_path
            ).replace(
                f"{variables["function_name"]}",
                function_name
            ).replace(
                f"{variables["parameters"]}",
                ",".join(str(i) for i in parameters)
            ).replace(
                f"{variables["expected_result"]}",
                str(expected_result[0])
            )
            result.append(test_body)

        return result

    def getFunction(self, language: str, function_name: str, parameters: list[str|int|float], expected_result: list[str|int|float]) -> list[str]:
        result: list[str] = []

        result.append(self.getFunctionHead(language, function_name, parameters, expected_result))
        result.extend(self.getFunctionBody(language, function_name, parameters, expected_result))

        result.append("")

        return result

    def getAllTestsOfFunction(self, language: str, function_name: str) -> list[str]:
        result: list[str] = []

        script_path = self.mainConfig.getScripts(language)

        data = self.mainConfig.getTestData(language, script_path[0], function_name)
        # test block
        for single_test in data:
            parameters, expected_result = single_test

            result.extend(self.getFunction(language, function_name, parameters, expected_result))

        return result

    def getAllTests(self, language: str) -> list[str]:
        result: list[str] = []

        script_path = self.mainConfig.getScripts(language)

        result.extend(self.getImports(language))

        result.append("")

        function_names = list(self.mainConfig.getFunctionsBody(language, script_path[0]).keys())
        for function_name in function_names:
            result.extend(self.getAllTestsOfFunction(language, function_name))

        result.extend(self.langConfig.getFooterData())

        return result

    def build(self, lang: str) -> list[str]:
        result: list[str] = []

        result.extend(self.getAllTests(lang))

        return result


@contextmanager
def temp_environ(vars: dict):
    old = os.environ.copy()
    os.environ.update(vars)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old)

class Writer:
    def __init__(self, lines: list[str] = []) -> None:
        self.lines = lines

    def write(self, script_path, print_lines: bool = True) -> None:
        with open(script_path, "w") as f:
            for line in self.lines:
                if print_lines:
                    print(line)
                f.writelines(line + "\n")

    @classmethod
    def runCommand(cls, command: str, env_vars: dict = {}) -> tuple[list[str], int]:
        if command == "":
            return [], 0

        for match in re.findall(r'\$[^\s]*', command):
            if match[1:] not in env_vars:
                return [f"Missing environment variable: [{match}]"], 1

        env = os.environ.copy()
        env.update(env_vars)

        with temp_environ(env_vars):
            expanded = os.path.expandvars(command)

        try:
            process = subprocess.run(expanded.split(), capture_output=True, text=True, check=True, env=env)
            return process.stdout.split("\n"), process.returncode

        except subprocess.CalledProcessError as e:
            return e.stderr.split("\n"), e.returncode
        except FileNotFoundError as e:
            return [str(e)], 127

    @classmethod
    def runHook(cls, hook: Hook) -> tuple[list[str], int]:
        log: list[str] = []
        return_code = 0

        for command in hook.commands:
            output, code = cls.runCommand(command, hook.attributes)
            log.extend(output[:-1] if output[-1] == "" else output)
            if code != 0:
                return_code = code

        return log, return_code

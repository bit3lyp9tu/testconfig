import os
import re

import subprocess

import hashlib

from contextlib import contextmanager

from rich.progress import Progress
from rich.traceback import install

from .config_parser import MainConfig, LangConfig
from .hook import Hook

class Script:
    def __init__(self, config: MainConfig, lang_config: LangConfig) -> None:
        self.mainConfig: MainConfig = config
        self.langConfig: LangConfig = lang_config

    @classmethod
    def hash_string(cls, s: str = "", hex_length: int = 4) -> str:
        return hashlib.shake_256(s.encode('utf-8')).hexdigest(hex_length)

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

    def getFunctionHead(
            self,
            language: str,
            module_name: str,
            function_name: str,
            parameters: str,
            expected_result: str,
            function_index: int = 0,
            hash: str = "",
            custom_test_case: str = ""
        ) -> str:
        scheme: dict = self.langConfig.getTestSyntaxScheme()["is_unequal_test"]
        mode = scheme.get("custom_scheme", "") if custom_test_case != "" else scheme.get("scheme", "")

        test_header = mode.replace(
            f"{self.langConfig.getVariable("module_name")}",
            module_name
        ).replace(
            f"{self.langConfig.getVariable("function_name")}",
            function_name
        ).replace(
            f"{self.langConfig.getVariable("function_index")}",
            f"{function_index}"
        ).replace(
            f"{self.langConfig.getVariable("parameters")}",
            parameters
        ).replace(
            f"{self.langConfig.getVariable("expected_result")}",
            expected_result
        ).replace(
            f"{self.langConfig.getVariable("generic_hash")}",
            hash
        ).replace(
            f"{self.langConfig.getVariable("custom_test_case")}",
            custom_test_case
        )
        return test_header

    def getFunctionCustom(self, function_name: str, parameters: str, expected_result: str, custom_syntax: str) -> str:
        function = "function"
        x_n = "x_n"
        y_n = "y_n"

        return f"{custom_syntax.replace(
            x_n,
            parameters
        ).replace(
            y_n,
            expected_result
        ).replace(
            function,
            function_name
        )}"

    def getFunctionBody(self, language: str, function_name: str, parameters: str, expected_result: str, custom_syntax: str = "", function_index: int = 0, hash: str = "") -> list[str]:
        result: list[str] = []

        script_path = self.mainConfig.getScripts(language)[0]

        fail_msg_lines = self.langConfig.getDefaultFailMessages()
        if custom_syntax != "":
            fail_msg_lines = self.langConfig.getCustomFailMessages()

        variables = self.langConfig.getVariables()

        for fail_msg in fail_msg_lines:
            if custom_syntax != "":
                function = "function"
                x_n = "x_n"
                y_n = "y_n"

                result.append(fail_msg.replace(
                    f"{variables["custom_test_case"]}",
                    f"{custom_syntax.replace(
                        x_n,
                        parameters
                    ).replace(
                        y_n,
                        expected_result
                    ).replace(
                        function,
                        function_name
                )}"))

            else:
                test_body = fail_msg.replace(
                    f"{variables["file_path"]}",
                    script_path
                ).replace(
                    f"{variables["function_name"]}",
                    function_name
                ).replace(
                    f"{self.langConfig.getVariable("function_index")}",
                    f"{function_index}"
                ).replace(
                    f"{variables["parameters"]}",
                    parameters
                ).replace(
                    f"{variables["expected_result"]}",
                    expected_result
                ).replace(
                    f"{self.langConfig.getVariable("generic_hash")}",
                    hash
                )
                result.append(f"{test_body}")
        return result

    def getReferenceHead(self, language: str, script_path: str, function_name: str) -> tuple[list[str], str]:
        result: list[str] = []

        function_module = ""
        code_file = ""
        code_file = self.mainConfig._getCodeFile(language, script_path, function_name)

        if not self.mainConfig._hasCodeFile(language, script_path, function_name):
            # use structure from code file
            code_file = script_path

        variable: str = f"VAR_{self.hash_string(code_file)}"
        # TODO: check if hash already exist in code-file --> if yes, concatenate recursively additional hashes
        function_module = variable

        if self.mainConfig._isCodeFileValid(script_path, code_file):
            # append import (from import references in config)

            # check if variable didn't already exist
            if not self.mainConfig.hasCustomVariable(language, variable):
                self.mainConfig.addCustomVariable(language, variable)

                # generate import header (use lang-config), replace path with own path and - replace old variable with hashed value
                result.extend(self.langConfig.getModifiedImportHead(code_file, variable))
                result.append("")

        return result, function_module

    def getFunction(
            self,
            language: str,
            script_path: str,
            function_name: str,
            parameters: str,
            expected_result: str,
            custom_syntax: str = "",
            index: int = 0
        ) -> list[str]:

        result: list[str] = []

        hash = self.hash_string(f"{language}:{script_path}:{function_name}:{index}", hex_length=8)

        reference_lines, module_variable = self.getReferenceHead(language, script_path, function_name)
        result.extend(reference_lines)

        function_head = self.getFunctionHead(
            language,
            module_variable,
            function_name,
            parameters,
            expected_result,
            index,
            hash,
            self.getFunctionCustom(function_name, parameters, expected_result, custom_syntax) if custom_syntax != "" else ""
        )

        result.append(function_head)
        result.extend(self.getFunctionBody(
            language,
            f"{ "" if custom_syntax != "" else (module_variable + ".")}{function_name}",
            parameters,
            expected_result,
            custom_syntax,
            index,
            hash
        ))
        result.append("")

        return result

    def getAllTestsOfFunction(self, language: str, script_path: str, function_name: str) -> list[str]:
        result: list[str] = []

        data = self.mainConfig.getTestData(language, script_path, function_name)
        # test block
        for index in range(len(data)):
            parameters, expected_result, custom_syntax = data[index]

            result.extend(self.getFunction(language, script_path, function_name, parameters, expected_result, index=index, custom_syntax=custom_syntax))

        return result

    def getAllTests(self, language: str) -> list[str]:
        result: list[str] = []

        script_paths = self.mainConfig.getScripts(language)

        result.extend(self.getImports(language))

        result.append("")

        for script_path in script_paths:    # TODO: needs testing
            function_names = list(self.mainConfig.getFunctionsBody(language, script_path).keys())

            result.append("")
            result.extend(self.langConfig.getModifiedImportHead(script_path, f"VAR_{self.hash_string(script_path)}"))
            result.append("")

            for function_name in function_names:
                result.extend(self.getAllTestsOfFunction(language, script_path, function_name))

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


class CommandRunner:

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
            process = subprocess.run(expanded, capture_output=True, text=True, check=True, shell=True, env=env)
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

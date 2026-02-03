import os
import re

import time

import subprocess

from pathlib import Path
from contextlib import contextmanager

from rich import print
from rich.progress import Progress
from rich.traceback import install

from config_parser import MainConfig, LangConfig, deep_merge
from hook import Hook, HookType

class LogLevel:
    def __init__(self, level: int = 0, prefix: str = "[]", color: str = "") -> None:
        self.level: int = level
        self.prefix: str = prefix
        self.color: str = color

class LogLevels:
    # TODO needs better name

    def __init__(self, *args) -> None:
        self.log_lvl_s: list[LogLevel] = list(args)

    def print(self, priority: int = 0, text: str = ""):
        for i in self.log_lvl_s:
            if priority == i.level:
                print(f"[bold {i.color}]{i.prefix}[/bold {i.color}]\t{text}")
                break


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


class RunController:

    LOGS = LogLevels(
        LogLevel(1, "[INFO]", "dodger_blue2"),
        LogLevel(2, "[WARN]", "yellow1"),
        LogLevel(3, "[ERROR]", "bright_red")
    )

    def __init__(self, config_path: str, lang_path: str) -> None:
        self.mainConfig = MainConfig(config_path)

        self.lang_path = lang_path

        self.langConfigs: dict = {}
        for language in self.mainConfig.getLanguages():
            path = f"{lang_path}/{language}.yaml"

            if Path(os.path.join(os.path.dirname(__file__), path)).is_file():
                self.langConfigs[path] = LangConfig(path)


    def getJoinedHook(self, hook_type: HookType = HookType.NONE, language: str = "", file: str = "") -> Hook:
        """
        Compares hooks defined in config.yaml and language.yaml files.
        Hook data from language.yaml overrides config.yaml.

        :param self: Description
        :param hook_type: Description
        :type hook_type: HookType
        :param language: Description
        :type language: str
        :param file: Description
        :type file: str
        :return: Description
        :rtype: Hook
        """

        hooks = self.mainConfig.getHooks()

        if hook_type.value == HookType.GENERAL_SETUP.value or hook_type.value == HookType.GENERAL_SHUTDOWN.value:
            main_config_dict = hooks[str(hook_type).lower()]
            lang_config_dict = {}
            if language != "" and language in self.mainConfig.getLanguages():
                lang_config_dict = self.langConfigs[f"{self.lang_path}/{language}.yaml"].getHook(hook_type).toDict()

            return Hook(hook_type, deep_merge(lang_config_dict, main_config_dict))

        if hook_type.value == HookType.FILE_SETUP.value or hook_type.value == HookType.FILE_SHUTDOWN.value:
            if language == "" or language not in self.mainConfig.getLanguages() or hooks[str(hook_type).lower()][language] == None:
                return Hook(hook_type, {})

            main_config_dict = hooks[str(hook_type).lower()][language]
            lang_config_dict = self.langConfigs[f"{self.lang_path}/{language}.yaml"].getHook(hook_type).toDict()

            return Hook(hook_type, deep_merge(lang_config_dict, main_config_dict))

        if hook_type.value == HookType.FUNCTION_SETUP.value or hook_type.value == HookType.FUNCTION_SHUTDOWN.value:
            if language == "" or language not in self.mainConfig.getLanguages() or file == "" or file not in self.mainConfig.getScripts(language):
                return Hook(hook_type, {})

            main_config_dict = hooks[str(hook_type).lower()][language][file]
            lang_config_dict = self.langConfigs[f"{self.lang_path}/{language}.yaml"].getHook(hook_type).toDict()

            return Hook(hook_type, deep_merge(lang_config_dict, main_config_dict))

        return Hook(hook_type, {"result": "something went wrong :("})


    def _hook_block(self, hook: Hook, path: str, output_stream: list[str]) -> list[str]:
        hook_name = str(hook.type).lower().replace("_", " ")
        msg = f"[Hook] [dark_magenta]{path}:[/dark_magenta] load {hook_name}..."
        output_stream.append(msg)
        self.LOGS.print(1, msg)
        out_lang, err_code = Writer.runHook(hook)
        if err_code != 0:
            self.LOGS.print(3, f"[dark_magenta]{path}.{hook_name.replace(" ", "_")}:[/dark_magenta] [bright_red]" + "".join(out_lang) + "[/bright_red]")
        output_stream.extend(out_lang)

        return output_stream


    def start(self, directory: str, keep_scripts: bool = True) -> list[str]:
        output: list[str] = []

        used_general_config_language = "python" # TODO: implement logic to determine which language to use

        output.extend(self._hook_block(self.getJoinedHook(HookType.GENERAL_SETUP, used_general_config_language), "/", output))

        # languages
        for path in self.langConfigs.keys():
            language_name = path.split("/")[-1].split(".yaml")[0]
            msg = f"Language Config file found: [{path}]"
            output.append(msg)
            self.LOGS.print(1, msg)

            output.extend(self._hook_block(self.getJoinedHook(HookType.FILE_SETUP, language_name), f"/{language_name}/", output))

            #   files
            for file in self.mainConfig.getScripts(language_name):
                output.extend(self._hook_block(self.getJoinedHook(HookType.FUNCTION_SETUP, language_name, file), f"/{language_name}/({file})/", output))

                #   write script file
                generated_file_name = f"{directory}/demo_file.{file.split(".")[-1]}"
                code_lines = Script(self.mainConfig, self.langConfigs[f"{self.lang_path}/{language_name}.yaml"])

                msg = f"[File Manager] generate script file [{generated_file_name}]..."
                output.append(msg)
                self.LOGS.print(1, msg)
                Writer(code_lines.getAllTests(language_name)).write(generated_file_name, False)

                #   execute script file
                msg = f"[File Manager] execute script file [{generated_file_name}]..."
                output.append(msg)
                self.LOGS.print(1, msg)
                script_result, exit_code = Writer.runCommand(self.langConfigs[path].getExecutionCommand(generated_file_name))
                output.extend(script_result)
                if exit_code != 0:
                    msg = f"[yellow1][Test] Test in [./{generated_file_name}] failed! (Exit code: {exit_code}) [/yellow1]"
                    output.append(msg)
                    self.LOGS.print(2, msg)

                #   delete script file
                # if keep_scripts == False:
                #     script_result, exit_code = Writer.runCommand(f"rm {generated_file_name}")
                #     if script_result[-1] != "":
                #         output.extend(script_result)

                output.extend(self._hook_block(self.getJoinedHook(HookType.FUNCTION_SHUTDOWN, language_name, file), f"/{language_name}/({file})/", output))

            output.extend(self._hook_block(self.getJoinedHook(HookType.FILE_SHUTDOWN, language_name), f"/{language_name}/", output))

        output.extend(self._hook_block(self.getJoinedHook(HookType.GENERAL_SHUTDOWN, used_general_config_language), f"/", output))

        return output

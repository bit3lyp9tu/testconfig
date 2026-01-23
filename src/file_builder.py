import os
import re

import subprocess

from pathlib import Path

from config_parser import MainConfig, LangConfig, Hook, HookType


class CodeBuilder:
    def __init__(self, config: str, lang_config: str) -> None:
        self.mainConfig: MainConfig = MainConfig(config)
        self.langConfig: LangConfig = LangConfig(lang_config)

    def getImports(self, language: str) -> list[str]:
        result: list[str] = []

        script_path = self.mainConfig.getScripts(language)

        module_name =  re.sub(r'src\.', '', script_path[0].split(".")[0].replace("/", "."))

        variables = self.langConfig.getVariables()
        infix = self.langConfig.getVariableInfixChar()

        modules = self.langConfig.getHeaderData()
        for module in modules:
            header = module.replace(
                variables["import_module"].replace(infix, ""),
                module_name
            ).replace(
                infix,
                ""
            )
            result.append(header)

        return result

    def getFunctionHead(self, language: str, function_name: str, parameters: list[str|int|float], expected_result: list[str|int|float]) -> str:
        script_path = self.mainConfig.getScripts(language)

        module_name =  re.sub(r'src\.', '', script_path[0].split(".")[0].replace("/", "."))

        variables = self.langConfig.getVariables()
        infix = self.langConfig.getVariableInfixChar()

        scheme = self.langConfig.getTestSyntaxScheme()["is_unequal_test"]
        test_header = scheme.replace(
            variables["import_module"].replace(infix, ""),
            module_name
        ).replace(
            variables["function_name"].replace(infix, ""),
            function_name
        ).replace(
            variables["parameters"].replace(infix, ""),
            ",".join(str(i) for i in parameters)
        ).replace(
            variables["expected_result"].replace(infix, ""),
            str(expected_result[0])
        ).replace(
            infix,
            ""
        )
        return test_header

    def getFunctionBody(self, language: str, function_name: str, parameters: list[str|int|float], expected_result: list[str|int|float]) -> list[str]:
        result: list[str] = []

        script_path = self.mainConfig.getScripts(language)

        module_name =  re.sub(r'src\.', '', script_path[0].split(".")[0].replace("/", "."))

        fail_msg_lines = self.langConfig.getFailMessages()

        variables = self.langConfig.getVariables()
        infix = self.langConfig.getVariableInfixChar()

        for fail_msg in fail_msg_lines:
            test_body = fail_msg.replace(
                variables["import_module"].replace(infix, ""),
                module_name
            ).replace(
                variables["function_name"].replace(infix, ""),
                function_name
            ).replace(
                variables["parameters"].replace(infix, ""),
                ",".join(str(i) for i in parameters)
            ).replace(
                variables["expected_result"].replace(infix, ""),
                str(expected_result[0])
            ).replace(
                infix,
                ""
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

        return result

    def build(self, lang: str) -> list[str]:
        result: list[str] = []

        result.extend(self.getAllTests(lang))

        return result


class ScriptBuilder:
    def __init__(self, lines: list[str] = []) -> None:
        self.lines = lines

    def write(self, script_path, print_lines: bool = True) -> None:
        with open(script_path, "w") as f:
            for line in self.lines:
                if print_lines:
                    print(line)
                f.writelines(line + "\n")

    def runCommand(self, command: str) -> tuple[list[str], int]:
        try:
            process = subprocess.run(command.split(" "), capture_output=True, text=True, check=True)
            return process.stdout.split("\n"), process.returncode

        except subprocess.CalledProcessError as e:
            return e.stderr.split("\n"), e.returncode

    def runHook(self, hook: Hook) -> tuple[list[str], int]:
        log: list[str] = []
        return_code = 0

        for attributes in hook.attributes:
            pass

        for command in hook.commands:
            output, code = self.runCommand(command)
            log.extend(output)
            if code != 0:
                return_code = code

        return log, return_code


class RunController:
    def __init__(self, config_path: str, lang_path: str) -> None:
        self.mainConfig = MainConfig(config_path)

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
        # return Hook(hook_type, hooks[str(hook_type).lower()])

        if hook_type == HookType.GENERAL_SETUP or hook_type == HookType.GENERAL_SHUTDOWN:
            main_config_dict = hooks[str(hook_type).lower()].copy()
            lang_config_dict = {}
            if language != "" and language in self.mainConfig.getLanguages():
                lang_config_dict = self.langConfigs[f"configs/lang/{language}.yaml"].getHook(hook_type).toDict().copy()
            else:
                lang_config_dict = {"result": "unsupported feature"}

            if main_config_dict == None or main_config_dict == {}:
                return Hook(hook_type, lang_config_dict)
            else:
                return Hook(hook_type, main_config_dict)

        if hook_type == HookType.FILE_SETUP or hook_type == HookType.FILE_SHUTDOWN:
            if language == "" or language not in self.mainConfig.getLanguages() or hooks[str(hook_type).lower()][language] == None:
                return Hook(hook_type, {})

            main_config_dict = hooks[str(hook_type).lower()][language].copy()
            lang_config_dict = self.langConfigs[f"configs/lang/{language}.yaml"].getHook(hook_type).toDict().copy()

            if main_config_dict == None or main_config_dict == {}:
                return Hook(hook_type, lang_config_dict)
            else:
                return Hook(hook_type, main_config_dict)

        if hook_type == HookType.FUNCTION_SETUP or hook_type == HookType.FUNCTION_SHUTDOWN:
            if language == "" or language not in self.mainConfig.getLanguages() or file == "" or file not in self.mainConfig.getScripts(language):
                return Hook(hook_type, {})

            main_config_dict = hooks[str(hook_type).lower()][language][file].copy()
            lang_config_dict = self.langConfigs[f"configs/lang/{language}.yaml"].getHook(hook_type).toDict().copy()

            if main_config_dict == None or main_config_dict == {}:
                return Hook(hook_type, lang_config_dict)
            else:
                return Hook(hook_type, main_config_dict)


        return Hook(hook_type, {"result": "something went wrong :("})


    def start(self, directory: str, keep_scripts: bool = True) -> list[str]:
        output: list[str] = []

        used_general_config_language = "python" # TODO: implement logic to determine which language to use

        # general hook setup
        output.append("[Hook] load general setup...")
        out, err_code = ScriptBuilder().runHook(self.getJoinedHook(HookType.GENERAL_SETUP, used_general_config_language))
        output.extend(out)
        #   initialize local attributes

        # languages
        for path in self.langConfigs.keys():
            language_name = path.split("/")[-1].split(".yaml")[0]
            output.append(f"Language Config file found: [{path}]")
        #   file setup hook
            output.append("[Hook] load file setup...")
            out_lang, err_code = ScriptBuilder().runHook(self.getJoinedHook(HookType.FILE_SETUP, language_name))
            output.extend(out_lang)

            #   initialize local attributes

            #   files
            for file in self.mainConfig.getScripts(language_name):
                #   function setup hook
                output.append("[Hook] load function setup...")
                out_file, err_code = ScriptBuilder().runHook(self.getJoinedHook(HookType.FUNCTION_SETUP, language_name, file))
                output.extend(out_file)

                #   initialize local attributes

                #   write script file
                generated_file_name = f"{directory}/demo_file.{file.split(".")[-1]}"
                code_lines = CodeBuilder(self.mainConfig.path, path)

                output.append(f"[File Manager] generate script file [{generated_file_name}]...")
                ScriptBuilder(code_lines.getAllTests(language_name)).write(generated_file_name, False)

                #   execute script file
                output.append(f"[File Manager] execute script file [{generated_file_name}]...")
                script_result, exit_code = ScriptBuilder([]).runCommand(self.langConfigs[path].getExecutionCommand(generated_file_name))
                output.extend(script_result)
                if exit_code != 0:
                    output.append(f"[Test] Test in {generated_file_name} failed!")
                    output.append(f"[Test] exit code: {exit_code}")

                #   delete script file
                if keep_scripts == False:
                    script_result, exit_code = ScriptBuilder([]).runCommand(f"rm {generated_file_name}")
                    if script_result[-1] != "":
                        output.extend(script_result)

                #   function shutdown hook
                output.append("[Hook] load function shutdown...")
                out_file, err_code = ScriptBuilder().runHook(self.getJoinedHook(HookType.FUNCTION_SHUTDOWN, language_name, file))
                output.extend(out_file)

            #   file shutdown hook
            output.append("[Hook] load file shutdown...")
            out_lang, err_code = ScriptBuilder().runHook(self.getJoinedHook(HookType.FILE_SHUTDOWN, language_name))
            output.extend(out_lang)

        # general hook shutdown
        output.append("[Hook] load general shutdown...")
        out, err_code = ScriptBuilder().runHook(self.getJoinedHook(HookType.GENERAL_SHUTDOWN, used_general_config_language))
        output.extend(out)

        return output




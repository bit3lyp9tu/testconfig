import os
import re

import mypy

import csv
import yaml

from pathlib import Path

from hook import Hook, HookType
from layer import GeneralLayer, FileLayer, FunctionLayer, to_dict


class MainConfig:
    def __init__(self, path) -> None:
        self.path: str = path

        abs_file_path: str = os.path.join(os.path.dirname(__file__), path)

        self.content: dict[str, dict] = {}
        with open(abs_file_path, 'r') as file:
            self.content = yaml.safe_load(file)

        self.attributes: dict[str, dict[str, str]] = {} # global/local variables?

    def getLanguages(self) -> list[str]:
        return sorted(self.content.keys() - {
            "general_setup",
            "general_shutdown",
            "file_setup",
            "file_shutdown",
            "function_setup",
            "function_shutdown"
        })

    def getScripts(self, lang: str) -> list[str]:
        if self.content[lang] == None:
            return []

        result: list[str] = sorted(self.content[lang].keys() - {
            "general_setup",
            "general_shutdown",
            "file_setup",
            "file_shutdown",
            "function_setup",
            "function_shutdown"
        })
        return [file for file in result if Path(os.path.dirname(Path(__file__).resolve().parents[0]), file).is_file()]

    def getFunctionsBody(self, lang: str, script_path: str) -> dict:
        if lang not in self.content.keys() or self.content[lang] == None:
            return {}
        if script_path not in self.content[lang].keys() or self.content[lang][script_path] == None:
            return {}
        if "tests" not in self.content[lang][script_path] or self.content[lang][script_path]["tests"] == None:
            return {}
        return self.content[lang][script_path]["tests"]


    def getFunction(self, lang: str, script_path: str, function: str) -> list[str]:
        function_content: dict[str, list[str] | dict[str, str]] = self.getFunctionsBody(lang, script_path)

        if function_content == {} or function not in function_content:
            return []

        if "csv_path" in function_content[function]:
            return []

        return list(function_content[function])


    def isPointingToCsvFile(self, lang: str, script_path: str, function: str) -> bool:
        function_content: dict[str, dict[str, str]] = self.getFunctionsBody(lang, script_path)

        if function_content == {} or function not in function_content:
            return False

        if "csv_path" not in function_content[function]:
            return False

        path: str = function_content[function]["csv_path"]
        return path.endswith(".csv") and Path(path).is_file()


    def _typifyTestCaseToList(self, testCaseParameters: str) -> list[int | float | str]:
        typified_parameters: list[int | float | str] = []

        for parameter in testCaseParameters.split(",") :
            if re.match(r'^[+-]?[0-9]+$', parameter) or re.match(r'[-]?[0-9]*\.[0-9]*', parameter):
                if re.match(r'^[+-]?[0-9]+$', parameter):
                    typified_parameters.append(int(parameter))
                if re.match(r'[-]?[0-9]*\.[0-9]*', parameter):
                    typified_parameters.append(float(parameter))
            else:
                typified_parameters.append(parameter)
        return typified_parameters

    def getTestData(self, lang: str, script_path: str, function: str) -> list[tuple[list[int | float | str], list[int | float | str]]]:
        results: list[tuple[list[int | float | str], list[int | float | str]]] = []

        body = self.content[lang][script_path]["tests"][function]

        if type(body) == list:
            # use data from yaml file
            for test_case in body:
                if " -> " in test_case:
                    data: tuple[str, str] = test_case.split(" -> ")
                    x_n: list[int | float | str] = self._typifyTestCaseToList(data[0])
                    y_n: list[int | float | str] = self._typifyTestCaseToList(data[1])

                    results.append((x_n, y_n))
        else:
            # use data from csv file
            path: str = body["csv_path"]
            if self.isPointingToCsvFile(lang, script_path, function):
                with open(path, 'r') as file:
                    lines = csv.reader(file, delimiter=';')
                    has_syntax_option = "syntax" in list(lines)[0]

                    if has_syntax_option:
                        pass
                    else:
                        for param in list(lines)[1:]:
                            x2_n: list[int | float | str] = self._typifyTestCaseToList(param[1].replace("[", "").replace("]", ""))
                            y2_n: list[int | float | str] = self._typifyTestCaseToList(param[2].replace("[", "").replace("]", ""))

                            results.append((x2_n, y2_n))

        return results

    def getHooks(self) -> dict[str, dict]:

        general_layer = GeneralLayer(
            self.getHookGeneral(HookType.GENERAL_SETUP),
            self.getHookGeneral(HookType.GENERAL_SHUTDOWN)
        )

        for language in self.getLanguages():
            if language in self.getLanguages() and self.content[language] != None:

                file_layer = FileLayer(
                    general_layer,
                    language,
                    self.getHookFile(HookType.FILE_SETUP, language),
                    self.getHookFile(HookType.FILE_SHUTDOWN, language)
                )

                for script in self.getScripts(language):
                    if script in self.content[language] and self.content[language][script] != None:

                        function_layer = FunctionLayer(
                            file_layer,
                            language,
                            script,
                            self.getHookFunction(HookType.FUNCTION_SETUP, language, script),
                            self.getHookFunction(HookType.FUNCTION_SHUTDOWN, language, script)
                        )
                        file_layer.merge(function_layer.toData())
                general_layer.merge(file_layer.toData())

            else:
                general_layer.merge({
                    "file_setup": {language: {}},
                    "file_shutdown": {language: {}},
                    "function_setup": {language: {}},
                    "function_shutdown": {language: {}},
                })
        return to_dict(general_layer.toData())


    def getHookGeneral(self, hook_type: HookType) -> Hook:
        hook_type_str: str = str(hook_type).lower()
        if hook_type_str not in self.content.keys() or self.content[hook_type_str] == None:
            return Hook(hook_type, {})
        return Hook(hook_type, self.content[hook_type_str])

    def getHookFile(self, hook_type: HookType, lang: str) -> Hook:
        hook_type_str: str = str(hook_type).lower()
        if hook_type_str not in self.content[lang].keys() or self.content[lang][hook_type_str] == None:
            return Hook(hook_type, {})
        return Hook(hook_type, self.content[lang][hook_type_str])

    def getHookFunction(self, hook_type: HookType, lang: str, file: str) -> Hook:
        hook_type_str: str = str(hook_type).lower()
        if hook_type_str not in self.content[lang][file].keys() or self.content[lang][file][hook_type_str] == None:
             return Hook(hook_type, {})
        return Hook(hook_type, self.content[lang][file][hook_type_str])


class LangConfig:
    def __init__(self, path) -> None:
        self.path: str = path

        abs_file_path: str = os.path.join(os.path.dirname(__file__), path)

        self.content: dict[str, dict] = {}
        with open(abs_file_path, 'r') as file:
            self.content = yaml.safe_load(file)

    def getVariableInfixChar(self) -> str:
        return self.content["config"]["variable_infix_char"]

    def getVariables(self) -> dict[str, str]:
        return self.content["config"]["variables"]

    def getHeaderData(self) -> list[str]:
        if "unit-test" not in self.content or self.content["unit-test"] == None:
            return []
        if "syntax_scheme" not in self.content["unit-test"] or self.content["unit-test"]["syntax_scheme"] == None:
            return []
        if "header_data" not in self.content["unit-test"]["syntax_scheme"]:
            return []
        return self.content["unit-test"]["syntax_scheme"]["header_data"]

    def getFooterData(self) -> list[str]:
        if "unit-test" not in self.content or self.content["unit-test"] == None:
            return []
        if "syntax_scheme" not in self.content["unit-test"] or self.content["unit-test"]["syntax_scheme"] == None:
            return []
        if "footer_data" not in self.content["unit-test"]["syntax_scheme"]:
            return []
        return self.content["unit-test"]["syntax_scheme"]["footer_data"]

    def getTestSyntaxScheme(self) -> dict[str, str]:
        return {
            list(test_types.keys())[0]:
            test_types[list(test_types.keys())[0]]["scheme"]
            for test_types in self.content["unit-test"]["syntax_scheme"]["single_test_code"]
        }

    def getFailMessages(self) -> list[str]:
        return self.content["unit-test"]["syntax_scheme"]["if_failure"]["run"]["messages"]

    def hasValidHookTypes(self) -> bool:
        return len(set(self.content["hooks"].keys()).union({
            "general_setup",
            "general_shutdown",
            "file_setup",
            "file_shutdown",
            "function_setup",
            "function_shutdown"
        })) <= 6

    def getHook(self, type: HookType) -> Hook:
        data = {}

        hook_name: str = str(type).lower()
        if self.content["hooks"] == None or hook_name not in self.content["hooks"].keys() or self.content["hooks"][hook_name] == None:
            return Hook(type, {})

        if "attributes" in self.content["hooks"][hook_name].keys():
            data["attributes"] = {k: "" for k in self.content["hooks"][hook_name]["attributes"]}

        if "commands" in self.content["hooks"][hook_name].keys():
            data["commands"] = self.content["hooks"][hook_name]["commands"]

        if "description" in self.content["hooks"][hook_name].keys():
            data["description"] = self.content["hooks"][hook_name]["description"]

        return Hook(type, data)

    def getExecutionCommand(self, path) -> str:
        if "config" not in self.content or self.content["config"] == None:
            return ""
        if "script_execution" not in self.content["config"] or self.content["config"]["script_execution"] == None:
            return ""
        if "file_path" not in self.content["config"]["script_execution"] or self.content["config"]["script_execution"]["file_path"] == None:
            return ""

        file_path: str = self.content["config"]["script_execution"]["file_path"]

        if "command" not in self.content["config"]["script_execution"] or self.content["config"]["script_execution"]["command"] == None:
            return ""
        command: str = self.content["config"]["script_execution"]["command"]
        return command.replace(file_path, path)

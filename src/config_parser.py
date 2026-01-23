import os
import re

from enum import Enum

import mypy

from pathlib import Path

import csv
import yaml


class HookType(Enum):
    NONE = 0
    GENERAL_SETUP = 1
    GENERAL_SHUTDOWN = 2
    FILE_SETUP = 3
    FILE_SHUTDOWN = 4
    FUNCTION_SETUP = 5
    FUNCTION_SHUTDOWN = 6

    def getType(self, id: int) -> Enum:
        match id:
            case 1:
                return HookType.GENERAL_SETUP
            case 2:
                return HookType.GENERAL_SHUTDOWN
            case 3:
                return HookType.FILE_SETUP
            case 4:
                return HookType.FILE_SHUTDOWN
            case 5:
                return HookType.FUNCTION_SETUP
            case 6:
                return HookType.FUNCTION_SHUTDOWN
            case _:
                return HookType.NONE

    def __str__(self) -> str:
        return str(self.name)

    def __eq__(self, hook_type) -> bool:
        return self.value == hook_type.value

class Hook:
    def __init__(self, hook_type: HookType, data: dict) -> None:
        self.type: HookType = hook_type

        attributes: dict[str, str] = {}
        commands: list[str] = []
        description: str = ""

        if data != {}:
            if "attributes" in data.keys():
                if type(data["attributes"]) == list:
                    attributes = {i: "" for i in list(dict(data["commands"]).keys())}
                else:
                    attributes = dict(data["attributes"])
            commands = list(data["commands"] if "commands" in data.keys() else [])
            description = str(data["description"] if "description" in data.keys() else "")

        self.attributes: dict[str, str] = attributes
        self.commands: list[str] = commands
        self.description: str = description

    # def __dict__(self) -> dict[str, dict[str, str] | list[str] | str]:
    #     return {
    #         "attributes": self.attributes,
    #         "commands": self.commands,
    #         "description": self.description
    #     }

    def toDict(self) ->  dict[str, dict[str, str] | list[str] | str]:
        result: dict[str, dict[str, str] | list[str] | str] = {}
        if self.attributes != {}:
            result["attributes"] = self.attributes
        if self.commands != []:
            result["commands"] = self.commands
        if self.description != "":
            result["description"] = self.description
        return result

    def __eq__(self, hook_type) -> bool:
        return self.type == hook_type.type and self.attributes == hook_type.attributes and self.commands == hook_type.commands and self.description == hook_type.description

    # def overrideWith(self, hook: 'Hook') -> 'Hook':
    #     if self.type == hook.type:
    #         return


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

        return sorted(self.content[lang].keys() - {
            "general_setup",
            "general_shutdown",
            "file_setup",
            "file_shutdown",
            "function_setup",
            "function_shutdown"
        })


    def getFunctionsBody(self, lang: str, script_path: str) -> dict[str, list[str] | dict[str, str]]:
        return self.content[lang][script_path]["tests"]

    def isPointingToCsvFile(self, lang: str, script_path: str, function: str) -> bool:
        function_content = self.content[lang][script_path]["tests"][function]
        if type(function_content) == list:
            return False
        else:
            path: str = function_content["csv_path"]
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
                    for param in list(lines)[1:]:
                        x2_n: list[int | float | str] = self._typifyTestCaseToList(param[1].replace("[", "").replace("]", ""))
                        y2_n: list[int | float | str] = self._typifyTestCaseToList(param[2].replace("[", "").replace("]", ""))

                        results.append((x2_n, y2_n))

        return results

    def getHooks(self) -> dict[str, dict]:
        result: dict[str, dict] = {}

        result["general_setup"] = self.getHookGeneral(HookType.GENERAL_SETUP).toDict()
        result["general_shutdown"] = self.getHookGeneral(HookType.GENERAL_SHUTDOWN).toDict()

        empty_languages: list[str] = []

        for language in self.getLanguages():
            if language in self.getLanguages() and self.content[language] != None:
                result["file_setup"] = {
                    language: self.getHookFile(HookType.FILE_SETUP, language).toDict()
                }
                result["file_shutdown"] = {
                    language: self.getHookFile(HookType.FILE_SHUTDOWN, language).toDict()
                }

                for script in self.getScripts(language):
                    if self.content[language][script] != None:
                        result["function_setup"] = {
                            language: {
                                script: self.getHookFunction(HookType.FUNCTION_SETUP, language, script).toDict()
                            }
                        }
                        result["function_shutdown"] = {
                            language: {
                                script: self.getHookFunction(HookType.FUNCTION_SHUTDOWN, language, script).toDict()
                            }
                        }
            else:
                empty_languages.append(language)

        for language in empty_languages:
            result["file_setup"][language] = {}
            result["file_shutdown"][language] = {}
            result["function_setup"][language] = {}
            result["function_shutdown"][language] = {}

        return result

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
        return self.content["unit-test"]["syntax_scheme"]["header_data"]["import"]

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
        file_path: str = self.content["config"]["script_execution"]["file_path"]
        command: str = self.content["config"]["script_execution"]["command"]
        return command.replace(file_path, path)

import os

from pathlib import Path

from .config_parser import MainConfig, LangConfig
from .file_builder import Writer, Script, CommandRunner
from .hook import Hook, HookType
from .layer import deep_merge
from .log_level import LogLevels

class RunController:
    def __init__(self, config_path: str, lang_path: str, logs: LogLevels = LogLevels(0)) -> None:
        self.mainConfig = MainConfig(config_path)

        self.lang_path = lang_path

        self.langConfigs: dict = {}
        for language in self.mainConfig.getLanguages():
            path = f"{lang_path}/{language}.yaml"

            if Path(os.path.join(os.path.dirname(__file__), path)).is_file():
                self.langConfigs[path] = LangConfig(path)

        self.LOGS = logs

        if self.LOGS.debug_level == 0 or self.LOGS.debug_level in self.LOGS.getLevels():
            pass
        else:
            raise ValueError(f"Invalid debug level")


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
        out_lang, err_code = CommandRunner.runHook(hook)
        if err_code != 0:
            self.LOGS.print(3, f"[dark_magenta]{path}.{hook_name.replace(" ", "_")}:[/dark_magenta] [bright_red]" + "".join(out_lang) + "[/bright_red]")
        output_stream.extend(out_lang)

        return output_stream


    def start(self, directory: str, keep_scripts: bool = True) -> list[str]:
        output: list[str] = []

        demo_file_name = "demo_file"

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
                generated_file_name = f"{directory}/{demo_file_name}.{file.split(".")[-1]}"
                code_lines = Script(self.mainConfig, self.langConfigs[f"{self.lang_path}/{language_name}.yaml"])

                msg = f"[File Manager] generate script file [{generated_file_name}]..."
                output.append(msg)
                self.LOGS.print(1, msg)
                Writer(code_lines.getAllTests(language_name)).write(generated_file_name, False)

                #   execute script file
                msg = f"[File Manager] execute script file [{generated_file_name}]..."
                output.append(msg)
                self.LOGS.print(1, msg)
                script_result, exit_code = CommandRunner.runCommand(self.langConfigs[path].getExecutionCommand(generated_file_name))
                output.extend(script_result)
                if exit_code != 0:
                    msg = f"[yellow1][Test] Test in [./{generated_file_name}] failed! (Exit code: {exit_code}) [/yellow1]"
                    output.append(msg)
                    self.LOGS.print(2, msg)

                #   delete script file
                if keep_scripts == False:
                    Path(f"./{generated_file_name}").unlink()
                    if exit_code == 0:
                        delete_msg = f"[File Manager] File: '{generated_file_name}' deleted"
                        output.extend(delete_msg)
                        self.LOGS.print(1, delete_msg)
                    else:
                        delete_msg = f"[yellow1][File Manager] Failed to delete [./{generated_file_name}] failed! (Exit code: {exit_code}) [/yellow1]"
                        output.extend(delete_msg)
                        self.LOGS.print(2, delete_msg)

                output.extend(self._hook_block(self.getJoinedHook(HookType.FUNCTION_SHUTDOWN, language_name, file), f"/{language_name}/({file})/", output))

            output.extend(self._hook_block(self.getJoinedHook(HookType.FILE_SHUTDOWN, language_name), f"/{language_name}/", output))

        output.extend(self._hook_block(self.getJoinedHook(HookType.GENERAL_SHUTDOWN, used_general_config_language), f"/", output))

        return output

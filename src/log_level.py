
class LogLevel:
    def __init__(self, level: int = 0, prefix: str = "[]", color: str = "") -> None:
        self.level: int = level
        self.prefix: str = prefix
        self.color: str = color

class LogLevels:
    # TODO needs better name

    def __init__(self, debug_level: int = 0, *args) -> None:
        self.debug_level: int = debug_level
        self.log_lvl_s: dict[int, LogLevel] = {i.level: i for i in list(args)}

    def print(self, priority: int = 0, text: str = ""):
        for k, v in self.log_lvl_s.items():
            if priority >= self.debug_level and k == priority:
                print(f"[bold {v.color}]{v.prefix}[/bold {v.color}]\t{text}")

    def getLevels(self) -> list[int]:
        return [i for i in self.log_lvl_s.keys()]

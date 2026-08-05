from __future__ import annotations

import configparser
from pathlib import Path


class AppConfig:
    def __init__(self, path: str | Path = "config.ini") -> None:
        self.path = Path(path)
        self.parser = configparser.ConfigParser()
        self.load()

    def load(self) -> None:
        if not self.parser.read(self.path, encoding="utf-8-sig"):
            raise FileNotFoundError(f"Configuration file not found: {self.path}")

    def get(self, section: str, option: str, fallback: str = "") -> str:
        return self.parser.get(section, option, fallback=fallback)

    def getboolean(self, section: str, option: str, fallback: bool = False) -> bool:
        return self.parser.getboolean(section, option, fallback=fallback)

    def getint(self, section: str, option: str, fallback: int = 0) -> int:
        return self.parser.getint(section, option, fallback=fallback)

    def set(self, section: str, option: str, value: str) -> None:
        if not self.parser.has_section(section):
            self.parser.add_section(section)
        self.parser.set(section, option, value)

    def save(self) -> None:
        with self.path.open("w", encoding="utf-8") as config_file:
            self.parser.write(config_file)

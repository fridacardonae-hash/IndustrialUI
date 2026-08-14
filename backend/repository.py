from __future__ import annotations

import csv
from abc import ABC, abstractmethod
from datetime import date
from pathlib import Path
from threading import Lock
from typing import Iterable


class DataRepository(ABC):
    @abstractmethod
    def append_production(self, row: dict[str, object]) -> None: ...
    @abstractmethod
    def append_process(self, row: dict[str, object]) -> None: ...
    @abstractmethod
    def append_alarm(self, row: dict[str, object]) -> None: ...
    @abstractmethod
    def read_rows(self, category: str, day: date | None = None) -> list[dict[str, str]]: ...


class CsvRepository(DataRepository):
    """Date-partitioned, thread-safe CSV repository; replaceable by a future SQL adapter."""
    FIELDS = {
        "production": ["timestamp", "output", "ok", "ng", "yield", "cycle_time", "machine_state", "work_order"],
        "process": ["timestamp", "pressure", "speed", "holding_time", "inspection_value", "parameters"],
        "alarms": ["start_time", "clear_time", "category", "error_code", "state", "responsible"],
    }

    def __init__(self, root: Path) -> None:
        self.root, self.lock = root, Lock()

    def _file(self, category: str, day: date | None = None) -> Path:
        chosen = day or date.today(); folder = self.root / chosen.strftime("%Y") / chosen.strftime("%m")
        folder.mkdir(parents=True, exist_ok=True)
        return folder / f"{category}_{chosen:%Y-%m-%d}.csv"

    def _append(self, category: str, row: dict[str, object]) -> None:
        fields = self.FIELDS[category]; path = self._file(category)
        with self.lock:
            exists = path.exists()
            with path.open("a", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=fields)
                if not exists: writer.writeheader()
                writer.writerow({field: row.get(field, "") for field in fields})

    def append_production(self, row: dict[str, object]) -> None: self._append("production", row)
    def append_process(self, row: dict[str, object]) -> None: self._append("process", row)
    def append_alarm(self, row: dict[str, object]) -> None: self._append("alarms", row)

    def read_rows(self, category: str, day: date | None = None) -> list[dict[str, str]]:
        path = self._file(category, day)
        if not path.exists(): return []
        with path.open("r", newline="", encoding="utf-8") as stream:
            return list(csv.DictReader(stream))

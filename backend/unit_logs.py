from __future__ import annotations

import csv
from pathlib import Path

from backend.config import AppConfig


class UnitCsvLogger:
    """Stores one row per processed unit in an externally configurable CSV."""

    HEADERS = ["timestamp", "unit_id", "result", "cycle_time_seconds", "machine_state", "alarm_code"]

    def __init__(self, config: AppConfig, project_root: Path) -> None:
        self.path = project_root / config.get("unit_logs", "directory", "logs") / config.get("unit_logs", "file_name", "unit_history.csv")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            with self.path.open("w", newline="", encoding="utf-8") as file:
                csv.writer(file).writerow(self.HEADERS)

    def recent_rows(self, limit: int = 50) -> list[list[str]]:
        with self.path.open("r", newline="", encoding="utf-8") as file:
            return list(csv.reader(file))[1:][-limit:][::-1]

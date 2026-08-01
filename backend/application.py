from __future__ import annotations

import logging
from pathlib import Path

from backend.config import AppConfig
from backend.status_service import StatusService
from frontend.app import IndustrialHMI


class IndustrialApplication:
    def __init__(self) -> None:
        root = Path(__file__).resolve().parent.parent
        self.config = AppConfig(root / "config.ini")
        logging.basicConfig(level=self.config.get("application", "log_level", "INFO"))
        self.status_service = StatusService(self.config)

    def run(self) -> None:
        IndustrialHMI(self.config, self.status_service).run()

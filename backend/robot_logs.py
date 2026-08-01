from __future__ import annotations

from backend.config import AppConfig
from backend.models import ConnectionState, ConnectionStatus


class RobotLogReader:
    """Extension point for direct Epson robot log collection.

    No robot commands are implemented. The exact Epson controller/API must be
    specified before enabling production log retrieval.
    """

    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def health_check(self) -> ConnectionStatus:
        if not self.config.getboolean("robot", "enabled"):
            return ConnectionStatus("Robot", ConnectionState.DISABLED, "Disabled in config.ini")
        if self.config.getboolean("application", "simulation_mode", True):
            return ConnectionStatus("Robot", ConnectionState.SIMULATED, "Epson controller TBD")
        return ConnectionStatus("Robot", ConnectionState.OFFLINE, "Robot adapter not configured")

    def read_logs(self) -> list[str]:
        return []

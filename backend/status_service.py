from __future__ import annotations

import socket

from backend.config import AppConfig
from backend.models import ConnectionState, ConnectionStatus
from backend.plc_slmp import SlmpPlcClient
from backend.robot_logs import RobotLogReader


class StatusService:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.plc = SlmpPlcClient(config)
        self.robot_logs = RobotLogReader(config)

    def all_statuses(self) -> list[ConnectionStatus]:
        return [
            self.plc.health_check(),
            self.robot_logs.health_check(),
            self._generic_status("Cameras", "cameras"),
            self._generic_status("MES", "mes"),
            self._generic_status("IoT", "iot"),
        ]

    def _generic_status(self, label: str, section: str) -> ConnectionStatus:
        if not self.config.getboolean(section, "enabled"):
            return ConnectionStatus(label, ConnectionState.DISABLED, "Disabled in config.ini")
        if self.config.getboolean("application", "simulation_mode", True):
            return ConnectionStatus(label, ConnectionState.SIMULATED, "Simulation mode")
        host, port = self.config.get(section, "host"), self.config.getint(section, "port")
        try:
            with socket.create_connection((host, port), timeout=2):
                return ConnectionStatus(label, ConnectionState.ONLINE, f"{host}:{port}")
        except OSError as error:
            return ConnectionStatus(label, ConnectionState.OFFLINE, str(error))

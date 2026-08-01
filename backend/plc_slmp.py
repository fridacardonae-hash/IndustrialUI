from __future__ import annotations

from slmp import SlmpClient
from backend.config import AppConfig
from backend.models import ConnectionState, ConnectionStatus


class SlmpPlcClient:
    """Read-only PLC connection adapter.

    Register mapping deliberately remains unimplemented until the PLC model,
    SLMP frame type and validated register list are defined.
    """

    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def health_check(self) -> ConnectionStatus:
        if not self.config.getboolean("plc", "enabled"):
            return ConnectionStatus("PLC", ConnectionState.DISABLED, "Disabled in config.ini")
        if self.config.getboolean("application", "simulation_mode", True):
            return ConnectionStatus("PLC", ConnectionState.SIMULATED, "SLMP simulation mode")

        host = self.config.get("plc", "host")
        port = self.config.getint("plc", "port")
        plc_family = self.config.get("plc", "plc_family", "iq-f")
        try:
            # Opens the binary SLMP session without issuing read/write commands.
            with SlmpClient(host, port=port, plc_family=plc_family):
                return ConnectionStatus("PLC", ConnectionState.ONLINE, f"SLMP {plc_family} {host}:{port}")
        except Exception as error:
            return ConnectionStatus("PLC", ConnectionState.OFFLINE, str(error))

    def read_machine_state(self) -> dict[str, object]:
        """Reserved for the approved SLMP register map; never writes to the PLC."""
        return {}

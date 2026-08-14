from __future__ import annotations

from datetime import datetime
from pathlib import Path

from backend.config import AppConfig
from backend.repository import CsvRepository, DataRepository
from backend.simulation_service import MachineSnapshot, SimulationService


class HmiService:
    """Application-facing facade; the UI never accesses PLC or CSV directly."""
    def __init__(self, config: AppConfig, repository: DataRepository | None = None) -> None:
        self.config = config
        root = Path(config.path).parent / config.get("storage", "directory", "data")
        self.repository = repository or CsvRepository(root)
        self.simulation = SimulationService()
        self.active_alarms: dict[str, dict[str, str]] = {}

    def poll(self) -> MachineSnapshot:
        snapshot = self.simulation.next_snapshot()
        if self.config.getboolean("application", "simulation_mode", True):
            self.repository.append_production({
                "timestamp": datetime.now().isoformat(timespec="seconds"), "output": snapshot.total_output,
                "ok": snapshot.total_ok, "ng": snapshot.total_ng,
                "yield": f"{(snapshot.quality or 0) * 100:.2f}", "cycle_time": snapshot.current_ct,
                "machine_state": snapshot.state, "work_order": snapshot.work_order,
            })
        return snapshot

    def parameters(self) -> dict[str, str]:
        section = "process_parameters"
        return {key: self.config.get(section, key) for key in self.config.parser.options(section)}

    def save_parameters(self, values: dict[str, str]) -> None:
        for key, value in values.items(): self.config.set("process_parameters", key, value)
        self.config.save()
        self.repository.append_process({"timestamp": datetime.now().isoformat(timespec="seconds"), **values, "parameters": str(values)})

    def sensor_states(self) -> dict[str, bool]: return self.simulation.sensor_states()

    def alarms(self) -> list[dict[str, str]]:
        return list(self.active_alarms.values()) + self.repository.read_rows("alarms")

    def create_simulated_alarm(self) -> None:
        now = datetime.now().isoformat(timespec="seconds")
        self.active_alarms["SIM-001"] = {"start_time": now, "clear_time": "", "category": "Simulation", "error_code": "SIM-001", "state": "ACTIVE", "responsible": ""}

    def clear_alarm(self, code: str, responsible: str = "") -> None:
        event = self.active_alarms.pop(code, None)
        if event:
            event.update({"clear_time": datetime.now().isoformat(timespec="seconds"), "state": "CLEARED", "responsible": responsible})
            self.repository.append_alarm(event)

    def production_rows(self) -> list[dict[str, str]]: return self.repository.read_rows("production")

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class MachineSnapshot:
    state: str = "IDLE"
    total_output: int = 0
    total_ok: int = 0
    total_ng: int = 0
    current_ct: float = 0.0
    average_ct: float = 0.0
    availability: float | None = None
    performance: float | None = None
    quality: float | None = None
    work_order: str = "NOT CONFIGURED"


class SimulationService:
    """Deterministic demo source; production PLC mapping remains external/configurable."""
    def __init__(self) -> None:
        self.tick = 0
        self.sensors = {"Part Present": True, "Clamp Closed": True, "Door Closed": True, "Air Pressure OK": True, "Robot Home": False, "Safety Circuit": True}

    def next_snapshot(self) -> MachineSnapshot:
        self.tick += 1
        state = "RUNNING" if self.tick % 29 else "PAUSED"
        total = self.tick // 3
        ng = total // 19
        ok = total - ng
        ct = 17.6 + (self.tick % 6) * .2
        self.sensors["Robot Home"] = self.tick % 8 < 5
        return MachineSnapshot(state, total, ok, ng, ct, 18.1, .96, .98, (ok / total if total else None), "WO-DEMO-001")

    def sensor_states(self) -> dict[str, bool]: return dict(self.sensors)

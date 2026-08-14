from __future__ import annotations
from dataclasses import dataclass
from backend.config import AppConfig

@dataclass(frozen=True)
class PlcTag:
    name: str
    address: str
    value_type: str = "bit"

class PlcTagMap:
    """Logical HMI tags; addresses remain empty until PLC validation."""
    DEFAULTS = {"machine_state":"string", "pressure":"float", "current_cycle_time":"float", "total_output":"int", "total_ok":"int", "total_ng":"int", "alarm_code":"int"}
    def __init__(self, config: AppConfig) -> None: self.config = config
    def tags(self) -> dict[str, PlcTag]:
        tags = {name: PlcTag(name, self.config.get("plc_tags", name, ""), kind) for name, kind in self.DEFAULTS.items()}
        for sensor in self.config.get("sensors", "names", "").split(","):
            name = sensor.strip()
            if name: tags[f"sensor.{name}"] = PlcTag(f"sensor.{name}", self.config.get("plc_tags", f"sensor_{name.lower().replace(' ', '_')}", ""), "bit")
        return tags
    def configured(self) -> dict[str, PlcTag]: return {name: tag for name, tag in self.tags().items() if tag.address.strip()}

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class ConnectionState(str, Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    DISABLED = "DISABLED"
    SIMULATED = "SIMULATED"
    ERROR = "ERROR"


@dataclass(frozen=True)
class ConnectionStatus:
    name: str
    state: ConnectionState
    detail: str = ""


@dataclass(frozen=True)
class SystemLog:
    timestamp: datetime
    level: str
    message: str

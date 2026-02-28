from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, TypeVar, Type, Optional
import threading

T = TypeVar("T")

@dataclass(frozen=True)
class RunConfig:
    """
    Immutable. Set once at startup from configuration.
    Frozen dataclass prevents accidental mutation.
    Add fields here that are determined by configuration.
    """
    channels: list[str]
    model_type: str
    # budget: float
    # Any schema variation lives here as Optional fields or subclasses

@dataclass
class RunState:
    """
    Mutable. Evolves throughout the run.
    Processes read and write here freely.
    """
    current_step: str = ""
    artifacts: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    def set(self, key: str, value: Any) -> None:
        self.artifacts[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.artifacts.get(key, default)
    
class AppContext:
    """
    Central application context - single source of truth.
    Thread-safe for concurrent reads/writes to state.
    Passed explicitly via dependency injection, not a global singleton.
    """

    def __init__(self, config: RunConfig, state: Optional[RunState] = None):
        self._config = config
        self._state = state or RunState()
        self._lock = threading.Lock()

    @property
    def config(self) -> RunConfig:
        """Read-only. Frozen at construction time."""
        return self._config

    @property
    def state(self) -> RunState:
        """Mutable runtime state."""
        return self._state

    def update_state(self, **kwargs: Any) -> None:
        """Thread-safe state mutation."""
        with self._lock:
            for key, value in kwargs.items():
                setattr(self._state, key, value)
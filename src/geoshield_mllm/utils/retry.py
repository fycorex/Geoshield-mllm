from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class RetryConfig:
    max_attempts: int = 3
    initial_seconds: float = 1.0
    max_seconds: float = 30.0
    multiplier: float = 2.0


def retry_call(fn: Callable[[], T], config: RetryConfig | None = None, sleep: Callable[[float], None] = time.sleep) -> T:
    cfg = config or RetryConfig()
    delay = cfg.initial_seconds
    last_error: Exception | None = None
    for attempt in range(1, cfg.max_attempts + 1):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001 - preserves original after final attempt.
            last_error = exc
            if attempt == cfg.max_attempts:
                break
            sleep(min(delay, cfg.max_seconds))
            delay *= cfg.multiplier
    assert last_error is not None
    raise last_error


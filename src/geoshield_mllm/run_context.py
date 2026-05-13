from __future__ import annotations

import subprocess
from dataclasses import dataclass, field

from geoshield_mllm.utils.time import utc_now_iso


def current_git_commit() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:  # noqa: BLE001
        return None


@dataclass(frozen=True)
class RunContext:
    run_id: str
    goal: str
    git_commit_hash: str | None = field(default_factory=current_git_commit)
    started_at: str = field(default_factory=utc_now_iso)


from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from geoshield_mllm.utils.time import utc_now_iso


@dataclass
class RunCard:
    run_id: str
    goal: str
    paper_alignment: str
    dataset_name: str
    subset_name: str
    num_images: int
    seed: int
    resize: int
    epsilon: str
    step_size: str
    steps: int
    attack_name: str
    attack_variant: str
    auxiliary_model: str | None
    victim_provider: str
    victim_model: str
    prompt_version: str
    geocoder_backend: str
    git_commit_hash: str | None
    started_at: str = field(default_factory=utc_now_iso)
    finished_at: str | None = None
    drive_paths: list[str] = field(default_factory=list)
    drive_ids: list[str] = field(default_factory=list)
    notes: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


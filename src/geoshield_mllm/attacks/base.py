from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from geoshield_mllm.datasets import ManifestItem


@dataclass(frozen=True)
class AttackConfig:
    attack_name: str
    attack_variant: str
    resize: int
    epsilon: str | float
    step_size: str | float
    steps: int
    output_root: str
    seed: int
    surrogate: dict[str, Any] = field(default_factory=dict)
    geoee: dict[str, Any] = field(default_factory=dict)
    gnfd: dict[str, Any] = field(default_factory=dict)
    psae: dict[str, Any] = field(default_factory=dict)
    attack_vllm_transfer: dict[str, Any] = field(default_factory=dict)
    notes: str | None = None


@dataclass(frozen=True)
class AttackResult:
    item_id: str
    clean_path: str | None
    adv_path: str | None
    metadata: dict[str, Any]
    dry_run: bool = False


class Attack(ABC):
    def __init__(self, config: AttackConfig) -> None:
        self.config = config

    @abstractmethod
    def run_item(self, item: ManifestItem, output_dir: Path, dry_run: bool = False) -> AttackResult:
        raise NotImplementedError

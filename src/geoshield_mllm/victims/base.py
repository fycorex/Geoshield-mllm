from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class VictimRequest:
    image_path: Path
    prompt: str
    prompt_version: str
    model: str


@dataclass(frozen=True)
class RawVictimResponse:
    provider: str
    model: str
    content: Any
    raw_text: str


class VictimProvider(ABC):
    provider_name: str

    @abstractmethod
    def infer_geolocation(self, request: VictimRequest) -> RawVictimResponse:
        raise NotImplementedError

    def describe_non_geo(self, request: VictimRequest) -> RawVictimResponse:
        return self.infer_geolocation(request)

    def judge_attack_success(self, clean_image: Path, adv_image: Path, gt_location: tuple[float, float], prompt_variant: str) -> RawVictimResponse:
        raise NotImplementedError("Attack success judging is not implemented for this provider yet.")


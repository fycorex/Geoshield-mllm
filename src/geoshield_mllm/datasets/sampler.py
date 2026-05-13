from __future__ import annotations

import random
from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")


def deterministic_sample(items: Sequence[T], sample_size: int, seed: int) -> list[T]:
    if sample_size > len(items):
        raise ValueError(f"sample_size {sample_size} exceeds population {len(items)}")
    rng = random.Random(seed)
    indices = list(range(len(items)))
    rng.shuffle(indices)
    return [items[index] for index in sorted(indices[:sample_size])]


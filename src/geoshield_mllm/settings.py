from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    techutopia_base_url: str = os.getenv("TECHUTOPIA_BASE_URL", "https://copilot.techutopia.cn/v1")
    techutopia_api_key: str | None = os.getenv("TECHUTOPIA_API_KEY")
    cache_dir: Path = Path(os.getenv("GEOSHIELD_MLLM_CACHE_DIR", ".cache/geoshield_mllm"))


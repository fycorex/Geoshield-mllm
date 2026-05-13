from __future__ import annotations

import shutil
from pathlib import Path

from geoshield_mllm.utils.hashing import sha256_file


class LocalCache:
    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def path_for(self, key: str) -> Path:
        clean_key = key.strip("/").replace("/", "__")
        return self.root / clean_key

    def put(self, source: Path, key: str) -> Path:
        dest = self.path_for(key)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
        return dest

    def validate(self, path: Path, expected_sha256: str) -> bool:
        return Path(path).exists() and sha256_file(Path(path)) == expected_sha256


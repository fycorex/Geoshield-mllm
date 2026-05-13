from __future__ import annotations

from pathlib import Path

from geoshield_mllm.attacks.base import Attack, AttackResult
from geoshield_mllm.datasets import ManifestItem
from geoshield_mllm.utils.time import utc_now_iso


class GeoShieldLikeAttack(Attack):
    """Interface placeholder for a real GeoShield/fork integration."""

    def run_item(self, item: ManifestItem, output_dir: Path, dry_run: bool = False) -> AttackResult:
        output_dir.mkdir(parents=True, exist_ok=True)
        metadata = {
            "attack_name": self.config.attack_name,
            "attack_variant": self.config.attack_variant,
            "resize": self.config.resize,
            "epsilon": self.config.epsilon,
            "step_size": self.config.step_size,
            "steps": self.config.steps,
            "surrogate": self.config.surrogate,
            "created_at": utc_now_iso(),
            "note": "Dry-run metadata only; no adversarial image generated." if dry_run else self.config.notes,
        }
        if not dry_run:
            raise NotImplementedError("Real GeoShield attack integration is not wired yet; run with dry_run=True.")
        return AttackResult(item_id=item.item_id, clean_path=item.image_path, adv_path=None, metadata=metadata, dry_run=True)


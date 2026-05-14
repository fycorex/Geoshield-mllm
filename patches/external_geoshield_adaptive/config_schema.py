"""Configuration schema for GeoShield adversarial attack."""

from dataclasses import dataclass, field
from hydra.core.config_store import ConfigStore


@dataclass
class WandbConfig:
    """Wandb-specific configuration."""
    entity: str = ""
    project: str = "geoshield"


@dataclass
class DataConfig:
    """Data loading configuration."""
    batch_size: int = 1
    num_samples: int = 100
    cle_data_path: str = "data/clean_images"
    tgt_data_path: str = "data/target_images"
    output: str = "./output"
    bbox_json_path: str = ""
    description_json_path: str = ""


@dataclass
class OptimConfig:
    """Optimization parameters."""
    alpha: float = 1.0
    epsilon: int = 8
    steps: int = 300
    enable_visual_contrastive: bool = False
    visual_contrastive_weight: float = 0.5
    contrastive_temperature: float = 0.07
    enable_relative_proxy: bool = False
    relative_proxy_weight: float = 0.25
    enable_gaussian: bool = False
    gaussian_prob: float = 0.5
    gaussian_scale_multiplier: float = 0.25
    enable_crop_pad_resize: bool = False
    crop_pad_resize_prob: float = 0.5
    enable_diffjpeg: bool = False
    diffjpeg_prob: float = 0.5
    jpeg_quality_min: float = 0.55
    jpeg_quality_max: float = 0.95
    enable_patchdrop: bool = False
    patchdrop_prob: float = 0.3
    patchdrop_rate: float = 0.15
    perturbation_averages: int = 1


@dataclass
class ModelConfig:
    """Model-specific parameters."""
    input_res: int = 336
    use_source_crop: bool = True
    use_target_crop: bool = True
    crop_scale: tuple = (0.5, 0.9)
    ensemble: bool = True
    device: str = "cuda:0"
    backbone: list = field(default_factory=lambda: ["L336", "B16", "B32", "Laion"])


@dataclass
class MainConfig:
    """Main configuration combining all sub-configs."""
    data: DataConfig = field(default_factory=DataConfig)
    optim: OptimConfig = field(default_factory=OptimConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    wandb: WandbConfig = field(default_factory=WandbConfig)
    attack: str = "fgsm"


@dataclass
class Ensemble3ModelsConfig(MainConfig):
    """Configuration for ensemble with 3 models."""

    def __post_init__(self):
        self.data = DataConfig(batch_size=1)
        self.model = ModelConfig(
            use_source_crop=True,
            use_target_crop=True,
            backbone=["B16", "B32", "Laion"]
        )


cs = ConfigStore.instance()
cs.store(name="config", node=MainConfig)
cs.store(name="ensemble_3models", node=Ensemble3ModelsConfig)

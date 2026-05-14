"""
GeoShield: Adversarial perturbation for image geolocation privacy protection.

This module implements adversarial attacks on images to prevent VLM-based
geolocation prediction while preserving semantic content.
"""

import os
import json
import random
from io import BytesIO
import numpy as np
import torch
import torch.nn.functional as F
import torchvision
import torchvision.transforms as transforms
import torchvision.transforms.functional as TF
from PIL import Image
from torch import nn
from torch.utils.data import Dataset
from typing import List, Dict, Optional
import hydra
from omegaconf import OmegaConf
import wandb
from tqdm import tqdm

from config_schema import MainConfig
from surrogates import (
    ClipB16FeatureExtractor,
    ClipL336FeatureExtractor,
    ClipB32FeatureExtractor,
    ClipLaionFeatureExtractor,
    Dinov2FeatureExtractor,
    Qwen2VLFeatureExtractor,
    LlavaNextFeatureExtractor,
    EnsembleFeatureLoss,
    EnsembleFeatureExtractor,
)
from utils import hash_training_config, setup_wandb, ensure_dir

os.environ["WANDB_MODE"] = "disabled"

BACKBONE_MAP: Dict[str, type] = {
    "L336": ClipL336FeatureExtractor,
    "B16": ClipB16FeatureExtractor,
    "B32": ClipB32FeatureExtractor,
    "Laion": ClipLaionFeatureExtractor,
    "DINOv2": Dinov2FeatureExtractor,
    "Qwen2VL": Qwen2VLFeatureExtractor,
    "LLaVANeXT": LlavaNextFeatureExtractor,
}


def load_bboxes(json_path: str) -> Dict:
    """Load bounding boxes from JSON file.

    Args:
        json_path: Path to JSON file containing detection results.

    Returns:
        Dictionary mapping image names to their size and bounding boxes.
    """
    with open(json_path, 'r') as f:
        raw = json.load(f)
    out = {}
    for name, v in raw.items():
        out[name] = {
            'size': tuple(v['image_size']),
            'boxes': [d.get('sam_box') or d.get('refined_box') or d['box'] for d in v['detections']]
        }
    return out


def load_descriptions(json_path: str) -> Dict[str, str]:
    """Load per-image semantic descriptions from JSON."""
    with open(json_path, "r") as f:
        raw = json.load(f)
    descriptions = {}
    for name, value in raw.items():
        if isinstance(value, str):
            descriptions[name] = value
        elif isinstance(value, dict):
            descriptions[name] = value.get("description", "")
    return descriptions


def bbox_to_mask(box: List[int], orig_hw: tuple, dst_res: int, device: str) -> torch.Tensor:
    """Convert bounding box to binary mask tensor.

    Args:
        box: Bounding box coordinates [x1, y1, x2, y2].
        orig_hw: Original image height and width.
        dst_res: Destination resolution.
        device: Target device for tensor.

    Returns:
        Binary mask tensor of shape [1, 1, dst_res, dst_res].
    """
    h0, w0 = orig_hw
    x1, y1, x2, y2 = box
    sx, sy = dst_res / w0, dst_res / h0
    x1, x2 = int(x1 * sx), int(x2 * sx)
    y1, y2 = int(y1 * sy), int(y2 * sy)
    mask = torch.zeros(1, 1, dst_res, dst_res, device=device)
    mask[:, :, y1:y2+1, x1:x2+1] = 1
    return mask


def apply_patchdrop(images: torch.Tensor, drop_rate: float) -> torch.Tensor:
    if drop_rate <= 0:
        return images
    batch, _channels, height, width = images.shape
    grid_h = max(1, height // 32)
    grid_w = max(1, width // 32)
    keep = (torch.rand(batch, 1, grid_h, grid_w, device=images.device) > drop_rate).float()
    keep = F.interpolate(keep, size=(height, width), mode="nearest")
    return images * keep


def apply_tensor_jpeg(images: torch.Tensor, quality_min: float, quality_max: float) -> torch.Tensor:
    quality = random.uniform(quality_min, quality_max)
    x = torch.clamp(images / 255.0, 0.0, 1.0)
    levels = max(8, int(16 + quality * 239))
    compressed = torch.round(x * levels) / levels
    if quality < 0.95:
        _, _, height, width = compressed.shape
        scale = max(0.5, min(1.0, 0.5 + 0.5 * quality))
        down_h = max(1, int(round(height * scale)))
        down_w = max(1, int(round(width * scale)))
        compressed = F.interpolate(compressed, size=(down_h, down_w), mode="bilinear", align_corners=False, antialias=True)
        compressed = F.interpolate(compressed, size=(height, width), mode="bilinear", align_corners=False, antialias=True)
    return images + (compressed * 255.0 - images).detach()


def apply_crop_pad_resize(images: torch.Tensor, image_size: int) -> torch.Tensor:
    outputs = []
    for image in images:
        top, left, crop_h, crop_w = transforms.RandomResizedCrop.get_params(
            image,
            scale=(0.6, 1.0),
            ratio=(0.85, 1.15),
        )
        cropped = TF.crop(image, top, left, crop_h, crop_w)
        resized = TF.resize(cropped, [image_size, image_size], antialias=True)
        outputs.append(resized)
    return torch.stack(outputs, dim=0)


def attack_vllm_augment(images: torch.Tensor, cfg: MainConfig) -> torch.Tensor:
    x = images
    if cfg.optim.enable_gaussian and random.random() < cfg.optim.gaussian_prob:
        sigma = float(cfg.optim.epsilon) * float(cfg.optim.gaussian_scale_multiplier)
        x = x + sigma * torch.randn_like(x)
    if cfg.optim.enable_crop_pad_resize and random.random() < cfg.optim.crop_pad_resize_prob:
        x = apply_crop_pad_resize(x, cfg.model.input_res)
    if cfg.optim.enable_diffjpeg and random.random() < cfg.optim.diffjpeg_prob:
        x = apply_tensor_jpeg(x, cfg.optim.jpeg_quality_min, cfg.optim.jpeg_quality_max)
    if cfg.optim.enable_patchdrop and random.random() < cfg.optim.patchdrop_prob:
        x = apply_patchdrop(x, cfg.optim.patchdrop_rate)
    return torch.clamp(x, 0.0, 255.0)


def ensemble_features_with_averaging(
    cfg: MainConfig,
    ensemble_extractor: nn.Module,
    images: torch.Tensor,
) -> Dict[int, torch.Tensor]:
    passes = max(1, int(cfg.optim.perturbation_averages))
    total = None
    for _ in range(passes):
        view = attack_vllm_augment(images, cfg) if passes > 1 else images
        features = ensemble_extractor(view)
        if total is None:
            total = {idx: value for idx, value in features.items()}
        else:
            for idx, value in features.items():
                total[idx] = total[idx] + value
    if passes == 1:
        return total
    return {idx: value / passes for idx, value in total.items()}


class MaskCrop:
    """Crop image region based on binary mask."""

    def __init__(self, input_res: int):
        self.input_res = input_res

    def __call__(self, image: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        if image.dim() == 4:
            image = image[0]
        if mask.dim() == 4:
            mask = mask[0, 0]
        elif mask.dim() == 3:
            mask = mask[0]

        indices = torch.nonzero(mask, as_tuple=False)
        if indices.shape[0] == 0:
            raise ValueError("Mask is empty, nothing to crop.")

        y1, x1 = indices.min(dim=0)[0]
        y2, x2 = indices.max(dim=0)[0]

        cropped = image[:, y1:y2 + 1, x1:x2 + 1]
        return cropped


def get_models(cfg: MainConfig):
    """Initialize feature extraction models based on configuration.

    Args:
        cfg: Configuration object containing model settings.

    Returns:
        Tuple of (ensemble_extractor, list of individual models).
    """
    if not cfg.model.ensemble and len(cfg.model.backbone) > 1:
        raise ValueError("When ensemble=False, only one backbone can be specified")

    models = []
    for backbone_name in cfg.model.backbone:
        if backbone_name not in BACKBONE_MAP:
            raise ValueError(
                f"Unknown backbone: {backbone_name}. Valid options are: {list(BACKBONE_MAP.keys())}"
            )
        model_class = BACKBONE_MAP[backbone_name]
        model = model_class().eval().to(cfg.model.device).requires_grad_(False)
        models.append(model)

    if cfg.model.ensemble:
        ensemble_extractor = EnsembleFeatureExtractor(models)
    else:
        ensemble_extractor = models[0]

    return ensemble_extractor, models


def get_ensemble_loss(cfg: MainConfig, models: List[nn.Module]):
    """Create ensemble loss function."""
    return EnsembleFeatureLoss(models)


def set_environment(seed: int = 2023):
    """Set random seeds for reproducibility."""
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def to_tensor(pic: Image.Image) -> torch.Tensor:
    """Convert PIL Image to PyTorch Tensor."""
    mode_to_nptype = {"I": np.int32, "I;16": np.int16, "F": np.float32}
    img = torch.from_numpy(
        np.array(pic, mode_to_nptype.get(pic.mode, np.uint8), copy=True)
    )
    img = img.view(pic.size[1], pic.size[0], len(pic.getbands()))
    img = img.permute((2, 0, 1)).contiguous()
    return img.to(dtype=torch.get_default_dtype())


class ImageFolderWithPaths(Dataset):
    """Dataset that returns images along with their file paths."""

    def __init__(self, root: str, transform=None):
        self.paths = [
            os.path.join(root, fname)
            for fname in os.listdir(root)
            if fname.lower().endswith(('.png', '.jpg', '.jpeg'))
        ]
        self.transform = transform

    def __len__(self):
        return len(self.paths)

    def __getitem__(self, idx):
        path = self.paths[idx]
        image = Image.open(path).convert('RGB')
        if self.transform:
            image = self.transform(image)
        return image, 0, path


def describe_image_placeholder(image_path: str) -> str:
    """Placeholder for image description function.

    Replace this with your own VLM-based image description API.
    For example:
    - OpenAI GPT-4V API
    - Claude Vision API
    - Google Gemini Vision API
    - Local BLIP/LLaVA models

    Args:
        image_path: Path to the image file.

    Returns:
        Text description of the image content (not location).
        Should describe visual elements like objects, scenes, activities.
    """
    # TODO: Implement your VLM API call here
    return "A scenic outdoor photograph."


@hydra.main(version_base=None, config_path="config", config_name="ensemble_3models")
def main(cfg: MainConfig):
    """Main entry point for GeoShield adversarial attack."""
    set_environment()
    setup_wandb(cfg, tags=["image_generation"])
    wandb.define_metric("epoch")
    wandb.define_metric("*", step_metric="epoch")

    ensemble_extractor, models = get_models(cfg)
    ensemble_loss = get_ensemble_loss(cfg, models)

    transform_fn = transforms.Compose([
        transforms.Resize(
            cfg.model.input_res,
            interpolation=torchvision.transforms.InterpolationMode.BICUBIC,
        ),
        transforms.CenterCrop(cfg.model.input_res),
        transforms.Lambda(lambda img: img.convert("RGB")),
        transforms.Lambda(lambda img: to_tensor(img)),
    ])

    clean_data = ImageFolderWithPaths(cfg.data.cle_data_path, transform=transform_fn)
    target_data = ImageFolderWithPaths(cfg.data.tgt_data_path, transform=transform_fn)

    data_loader_clean = torch.utils.data.DataLoader(
        clean_data, batch_size=cfg.data.batch_size, shuffle=False
    )
    data_loader_target = torch.utils.data.DataLoader(
        target_data, batch_size=cfg.data.batch_size, shuffle=False
    )

    print("Using source crop:", cfg.model.use_source_crop)
    print("Using target crop:", cfg.model.use_target_crop)

    source_crop = (
        transforms.RandomResizedCrop(cfg.model.input_res, scale=cfg.model.crop_scale)
        if cfg.model.use_source_crop
        else torch.nn.Identity()
    )
    target_crop = (
        transforms.RandomResizedCrop(cfg.model.input_res, scale=cfg.model.crop_scale)
        if cfg.model.use_target_crop
        else torch.nn.Identity()
    )

    # Load bounding boxes if available
    bbox_json_path = cfg.data.get("bbox_json_path", None)
    bbox_dict = load_bboxes(bbox_json_path) if bbox_json_path and os.path.exists(bbox_json_path) else {}
    description_json_path = cfg.data.get("description_json_path", None)
    description_dict = (
        load_descriptions(description_json_path)
        if description_json_path and os.path.exists(description_json_path)
        else {}
    )

    for i, ((image_org, _, path_org), (image_tgt, _, path_tgt)) in enumerate(
        zip(data_loader_clean, data_loader_target)
    ):
        if cfg.data.batch_size * (i + 1) > cfg.data.num_samples:
            break

        print(f"\nProcessing image {i+1}/{cfg.data.num_samples//cfg.data.batch_size}")

        attack_imgpair(
            cfg=cfg,
            ensemble_extractor=ensemble_extractor,
            ensemble_loss=ensemble_loss,
            source_crop=source_crop,
            img_index=i,
            image_org=image_org,
            path_org=path_org,
            image_tgt=image_tgt,
            target_crop=target_crop,
            bbox_dict=bbox_dict,
            description_dict=description_dict,
        )

    wandb.finish()


def attack_imgpair(
    cfg: MainConfig,
    ensemble_extractor: nn.Module,
    ensemble_loss: nn.Module,
    source_crop: Optional[transforms.RandomResizedCrop],
    target_crop: Optional[transforms.RandomResizedCrop],
    img_index: int,
    image_org: torch.Tensor,
    path_org: List[str],
    image_tgt: torch.Tensor,
    bbox_dict: Dict,
    description_dict: Dict[str, str],
):
    """Attack a single image pair."""
    image_org = image_org.to(cfg.model.device)
    image_tgt = image_tgt.to(cfg.model.device)

    img_name = os.path.basename(path_org[0])

    # Get bounding boxes or use full image
    if img_name in bbox_dict:
        img_size = bbox_dict[img_name]['size']
        boxes = bbox_dict[img_name]['boxes']
    else:
        img_size = (image_org.shape[2], image_org.shape[3])
        boxes = []

    # Add full image bbox
    boxes.append([0, 0, img_size[1], img_size[0]])

    # Calculate area-based probabilities
    areas = []
    for box in boxes:
        m = bbox_to_mask(box, img_size, cfg.model.input_res, cfg.model.device)
        areas.append(torch.sum(m).float())
    areas = torch.stack(areas)
    total_area = areas.sum() + 1e-8
    probs = [torch.sum(bbox_to_mask(box, img_size, cfg.model.input_res, cfg.model.device)).float() / total_area
             for box in boxes]

    # Get image description (placeholder - replace with your VLM API)
    tmp_img_path = './tmp_image_tgt.jpg'
    os.makedirs(os.path.dirname(tmp_img_path) if os.path.dirname(tmp_img_path) else '.', exist_ok=True)
    torchvision.utils.save_image(image_tgt[0]/255, tmp_img_path)
    description = (
        description_dict.get(img_name)
        or description_dict.get(os.path.splitext(img_name)[0])
        or describe_image_placeholder(tmp_img_path)
    )
    print(f"Image description: {description}")

    adv_image = fgsm_attack_masked(
        cfg=cfg,
        ensemble_extractor=ensemble_extractor,
        ensemble_loss=ensemble_loss,
        source_crop=source_crop,
        target_crop=target_crop,
        img_index=img_index,
        image_org=image_org,
        image_tgt=image_tgt,
        boxes=boxes,
        image_size=img_size,
        probs=probs,
        description=description,
    )

    # Save output
    config_hash = hash_training_config(cfg) + '+geoshield'

    for path_idx in range(len(path_org)):
        folder, name = (
            os.path.basename(os.path.dirname(path_org[path_idx])),
            os.path.basename(path_org[path_idx]),
        )
        folder_to_save = os.path.join(cfg.data.output, "img", config_hash, folder)
        ensure_dir(folder_to_save)

        ext = os.path.splitext(name)[1].lower()
        save_name = name if ext in [".jpeg", ".jpg", ".png"] else name + ".png"
        save_path = os.path.join(folder_to_save, save_name)
        torchvision.utils.save_image(adv_image[path_idx], save_path)


def log_metrics(pbar, metrics: Dict, img_index: int, epoch: int = None):
    """Log metrics to progress bar and wandb."""
    pbar_metrics = {
        k: f"{v:.5f}" if "sim" in k else f"{v:.3f}" for k, v in metrics.items()
    }
    pbar.set_postfix(pbar_metrics)

    wandb_metrics = {f"img{img_index}_{k}": v for k, v in metrics.items()}
    if epoch is not None:
        wandb_metrics["epoch"] = epoch
    wandb.log(wandb_metrics)


def fgsm_attack_masked(
    cfg: MainConfig,
    ensemble_extractor: nn.Module,
    ensemble_loss: nn.Module,
    source_crop: Optional[transforms.RandomResizedCrop],
    target_crop: Optional[transforms.RandomResizedCrop],
    img_index: int,
    image_org: torch.Tensor,
    image_tgt: torch.Tensor,
    boxes: List,
    image_size: tuple,
    probs: List[float],
    description: str,
) -> torch.Tensor:
    """Perform FGSM attack with geolocation-aware loss.

    Args:
        cfg: Configuration parameters.
        ensemble_extractor: Feature extractor model.
        ensemble_loss: Loss function.
        source_crop: Transform for source images.
        target_crop: Transform for target images.
        img_index: Image index for logging.
        image_org: Original image tensor.
        image_tgt: Target image tensor.
        boxes: List of bounding boxes.
        image_size: Original image size.
        probs: Sampling probabilities for boxes.
        description: Text description of the image.

    Returns:
        Adversarial image tensor.
    """
    delta = torch.zeros_like(image_org, requires_grad=True)
    pbar = tqdm(range(cfg.optim.steps), desc="Attack progress")
    mask_crop = MaskCrop(cfg.model.input_res)

    for epoch in pbar:
        loss = 0

        # Random box selection
        box = random.choices(boxes, weights=[float(p) for p in probs], k=1)[0]
        mask = bbox_to_mask(box, image_size, cfg.model.input_res, cfg.model.device)

        with torch.no_grad():
            img_tgt = mask_crop(image_tgt, mask).unsqueeze(0)
            ensemble_loss.set_ground_truth(img_tgt)

        adv_image = image_org + delta

        crop = transforms.RandomCrop(224)
        adv_image_mask = crop(adv_image)
        adv_image_cropped = source_crop(adv_image)

        adv_image_cropped = attack_vllm_augment(adv_image_cropped, cfg)
        adv_image_mask = attack_vllm_augment(adv_image_mask, cfg)

        adv_features = ensemble_features_with_averaging(cfg, ensemble_extractor, adv_image_cropped)
        adv_features_mask = ensemble_features_with_averaging(cfg, ensemble_extractor, adv_image_mask)

        metrics = {
            "max_delta": torch.max(torch.abs(delta)).item(),
            "mean_delta": torch.mean(torch.abs(delta)).item(),
        }

        global_sim = ensemble_loss(adv_features)
        local_sim = ensemble_loss(adv_features_mask)
        loss -= (global_sim + local_sim)

        # Geo-semantic loss
        with torch.no_grad():
            img_tgt_full = target_crop(image_org)
            ensemble_loss.set_ground_truth(img_tgt_full)
            ensemble_loss.set_geotext_truth(description, cfg.model.device)

        text_loss = ensemble_loss.geo_loss(adv_features)
        text_local_loss = ensemble_loss.geo_loss(adv_features_mask)
        loss -= (text_loss + text_local_loss)

        if cfg.optim.enable_visual_contrastive or cfg.optim.enable_relative_proxy:
            with torch.no_grad():
                positive_img = target_crop(image_org)
                negative_img = mask_crop(image_tgt, mask).unsqueeze(0)
                positive_features = ensemble_loss.encode_examples(positive_img)
                negative_features = ensemble_loss.encode_examples(negative_img)
                clean_features = ensemble_extractor(positive_img)
            if cfg.optim.enable_visual_contrastive:
                vc_objective = ensemble_loss.visual_contrastive_objective(
                    adv_features,
                    positive_features,
                    negative_features,
                    cfg.optim.contrastive_temperature,
                )
                loss += cfg.optim.visual_contrastive_weight * vc_objective
            if cfg.optim.enable_relative_proxy:
                rp_objective = ensemble_loss.relative_proxy_objective(
                    clean_features,
                    adv_features,
                    positive_features,
                    negative_features,
                )
                loss += cfg.optim.relative_proxy_weight * rp_objective

        grad = torch.autograd.grad(loss, delta, create_graph=False)[0]

        delta.data = torch.clamp(
            delta + cfg.optim.alpha * torch.sign(grad),
            min=-cfg.optim.epsilon,
            max=cfg.optim.epsilon,
        )

    adv_image = image_org + delta
    adv_image = torch.clamp(adv_image / 255.0, 0.0, 1.0)

    final_metrics = {
        "max_delta": torch.max(torch.abs(delta)).item(),
        "mean_delta": torch.mean(torch.abs(delta)).item(),
    }
    log_metrics(pbar, final_metrics, img_index)

    return adv_image


if __name__ == "__main__":
    main()

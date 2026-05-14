"""DINOv2 visual surrogate adapter."""

import torch
from transformers import AutoImageProcessor, AutoModel
from torchvision import transforms

from .Base import BaseFeatureExtractor


class Dinov2FeatureExtractor(BaseFeatureExtractor):
    """Feature extractor using a DINOv2 vision backbone."""

    def __init__(self, model_id: str = "facebook/dinov2-base"):
        super().__init__()
        self.model_id = model_id
        self.model = AutoModel.from_pretrained(model_id)
        self.processor = AutoImageProcessor.from_pretrained(model_id)
        size = self.processor.size.get("height", 224) if isinstance(self.processor.size, dict) else 224
        mean = getattr(self.processor, "image_mean", [0.485, 0.456, 0.406])
        std = getattr(self.processor, "image_std", [0.229, 0.224, 0.225])
        self.normalizer = transforms.Compose(
            [
                transforms.Resize(size, interpolation=transforms.InterpolationMode.BICUBIC, antialias=True),
                transforms.Lambda(lambda img: torch.clamp(img, 0.0, 255.0) / 255.0),
                transforms.CenterCrop(size),
                transforms.Normalize(mean, std),
            ]
        )

    def forward(self, x):
        pixel_values = self.normalizer(x)
        output = self.model(pixel_values=pixel_values)
        if getattr(output, "pooler_output", None) is not None:
            features = output.pooler_output
        else:
            features = output.last_hidden_state[:, 0]
        features = features / features.norm(dim=1, keepdim=True)
        return features

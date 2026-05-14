"""Open VLLM visual surrogate adapter.

This adapter is intentionally generic. It supports models exposing
`get_image_features`, `vision_model`, or `visual` modules through Transformers.
Specific Qwen/LLaVA checkpoints can be selected through environment variables.
"""

import os

import torch
from transformers import AutoModel, AutoProcessor
from torchvision import transforms

from .Base import BaseFeatureExtractor


class OpenVLLMFeatureExtractor(BaseFeatureExtractor):
    def __init__(self, model_id: str):
        super().__init__()
        self.model_id = model_id
        self.processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
        self.model = AutoModel.from_pretrained(model_id, trust_remote_code=True)
        self.normalizer = transforms.Compose(
            [
                transforms.Resize(336, interpolation=transforms.InterpolationMode.BICUBIC, antialias=True),
                transforms.Lambda(lambda img: torch.clamp(img, 0.0, 255.0) / 255.0),
                transforms.CenterCrop(336),
                transforms.Normalize((0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711)),
            ]
        )

    def forward(self, x):
        pixel_values = self.normalizer(x)
        if hasattr(self.model, "get_image_features"):
            features = self.model.get_image_features(pixel_values=pixel_values)
        elif hasattr(self.model, "vision_model"):
            output = self.model.vision_model(pixel_values=pixel_values)
            features = getattr(output, "pooler_output", None)
            if features is None:
                features = output.last_hidden_state[:, 0]
        elif hasattr(self.model, "visual"):
            features = self.model.visual(pixel_values)
            if isinstance(features, (tuple, list)):
                features = features[0]
        else:
            raise RuntimeError(f"Model {self.model_id} does not expose a known visual feature interface")
        features = self.as_feature_tensor(features)
        if features.dim() > 2:
            features = features[:, 0]
        return features / features.norm(dim=1, keepdim=True)


class Qwen2VLFeatureExtractor(OpenVLLMFeatureExtractor):
    def __init__(self):
        super().__init__(os.environ.get("GEOSHIELD_QWEN2VL_MODEL", "Qwen/Qwen2.5-VL-3B-Instruct"))


class LlavaNextFeatureExtractor(OpenVLLMFeatureExtractor):
    def __init__(self):
        super().__init__(os.environ.get("GEOSHIELD_LLAVA_NEXT_MODEL", "llava-hf/llava-v1.6-mistral-7b-hf"))

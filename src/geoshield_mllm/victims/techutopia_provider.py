from __future__ import annotations

import base64
import json
import mimetypes
import os
from typing import Literal

from geoshield_mllm.victims.base import RawVictimResponse, VictimProvider, VictimRequest


class TechUtopiaProvider(VictimProvider):
    provider_name = "techutopia"

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        image_mode: Literal["data_url", "none"] | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("TECHUTOPIA_API_KEY")
        self.base_url = (base_url or os.getenv("TECHUTOPIA_BASE_URL") or "https://copilot.techutopia.cn/v1").rstrip("/")
        self.image_mode = image_mode or os.getenv("TECHUTOPIA_IMAGE_MODE", "data_url")
        self.default_headers = self._default_headers()

    @staticmethod
    def _default_headers() -> dict[str, str]:
        headers = {
            "User-Agent": os.getenv("TECHUTOPIA_USER_AGENT", "Geoshield-mllm/0.1 research-client"),
        }
        extra = os.getenv("TECHUTOPIA_EXTRA_HEADERS_JSON")
        if extra:
            parsed = json.loads(extra)
            if not isinstance(parsed, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in parsed.items()):
                raise ValueError("TECHUTOPIA_EXTRA_HEADERS_JSON must be a JSON object of string headers.")
            headers.update(parsed)
        return headers

    def infer_geolocation(self, request: VictimRequest) -> RawVictimResponse:
        if not self.api_key:
            raise RuntimeError("TECHUTOPIA_API_KEY is required for live TechUtopia calls.")
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("openai package is required for TechUtopia OpenAI-compatible calls.") from exc

        content: list[dict] = [{"type": "text", "text": request.prompt}]
        if self.image_mode == "data_url":
            image_bytes = request.image_path.read_bytes()
            mime_type = mimetypes.guess_type(request.image_path.name)[0] or "image/jpeg"
            data_url = f"data:{mime_type};base64,{base64.b64encode(image_bytes).decode('ascii')}"
            content.append({"type": "image_url", "image_url": {"url": data_url}})
        elif self.image_mode != "none":
            raise ValueError(f"Unsupported TECHUTOPIA_IMAGE_MODE: {self.image_mode}")

        client = OpenAI(api_key=self.api_key, base_url=self.base_url, default_headers=self.default_headers, timeout=60.0)
        response = client.chat.completions.create(
            model=request.model,
            messages=[
                {
                    "role": "user",
                    "content": content,
                }
            ],
            temperature=0,
        )
        raw_text = response.choices[0].message.content or ""
        content = response.model_dump(mode="json") if hasattr(response, "model_dump") else response
        return RawVictimResponse(provider=self.provider_name, model=request.model, content=content, raw_text=raw_text)

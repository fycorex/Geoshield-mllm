from __future__ import annotations

import base64
import mimetypes
import os

from geoshield_mllm.victims.base import RawVictimResponse, VictimProvider, VictimRequest


class TechUtopiaProvider(VictimProvider):
    provider_name = "techutopia"

    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        self.api_key = api_key or os.getenv("TECHUTOPIA_API_KEY")
        self.base_url = (base_url or os.getenv("TECHUTOPIA_BASE_URL") or "https://copilot.techutopia.cn/v1").rstrip("/")

    def infer_geolocation(self, request: VictimRequest) -> RawVictimResponse:
        if not self.api_key:
            raise RuntimeError("TECHUTOPIA_API_KEY is required for live TechUtopia calls.")
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("openai package is required for TechUtopia OpenAI-compatible calls.") from exc

        image_bytes = request.image_path.read_bytes()
        mime_type = mimetypes.guess_type(request.image_path.name)[0] or "image/jpeg"
        data_url = f"data:{mime_type};base64,{base64.b64encode(image_bytes).decode('ascii')}"
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        response = client.chat.completions.create(
            model=request.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": request.prompt},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                }
            ],
            temperature=0,
        )
        raw_text = response.choices[0].message.content or ""
        content = response.model_dump(mode="json") if hasattr(response, "model_dump") else response
        return RawVictimResponse(provider=self.provider_name, model=request.model, content=content, raw_text=raw_text)

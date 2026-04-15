from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class DemoEnv:
    openai_api_key: str
    model: str
    aegis_api_key: str | None
    aegis_base_url: str | None


def load_demo_env() -> DemoEnv:
    load_dotenv()

    openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is required.")

    model = os.getenv("DEMO_MODEL", "openai:gpt-4o-mini").strip()
    aegis_api_key = os.getenv("AEGIS_API_KEY", "").strip() or None
    aegis_base_url = os.getenv("AEGIS_BASE_URL", "").strip() or None

    return DemoEnv(
        openai_api_key=openai_api_key,
        model=model,
        aegis_api_key=aegis_api_key,
        aegis_base_url=aegis_base_url,
    )

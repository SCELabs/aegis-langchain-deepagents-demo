from __future__ import annotations

from typing import Any

from aegis import AegisClient


class AegisDeepAgentsAdapter:
    def __init__(self, *, base_prompt: str, api_key: str | None = None, base_url: str | None = None) -> None:
        self.base_prompt = base_prompt
        self.client = AegisClient(api_key=api_key, base_url=base_url) if (api_key or base_url) else AegisClient()
        self.plan = self.client.auto(
            system_type="multi_agent",
            base_prompt=base_prompt,
            symptoms=["inefficient_execution"],
            severity="low",
            metadata={"demo": "deepagents", "mode": "minimal_generation_only_v2"},
        )

    def apply_system_prompt(self, prompt: str) -> str:
        return prompt

    def generation_kwargs(self) -> dict[str, Any]:
        gen = dict(self.plan.generation_config() or {})

        temperature = gen.get("temperature", 0.4)
        top_p = gen.get("top_p", 1.0)

        temperature = max(0.1, min(float(temperature), 0.4))
        top_p = max(0.8, min(float(top_p), 1.0))

        return {
            "temperature": temperature,
            "top_p": top_p,
        }

    def raw_plan(self) -> dict[str, Any]:
        return dict(self.plan.raw)

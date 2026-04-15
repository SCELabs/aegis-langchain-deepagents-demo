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
            symptoms=[
                "agents_disagree",
                "retry_loops",
                "inefficient_execution",
            ],
            severity="medium",
            metadata={"demo": "deepagents"},
        )

    def apply_system_prompt(self, prompt: str) -> str:
        return self.plan.apply_system_prompt(prompt)

    def generation_kwargs(self) -> dict[str, Any]:
        return dict(self.plan.generation_config() or {})

    def raw_plan(self) -> dict[str, Any]:
        return dict(self.plan.raw)

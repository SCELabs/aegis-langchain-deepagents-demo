from __future__ import annotations

from typing import Any

from aegis import AegisClient, AegisConfig, AegisResult


class AegisDeepAgentsAdapter:
    def __init__(self, *, base_prompt: str, api_key: str | None = None, base_url: str | None = None) -> None:
        self.base_prompt = base_prompt
        self.client = (
            AegisClient(api_key=api_key, base_url=base_url, config=AegisConfig(mode="balanced"))
            if (api_key or base_url)
            else AegisClient(config=AegisConfig(mode="balanced"))
        )
        self.result: AegisResult = self.client.auto().llm(
            base_prompt=base_prompt,
            symptoms=["inefficient_execution"],
            severity="low",
            metadata={"demo": "deepagents", "mode": "minimal_generation_only_v2"},
        )

    def apply_system_prompt(self, prompt: str) -> str:
        return prompt

    def _generation_hints(self) -> dict[str, Any]:
        scope_data = getattr(self.result, "scope_data", None)
        if isinstance(scope_data, dict):
            for key in ("generation", "generation_config", "model_config", "params"):
                value = scope_data.get(key)
                if isinstance(value, dict):
                    return value
            return scope_data
        return {}

    def generation_kwargs(self) -> dict[str, Any]:
        gen = dict(self._generation_hints())

        temperature = gen.get("temperature", 0.4)
        top_p = gen.get("top_p", 1.0)

        temperature = max(0.1, min(float(temperature), 0.4))
        top_p = max(0.8, min(float(top_p), 1.0))

        return {
            "temperature": temperature,
            "top_p": top_p,
        }

    def raw_result(self) -> dict[str, Any]:
        return {
            "scope": getattr(self.result, "scope", None),
            "scope_data": getattr(self.result, "scope_data", None),
            "actions": getattr(self.result, "actions", None),
            "trace": getattr(self.result, "trace", None),
            "metrics": getattr(self.result, "metrics", None),
            "used_fallback": getattr(self.result, "used_fallback", None),
            "explanation": getattr(self.result, "explanation", None),
        }

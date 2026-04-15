from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aegis import AegisClient


@dataclass
class SupervisorDecision:
    temperature: float
    top_p: float
    should_stop_early: bool
    should_force_final_json: bool
    notes: list[str]


class AegisLoopSupervisor:
    def __init__(self, *, base_prompt: str, api_key: str | None, base_url: str | None) -> None:
        self.client = AegisClient(api_key=api_key, base_url=base_url) if (api_key or base_url) else AegisClient()
        self.base_prompt = base_prompt

    def decide(
        self,
        *,
        iteration: int,
        model_calls: int,
        tool_calls: int,
        repeated_reads: int,
        last_output: str,
    ) -> SupervisorDecision:
        symptoms: list[str] = []

        if iteration >= 2:
            symptoms.append("inefficient_execution")
        if repeated_reads > 0:
            symptoms.append("retry_loops")
        if last_output and "```" in last_output:
            symptoms.append("format_drift")

        if not symptoms:
            return SupervisorDecision(
                temperature=0.7,
                top_p=1.0,
                should_stop_early=False,
                should_force_final_json=False,
                notes=["no_intervention"],
            )

        plan = self.client.auto(
            system_type="multi_agent",
            base_prompt=self.base_prompt,
            symptoms=symptoms,
            severity="low",
            metadata={
                "demo": "langchain_runtime_supervisor",
                "iteration": iteration,
                "model_calls": model_calls,
                "tool_calls": tool_calls,
                "repeated_reads": repeated_reads,
            },
        )

        gen = dict(plan.generation_config() or {})
        temperature = max(0.1, min(float(gen.get("temperature", 0.4)), 0.7))
        top_p = max(0.8, min(float(gen.get("top_p", 1.0)), 1.0))

        should_stop_early = repeated_reads >= 2 or model_calls >= 4
        should_force_final_json = repeated_reads > 0 or "```" in last_output

        notes = [f"symptoms={','.join(symptoms)}"]

        return SupervisorDecision(
            temperature=temperature,
            top_p=top_p,
            should_stop_early=should_stop_early,
            should_force_final_json=should_force_final_json,
            notes=notes,
        )

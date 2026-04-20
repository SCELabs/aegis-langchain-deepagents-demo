from __future__ import annotations

import json
from pathlib import Path
from statistics import mean
from typing import Any

from langchain_openai import ChatOpenAI

from aegis import AegisClient
from benchmark_v3.cases import CASES
from benchmark_v3.prompts import SYSTEM_PROMPT, VALIDATOR_PROMPT, build_solver_prompt
from benchmark_v3.scoring import evaluate, parse_json
from demo.env import load_demo_env


def invoke_text(model, messages) -> str:
    response = model.invoke(messages)
    return response.content if isinstance(response.content, str) else str(response.content)


def output_looks_good(text: str) -> bool:
    parsed = parse_json(text)
    return (
        isinstance(parsed, dict)
        and isinstance(parsed.get("selected_ids"), list)
        and "average_score" in parsed
        and "rationale" in parsed
    )


def output_matches_task(text: str, items: list[dict]) -> bool:
    parsed = parse_json(text)
    if not isinstance(parsed, dict):
        return False

    ranked = sorted(items, key=lambda x: x["score"], reverse=True)
    expected_top3 = [x["id"] for x in ranked[:3]]
    expected_avg = float(mean(x["score"] for x in items))

    selected_ids = parsed.get("selected_ids")
    average_score = parsed.get("average_score")
    if not isinstance(selected_ids, list):
        return False
    if not isinstance(average_score, (int, float)):
        return False

    ids_ok = selected_ids == expected_top3
    avg_ok = abs(float(average_score) - expected_avg) <= 0.01
    return ids_ok and avg_ok


def _safe_scope_invoke(scope_obj: Any, method: str, kwargs: dict[str, Any]) -> Any:
    """Call scope methods defensively across minor SDK shape differences."""
    fn = getattr(scope_obj, method, None)
    if not callable(fn):
        return scope_obj

    attempt = dict(kwargs)
    for key in ["metadata", "mode", "severity", "symptoms", "base_prompt", "system_type", "name", "input"]:
        try:
            return fn(**attempt)
        except TypeError:
            attempt.pop(key, None)

    try:
        return fn(**attempt)
    except TypeError:
        return scope_obj


def build_scope_result(client: AegisClient, case: dict, solver_prompt: str) -> Any:
    """Use the v0.3 scope-first SDK surface: client.auto().llm(...).step(...)."""
    scope = client.auto()
    scope = _safe_scope_invoke(
        scope,
        "llm",
        {
            "mode": "light",
            "base_prompt": SYSTEM_PROMPT,
            "symptoms": ["inefficient_execution", "inconsistent_outputs"],
            "severity": "low",
            "metadata": {"case_id": case["id"], "demo": "benchmark_v3"},
        },
    )
    scope = _safe_scope_invoke(
        scope,
        "step",
        {
            "name": "benchmark_v3_case",
            "input": {"case_id": case["id"], "task": case["brief"], "prompt": solver_prompt},
            "mode": "light",
        },
    )
    return scope


def resolve_generation_config(scope_result: Any) -> tuple[float, float, dict[str, Any]]:
    gen = {}
    gen_fn = getattr(scope_result, "generation_config", None)
    if callable(gen_fn):
        maybe = gen_fn()
        if isinstance(maybe, dict):
            gen = maybe

    raw = dict(getattr(scope_result, "raw", {}) or {})
    scope_data = raw.get("scope_data") if isinstance(raw.get("scope_data"), dict) else {}
    hint_gen = scope_data.get("generation") if isinstance(scope_data, dict) else {}
    if not isinstance(hint_gen, dict):
        hint_gen = {}

    temperature = hint_gen.get("temperature", gen.get("temperature", 0.25))
    top_p = hint_gen.get("top_p", gen.get("top_p", 0.92))

    temperature = max(0.15, min(float(temperature), 0.35))
    top_p = max(0.85, min(float(top_p), 0.97))
    return temperature, top_p, scope_data


def run(mode: str = "benchmark_v3_aegis") -> Path:
    env = load_demo_env()
    run_root = Path("results") / mode
    run_root.mkdir(parents=True, exist_ok=True)

    client = AegisClient(api_key=env.aegis_api_key, base_url=env.aegis_base_url)

    results = []
    total_calls = 0

    for case in CASES:
        items_text = json.dumps(case["items"], indent=2)
        solver_prompt = build_solver_prompt(case["brief"], items_text)

        scope_result = build_scope_result(client, case, solver_prompt)
        temperature, top_p, scope_data = resolve_generation_config(scope_result)

        model = ChatOpenAI(
            model=env.model.replace("openai:", ""),
            api_key=env.openai_api_key,
            temperature=temperature,
            top_p=top_p,
        )

        answer_1 = invoke_text(model, [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    solver_prompt
                    + "\n\nReturn raw JSON only. No code fences. "
                    + "Be exact about descending score order and average over all items."
                ),
            },
        ])
        total_calls += 1

        local_valid = output_matches_task(answer_1, case["items"])
        schema_valid = output_looks_good(answer_1)
        validation_intensity = "light"
        if isinstance(scope_data, dict):
            validation = scope_data.get("validation")
            if isinstance(validation, dict):
                validation_intensity = str(validation.get("intensity", "light")).lower()

        if local_valid:
            validator = "SKIPPED"
            final_output = answer_1
            calls = 1
        else:
            validator = invoke_text(model, [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"{VALIDATOR_PROMPT}\n\nTask:\n{solver_prompt}\n\nAnswer:\n{answer_1}",
                },
            ])
            total_calls += 1

            if "VALID" in validator.upper() and schema_valid and validation_intensity == "light":
                final_output = answer_1
                calls = 2
            else:
                answer_2 = invoke_text(model, [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": solver_prompt},
                    {"role": "assistant", "content": answer_1},
                    {
                        "role": "user",
                        "content": (
                            "Revise and return final raw JSON only. "
                            "No code fences. No extra keys. "
                            "selected_ids must be exactly the top 3 in descending score order. "
                            "average_score must be computed over all items."
                        ),
                    },
                ])
                total_calls += 1
                final_output = answer_2
                calls = 3

        score = evaluate(final_output, case["expected"])
        results.append(
            {
                "id": case["id"],
                "calls": calls,
                "temperature": temperature,
                "top_p": top_p,
                "schema_valid_first_pass": schema_valid,
                "task_valid_first_pass": local_valid,
                "validation_intensity": validation_intensity,
                "validator": validator,
                "output": final_output,
                **score,
            }
        )

    summary = {
        "mode": mode,
        "cases": len(results),
        "exact_matches": sum(1 for r in results if r["exact_match"]),
        "avg_score": sum(r["score"] for r in results) / len(results),
        "total_model_calls": total_calls,
        "avg_model_calls": total_calls / len(results),
        "results": results,
    }

    (run_root / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return run_root


if __name__ == "__main__":
    path = run()
    print(f"aegis benchmark written to: {path}")
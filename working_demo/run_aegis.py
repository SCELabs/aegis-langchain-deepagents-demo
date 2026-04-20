from __future__ import annotations

import json
from pathlib import Path

from langchain_openai import ChatOpenAI

from aegis import AegisClient, AegisConfig
from demo.env import load_demo_env
from demo.scoring import evaluate_output
from working_demo.prompts import SYSTEM_PROMPT, build_user_prompt
from working_demo.task_data import BRIEF, ITEMS


def _generation_hints(result) -> dict:
    scope_data = getattr(result, "scope_data", None)
    if isinstance(scope_data, dict):
        for key in ("generation", "generation_config", "model_config", "params"):
            value = scope_data.get(key)
            if isinstance(value, dict):
                return value
        return scope_data
    return {}


def _serialize_result(result) -> dict:
    return {
        "scope": getattr(result, "scope", None),
        "scope_data": getattr(result, "scope_data", None),
        "actions": getattr(result, "actions", None),
        "trace": getattr(result, "trace", None),
        "metrics": getattr(result, "metrics", None),
        "used_fallback": getattr(result, "used_fallback", None),
        "explanation": getattr(result, "explanation", None),
    }


def run_aegis(mode: str = "working_aegis_supervised") -> Path:
    env = load_demo_env()
    run_root = Path("results") / mode
    run_root.mkdir(parents=True, exist_ok=True)

    for p in sorted(run_root.rglob("*"), reverse=True):
        if p.is_file():
            p.unlink()

    items_text = json.dumps(ITEMS, indent=2)
    user_prompt = build_user_prompt(BRIEF, items_text)

    client = AegisClient(
        api_key=env.aegis_api_key,
        base_url=env.aegis_base_url,
        config=AegisConfig(mode="balanced"),
    )

    result = client.auto().llm(
        base_prompt=SYSTEM_PROMPT,
        symptoms=["inconsistent_outputs", "inefficient_execution"],
        severity="low",
        metadata={"demo": "working_runtime_optimization"},
    )

    gen = _generation_hints(result)
    temperature = max(0.1, min(float(gen.get("temperature", 0.4)), 0.7))
    top_p = max(0.8, min(float(gen.get("top_p", 1.0)), 1.0))

    model = ChatOpenAI(
        model=env.model.replace("openai:", ""),
        api_key=env.openai_api_key,
        temperature=temperature,
        top_p=top_p,
    )

    response = model.invoke(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt + "\n\nReturn raw JSON only. No code fences."},
        ]
    )

    output = response.content if isinstance(response.content, str) else str(response.content)
    (run_root / "final_output.txt").write_text(output, encoding="utf-8")
    (run_root / "aegis_result.json").write_text(json.dumps(_serialize_result(result), indent=2) + "\n", encoding="utf-8")

    debug_summary = getattr(result, "debug_summary", None)
    if callable(debug_summary):
        (run_root / "aegis_debug_summary.txt").write_text(str(debug_summary()) + "\n", encoding="utf-8")

    workspace = run_root / "workspace"
    workspace.mkdir(exist_ok=True)
    (workspace / "items.json").write_text(items_text + "\n", encoding="utf-8")

    scoring = evaluate_output(run_root, output)

    metrics = {
        "mode": mode,
        "completed": True,
        "model_calls": 1,
        "tool_calls": 0,
        "repeated_tool_signals": 0,
        "parsed_json": scoring["parsed_json"],
        "correct_top3": scoring["correct_top3"],
        "correct_average": scoring["correct_average"],
        "exact_match": scoring["exact_match"],
        "score": scoring["score"],
        "temperature": temperature,
        "top_p": top_p,
        "aegis_scope": getattr(result, "scope", None),
        "aegis_used_fallback": getattr(result, "used_fallback", None),
    }

    (run_root / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    return run_root

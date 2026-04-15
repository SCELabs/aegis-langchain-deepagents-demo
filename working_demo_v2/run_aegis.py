from __future__ import annotations

import json
from pathlib import Path

from langchain_openai import ChatOpenAI

from aegis import AegisClient
from demo.env import load_demo_env
from demo.scoring import evaluate_output
from working_demo.task_data import BRIEF, ITEMS
from working_demo_v2.prompts import SYSTEM_PROMPT, build_user_prompt


def run_aegis(mode: str = "v2_aegis") -> Path:
    env = load_demo_env()
    run_root = Path("results") / mode
    run_root.mkdir(parents=True, exist_ok=True)

    for p in sorted(run_root.rglob("*"), reverse=True):
        if p.is_file():
            p.unlink()

    items_text = json.dumps(ITEMS, indent=2)
    user_prompt = build_user_prompt(BRIEF, items_text)

    client = AegisClient(api_key=env.aegis_api_key, base_url=env.aegis_base_url)

    plan = client.auto(
        system_type="single_agent",
        base_prompt=SYSTEM_PROMPT,
        symptoms=["inefficient_execution"],
        severity="medium",
    )

    gen = plan.generation_config() or {}

    model = ChatOpenAI(
        model=env.model.replace("openai:", ""),
        api_key=env.openai_api_key,
        temperature=gen.get("temperature", 0.3),
    )

    # Aegis version: only ONE pass
    response = model.invoke([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt + "\n\nReturn final answer in one pass. No re-check loop."},
    ])

    output = response.content if isinstance(response.content, str) else str(response.content)

    (run_root / "final_output.txt").write_text(output, encoding="utf-8")
    (run_root / "aegis_plan.json").write_text(json.dumps(plan.raw, indent=2))

    workspace = run_root / "workspace"
    workspace.mkdir(exist_ok=True)
    (workspace / "items.json").write_text(items_text + "\n", encoding="utf-8")

    scoring = evaluate_output(run_root, output)

    metrics = {
        "mode": mode,
        "model_calls": 1,
        "parsed_json": scoring["parsed_json"],
        "correct_top3": scoring["correct_top3"],
        "correct_average": scoring["correct_average"],
        "exact_match": scoring["exact_match"],
        "score": scoring["score"],
    }

    (run_root / "metrics.json").write_text(json.dumps(metrics, indent=2))
    return run_root

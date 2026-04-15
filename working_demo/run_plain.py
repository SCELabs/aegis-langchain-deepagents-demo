from __future__ import annotations

import json
from pathlib import Path

from langchain_openai import ChatOpenAI

from demo.env import load_demo_env
from demo.scoring import evaluate_output
from working_demo.prompts import SYSTEM_PROMPT, build_user_prompt
from working_demo.task_data import BRIEF, ITEMS


def run_plain(mode: str = "working_plain_baseline") -> Path:
    env = load_demo_env()
    run_root = Path("results") / mode
    run_root.mkdir(parents=True, exist_ok=True)

    for p in sorted(run_root.rglob("*"), reverse=True):
        if p.is_file():
            p.unlink()

    items_text = json.dumps(ITEMS, indent=2)
    user_prompt = build_user_prompt(BRIEF, items_text)

    model = ChatOpenAI(
        model=env.model.replace("openai:", ""),
        api_key=env.openai_api_key,
        temperature=0.7,
        top_p=1.0,
    )

    response = model.invoke(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
    )

    output = response.content if isinstance(response.content, str) else str(response.content)
    (run_root / "final_output.txt").write_text(output, encoding="utf-8")

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
    }

    (run_root / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    return run_root

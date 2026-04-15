from __future__ import annotations

import json
from pathlib import Path

from langchain_openai import ChatOpenAI

from demo.env import load_demo_env
from demo.scoring import evaluate_output
from scenarios.file_selection import SYSTEM_PROMPT, USER_TASK, build_workspace
from supervisor.agent_loop import run_agent_loop, save_loop_artifacts


def run_plain(*, mode: str) -> Path:
    env = load_demo_env()
    run_root = Path("results") / mode
    run_root.mkdir(parents=True, exist_ok=True)

    for p in sorted(run_root.rglob("*"), reverse=True):
        if p.is_file():
            p.unlink()

    build_workspace(run_root)

    model = ChatOpenAI(
        model=env.model.replace("openai:", ""),
        api_key=env.openai_api_key,
        temperature=0.7,
        top_p=1.0,
    )

    state = run_agent_loop(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        user_task=USER_TASK,
        run_root=run_root,
        max_iterations=6,
    )
    save_loop_artifacts(run_root, state)

    scoring = evaluate_output(run_root, state.final_output)
    metrics = {
        "mode": mode,
        "completed": state.completed,
        "model_calls": state.model_calls,
        "tool_calls": state.tool_calls,
        "repeated_tool_signals": state.repeated_reads,
        "parsed_json": scoring["parsed_json"],
        "correct_top3": scoring["correct_top3"],
        "correct_average": scoring["correct_average"],
        "exact_match": scoring["exact_match"],
        "score": scoring["score"],
    }

    (run_root / "metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n",
        encoding="utf-8",
    )

    return run_root

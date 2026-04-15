from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from langchain_openai import ChatOpenAI

from demo.env import load_demo_env
from demo.scoring import evaluate_output
from scenarios.file_selection import SYSTEM_PROMPT, USER_TASK, build_workspace
from supervisor.aegis_supervisor import AegisLoopSupervisor


def run_supervised(*, mode: str) -> Path:
    env = load_demo_env()
    run_root = Path("results") / mode
    run_root.mkdir(parents=True, exist_ok=True)

    for p in sorted(run_root.rglob("*"), reverse=True):
        if p.is_file():
            p.unlink()

    build_workspace(run_root)

    supervisor = AegisLoopSupervisor(
        base_prompt=SYSTEM_PROMPT,
        api_key=env.aegis_api_key,
        base_url=env.aegis_base_url,
    )

    messages: list[dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_TASK},
    ]

    model_calls = 0
    tool_calls = 0
    repeated_reads = 0
    read_counts: dict[str, int] = {}
    final_output = ""
    completed = False
    decision_log: list[dict[str, Any]] = []

    for iteration in range(1, 7):
        decision = supervisor.decide(
            iteration=iteration,
            model_calls=model_calls,
            tool_calls=tool_calls,
            repeated_reads=repeated_reads,
            last_output=final_output,
        )

        model = ChatOpenAI(
            model=env.model.replace("openai:", ""),
            api_key=env.openai_api_key,
            temperature=decision.temperature,
            top_p=decision.top_p,
        )

        if decision.should_force_final_json:
            working_messages = messages + [
                {
                    "role": "user",
                    "content": "Return the final answer now. Output raw JSON only. Do not use code fences.",
                }
            ]
        else:
            working_messages = list(messages)

        response = model.invoke(working_messages)
        model_calls += 1

        text = response.content if isinstance(response.content, str) else str(response.content)
        messages.append({"role": "assistant", "content": text})

        decision_log.append(
            {
                "iteration": iteration,
                "temperature": decision.temperature,
                "top_p": decision.top_p,
                "should_stop_early": decision.should_stop_early,
                "should_force_final_json": decision.should_force_final_json,
                "notes": decision.notes,
                "assistant_output": text,
            }
        )

        lowered = text.lower()
        requested = []
        if "brief.md" in lowered:
            requested.append("/workspace/brief.md")
        if "items.json" in lowered:
            requested.append("/workspace/items.json")

        if text.strip().startswith("{"):
            final_output = text
            completed = True
            break

        if text.strip().startswith("```json") or text.strip().startswith("```"):
            final_output = text
            completed = True
            break

        if decision.should_stop_early and iteration >= 3:
            messages.append(
                {
                    "role": "user",
                    "content": "Stop exploring. Return the final JSON answer now with no code fences.",
                }
            )

        if not requested:
            messages.append(
                {
                    "role": "user",
                    "content": "Read the required files if needed. Then return the final JSON.",
                }
            )
            continue

        for rel_path in requested:
            read_counts[rel_path] = read_counts.get(rel_path, 0) + 1
            if read_counts[rel_path] > 1:
                repeated_reads += 1
            tool_calls += 1

            content = (run_root / rel_path.lstrip("/")).read_text(encoding="utf-8")
            messages.append(
                {
                    "role": "user",
                    "content": f"FILE CONTENT {rel_path}:\n\n{content}",
                }
            )

    (run_root / "decision_log.json").write_text(
        json.dumps(decision_log, indent=2) + "\n",
        encoding="utf-8",
    )
    (run_root / "final_output.txt").write_text(final_output, encoding="utf-8")

    scoring = evaluate_output(run_root, final_output)
    metrics = {
        "mode": mode,
        "completed": completed,
        "model_calls": model_calls,
        "tool_calls": tool_calls,
        "repeated_tool_signals": repeated_reads,
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

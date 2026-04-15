from __future__ import annotations

import json
from pathlib import Path

from langchain_openai import ChatOpenAI

from demo.env import load_demo_env
from benchmark_v3.cases import CASES
from benchmark_v3.prompts import SYSTEM_PROMPT, VALIDATOR_PROMPT, build_solver_prompt
from benchmark_v3.scoring import evaluate

def invoke_text(model, messages) -> str:
    response = model.invoke(messages)
    return response.content if isinstance(response.content, str) else str(response.content)

def run(mode: str = "benchmark_v3_baseline") -> Path:
    env = load_demo_env()
    run_root = Path("results") / mode
    run_root.mkdir(parents=True, exist_ok=True)

    results = []
    total_calls = 0

    model = ChatOpenAI(
        model=env.model.replace("openai:", ""),
        api_key=env.openai_api_key,
        temperature=0.7,
        top_p=1.0,
    )

    for case in CASES:
        items_text = json.dumps(case["items"], indent=2)
        solver_prompt = build_solver_prompt(case["brief"], items_text)

        planner = invoke_text(model, [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "Plan how to solve this task briefly, then proceed."},
        ])
        total_calls += 1

        answer_1 = invoke_text(model, [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": solver_prompt},
        ])
        total_calls += 1

        validator = invoke_text(model, [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"{VALIDATOR_PROMPT}\n\nTask:\n{solver_prompt}\n\nAnswer:\n{answer_1}"},
        ])
        total_calls += 1

        if "VALID" in validator.upper():
            final_output = answer_1
            calls = 3
        else:
            answer_2 = invoke_text(model, [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": solver_prompt},
                {"role": "assistant", "content": answer_1},
                {"role": "user", "content": "Revise the answer and return final JSON only."},
            ])
            total_calls += 1
            final_output = answer_2
            calls = 4

        score = evaluate(final_output, case["expected"])
        results.append({
            "id": case["id"],
            "calls": calls,
            "output": final_output,
            **score,
        })

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
    print(f"baseline benchmark written to: {path}")

from __future__ import annotations

import json
from pathlib import Path

from langchain_openai import ChatOpenAI

from aegis import AegisClient
from demo.env import load_demo_env
from benchmark_v3.cases import CASES
from benchmark_v3.prompts import SYSTEM_PROMPT, VALIDATOR_PROMPT, build_solver_prompt
from benchmark_v3.scoring import evaluate, parse_json


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

        plan = client.auto(
            system_type="single_agent",
            base_prompt=SYSTEM_PROMPT,
            symptoms=["inefficient_execution", "inconsistent_outputs"],
            severity="medium",
            metadata={"case_id": case["id"], "demo": "benchmark_v3"},
        )

        gen = plan.generation_config() or {}
        temperature = max(0.1, min(float(gen.get("temperature", 0.2)), 0.4))
        top_p = max(0.8, min(float(gen.get("top_p", 0.9)), 1.0))

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

        if output_looks_good(answer_1):
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

            if "VALID" in validator.upper():
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
        results.append({
            "id": case["id"],
            "calls": calls,
            "temperature": temperature,
            "top_p": top_p,
            "validator": validator,
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
    print(f"aegis benchmark written to: {path}")

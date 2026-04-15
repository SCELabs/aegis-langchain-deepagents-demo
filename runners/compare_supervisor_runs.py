from __future__ import annotations

import json
from pathlib import Path


def load_metrics(name: str) -> dict:
    path = Path("results") / name / "metrics.json"
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    baseline = load_metrics("plain_supervisor_baseline")
    aegis = load_metrics("aegis_supervisor")

    print("=" * 60)
    print("PLAIN BASELINE")
    print("=" * 60)
    print(json.dumps(baseline, indent=2))

    print("\n" + "=" * 60)
    print("AEGIS SUPERVISOR")
    print("=" * 60)
    print(json.dumps(aegis, indent=2))

    print("\n" + "=" * 60)
    print("RESULT")
    print("=" * 60)
    for key in [
        "completed",
        "correct_top3",
        "correct_average",
        "exact_match",
        "score",
        "model_calls",
        "tool_calls",
        "repeated_tool_signals",
    ]:
        print(f"{key}: baseline={baseline.get(key)} | aegis={aegis.get(key)}")

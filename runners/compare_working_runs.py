from __future__ import annotations

import json
from pathlib import Path


def load_metrics(name: str) -> dict:
    path = Path("results") / name / "metrics.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_output(name: str) -> str:
    path = Path("results") / name / "final_output.txt"
    return path.read_text(encoding="utf-8", errors="ignore").strip()


def main() -> None:
    baseline = load_metrics("working_plain_baseline")
    aegis = load_metrics("working_aegis_supervised")

    print("=" * 60)
    print("WORKING BASELINE")
    print("=" * 60)
    print(json.dumps(baseline, indent=2))
    print("\nOUTPUT:")
    print(load_output("working_plain_baseline"))

    print("\n" + "=" * 60)
    print("WORKING AEGIS")
    print("=" * 60)
    print(json.dumps(aegis, indent=2))
    print("\nOUTPUT:")
    print(load_output("working_aegis_supervised"))

    print("\n" + "=" * 60)
    print("RESULT")
    print("=" * 60)
    for key in [
        "correct_top3",
        "correct_average",
        "exact_match",
        "score",
        "model_calls",
        "tool_calls",
        "repeated_tool_signals",
    ]:
        print(f"{key}: baseline={baseline.get(key)} | aegis={aegis.get(key)}")

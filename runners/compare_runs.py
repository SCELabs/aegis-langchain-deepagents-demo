from __future__ import annotations

import json
from pathlib import Path


def load_metrics(name: str) -> dict:
    path = Path("results") / name / "metrics.json"
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    baseline = load_metrics("baseline")
    aegis = load_metrics("aegis")

    print("=" * 60)
    print("BASELINE")
    print("=" * 60)
    print(json.dumps(baseline, indent=2))

    print("\n" + "=" * 60)
    print("AEGIS")
    print("=" * 60)
    print(json.dumps(aegis, indent=2))

    print("\n" + "=" * 60)
    print("RESULT")
    print("=" * 60)

    print(f"Top 3 correct: baseline={baseline['correct_top3']} | aegis={aegis['correct_top3']}")
    print(f"Average correct: baseline={baseline['correct_average']} | aegis={aegis['correct_average']}")
    print(f"Exact match: baseline={baseline['exact_match']} | aegis={aegis['exact_match']}")
    print(f"Score: baseline={baseline['score']} | aegis={aegis['score']}")
    print(f"Model calls: baseline={baseline['model_calls']} | aegis={aegis['model_calls']}")
    print(f"Tool calls: baseline={baseline['tool_calls']} | aegis={aegis['tool_calls']}")
    print(f"Repeated read signals: baseline={baseline['repeated_tool_signals']} | aegis={aegis['repeated_tool_signals']}")


if __name__ == "__main__":
    main()

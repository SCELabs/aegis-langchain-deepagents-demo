from __future__ import annotations

import json
from pathlib import Path


def load_json(path: Path) -> dict:
    if not path.exists():
        return {"missing": True, "path": str(path)}
    return json.loads(path.read_text(encoding="utf-8"))


def load_metrics(name: str) -> dict:
    return load_json(Path("results") / name / "metrics.json")


def load_output(name: str) -> str:
    path = Path("results") / name / "final_output.txt"
    if not path.exists():
        return "missing"
    return path.read_text(encoding="utf-8", errors="ignore").strip()


def load_error(name: str) -> str:
    path = Path("results") / name / "error.txt"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore").strip()


def main() -> None:
    baseline = load_metrics("baseline")
    aegis = load_metrics("aegis")

    print("=" * 60)
    print("BASELINE")
    print("=" * 60)
    print(json.dumps(baseline, indent=2))
    print("\nOUTPUT:")
    print(load_output("baseline"))
    baseline_error = load_error("baseline")
    if baseline_error:
        print("\nERROR:")
        print(baseline_error)

    print("\n" + "=" * 60)
    print("AEGIS")
    print("=" * 60)
    print(json.dumps(aegis, indent=2))
    print("\nOUTPUT:")
    print(load_output("aegis"))
    aegis_error = load_error("aegis")
    if aegis_error:
        print("\nERROR:")
        print(aegis_error)

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
        "completed",
    ]:
        print(f"{key}: baseline={baseline.get(key)} | aegis={aegis.get(key)}")


if __name__ == "__main__":
    main()

import json
from pathlib import Path

for name in ["benchmark_v3_baseline", "benchmark_v3_aegis"]:
    path = Path("results") / name / "summary.json"
    data = json.loads(path.read_text())
    print("=" * 80)
    print(name.upper())
    print("=" * 80)
    for r in data["results"]:
        print(
            f"{r['id']} | calls={r['calls']} | "
            f"parsed={r['parsed_json']} | "
            f"top3={r['correct_top3']} | "
            f"avg={r['correct_average']} | "
            f"exact={r['exact_match']}"
        )
        print("output:", r["output"])
        print("-" * 80)

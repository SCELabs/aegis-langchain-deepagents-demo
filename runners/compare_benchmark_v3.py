import json
from pathlib import Path

def load(name):
    return json.loads((Path("results") / name / "summary.json").read_text())

b = load("benchmark_v3_baseline")
a = load("benchmark_v3_aegis")

print("=" * 60)
print("BASELINE")
print("=" * 60)
print(json.dumps({
    "cases": b["cases"],
    "exact_matches": b["exact_matches"],
    "avg_score": b["avg_score"],
    "total_model_calls": b["total_model_calls"],
    "avg_model_calls": b["avg_model_calls"],
}, indent=2))

print("\n" + "=" * 60)
print("AEGIS")
print("=" * 60)
print(json.dumps({
    "cases": a["cases"],
    "exact_matches": a["exact_matches"],
    "avg_score": a["avg_score"],
    "total_model_calls": a["total_model_calls"],
    "avg_model_calls": a["avg_model_calls"],
}, indent=2))

print("\n" + "=" * 60)
print("RESULT")
print("=" * 60)
print(f"Exact matches: {b['exact_matches']} -> {a['exact_matches']}")
print(f"Average score: {b['avg_score']} -> {a['avg_score']}")
print(f"Total model calls: {b['total_model_calls']} -> {a['total_model_calls']}")
print(f"Average model calls: {b['avg_model_calls']} -> {a['avg_model_calls']}")
print(f"Call reduction: {b['total_model_calls'] - a['total_model_calls']}")

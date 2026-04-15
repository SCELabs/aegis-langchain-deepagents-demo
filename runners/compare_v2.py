import json
from pathlib import Path

def load(name):
    return json.loads((Path("results") / name / "metrics.json").read_text())

b = load("v2_plain_baseline")
a = load("v2_aegis")

print("=" * 60)
print("BASELINE")
print("=" * 60)
print(json.dumps(b, indent=2))

print("\n" + "=" * 60)
print("AEGIS")
print("=" * 60)
print(json.dumps(a, indent=2))

print("\n" + "=" * 60)
print("RESULT")
print("=" * 60)
print(f"Model calls: {b['model_calls']} -> {a['model_calls']}")
print(f"Exact match: {b['exact_match']} -> {a['exact_match']}")
print(f"Score: {b['score']} -> {a['score']}")
print(f"Call reduction: {b['model_calls'] - a['model_calls']}")

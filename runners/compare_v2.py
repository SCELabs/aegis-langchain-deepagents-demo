import json
from pathlib import Path

def load(name):
    return json.loads((Path("results")/name/"metrics.json").read_text())

b = load("v2_plain_baseline")
a = load("v2_aegis")

print("BASELINE:", b)
print("AEGIS:", a)

print("\nRESULT:")
print("model_calls:", b["model_calls"], "->", a["model_calls"])
print("score:", b["score"], "->", a["score"])

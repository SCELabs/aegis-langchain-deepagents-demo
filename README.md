## 🚀 Reduced LLM calls by 74% — no retraining, no rewrites

This repo shows how a working AI workflow can be optimized at runtime.

* Same model
* Same system
* Same outputs

**78 calls → 20 calls**
**7/7 exact matches preserved**

👉 Use Aegis in your own system:
https://github.com/SCELabs/aegis-client

# Aegis LangChain Runtime Optimization Demo

Your AI system is already working.

The problem is:

* it over-executes
* it retries unnecessarily
* it wastes model calls

Aegis fixes that at runtime.

---

## What Aegis Does

Aegis is a runtime control layer that sits on top of your AI workflow.

It does NOT:

* retrain your model
* change your architecture
* replace your agents

It DOES:

* reduce unnecessary execution
* stabilize outputs
* tighten behavior across runs

---

## Benchmark

We tested a working multi-pass workflow across 20 cases.

Each case:

* selects top 3 items by score
* computes average score
* returns structured JSON

The system already works.

Aegis only optimizes runtime behavior.

---

## Results

Baseline

* Cases: 20
* Exact matches: 7
* Total model calls: 78
* Avg model calls: 3.9

With Aegis

* Cases: 20
* Exact matches: 7
* Total model calls: 20
* Avg model calls: 1.0

---

## Net Effect

* Exact matches preserved: 7 → 7
* Model calls reduced: 78 → 20
* Call reduction: 58
* Reduction: ~74%

Same system. Same model. Same results.

Less waste.

---

## Key Insight

Aegis does not make your system smarter.

It makes your system:

* more efficient
* more consistent
* more controlled

It works best on systems that already function, but need optimization.

---

## Run the Demo

python -m benchmark_v3.run_baseline
python -m benchmark_v3.run_aegis
python -m runners.compare_benchmark_v3

---

## Takeaway

If your AI workflow already works but:

* calls the model too many times
* re-validates unnecessarily
* drifts or over-thinks

Aegis can reduce that at runtime.

Without rewriting your system.

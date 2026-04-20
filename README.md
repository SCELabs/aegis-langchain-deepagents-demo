# Aegis LangChain DeepAgents Demo

This demo shows how Aegis stabilizes runtime behavior in an existing LangChain/DeepAgents workflow **without changing the underlying model or redesigning the app**.

- Same task and prompts  
- Same workflow shape  
- Aegis inserted as a runtime control layer  

---

## What this demo proves

Aegis is used as a **scope-first runtime SDK**:

- `client.auto().llm(...)` for model-call stabilization  
- `client.auto().step(...)` for loop/supervisor step stabilization (where applicable)  

This repository **does not use the legacy plan-first mental model**.

---

## Aegis SDK surface used

```python
from aegis import AegisClient, AegisConfig
import os

client = AegisClient(
    api_key=os.environ["AEGIS_API_KEY"],
    base_url=os.getenv("AEGIS_BASE_URL"),
    config=AegisConfig(mode="balanced"),
)

result = client.auto().llm(...)
```

Returned `AegisResult` values are inspected in the demo outputs, including:

- `actions`
- `trace`
- `metrics`
- `used_fallback`
- `explanation`
- `scope`
- `scope_data`

---

## Environment

### Required

- `OPENAI_API_KEY`
- `AEGIS_API_KEY`

### Optional

- `AEGIS_BASE_URL` (set explicitly if not using default endpoint)
- `DEMO_MODEL` (default: `openai:gpt-4o-mini`)

### Example `.env`

```env
OPENAI_API_KEY=...
AEGIS_API_KEY=...
AEGIS_BASE_URL=http://localhost:8080
DEMO_MODEL=openai:gpt-4o-mini
```

---

## Run

```bash
python -m benchmark_v3.run_baseline
python -m benchmark_v3.run_aegis
python -m runners.compare_benchmark_v3
```

### Other runnable variants

```bash
python -m runners.run_aegis
python -m runners.run_working_aegis
python -m runners.run_v2_aegis
python -m runners.run_aegis_supervisor
```

---

## What to inspect in outputs

Aegis runs emit:

- `aegis_result*.json` files (replacing old plan artifacts)
- optional `aegis_debug_summary.txt`

Inspect:

- `actions` → applied runtime controls  
- `used_fallback` → whether fallback behavior was triggered  
- `trace` / `metrics` → decision and execution context  

---

## Key takeaway

This demo shows how Aegis sits **above an existing system** to:

- reduce waste  
- stabilize behavior  
- improve consistency  

…without changing the underlying model integration.
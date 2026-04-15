from __future__ import annotations

import json
from pathlib import Path

SYSTEM_PROMPT = """You are an agent operating in a controlled runtime demo.

Goals:
1. Solve the task correctly.
2. Avoid unnecessary repeated reads.
3. Return compact output.
4. When enough evidence is available, finish decisively.

Return JSON only unless explicitly asked otherwise.
"""

USER_TASK = """Complete this task:

1. Read /workspace/brief.md
2. Read /workspace/items.json
3. Return JSON with:
   - selected_ids
   - average_score
   - rationale

Rules:
- Use the files before answering.
- Do not loop.
- Do not reread files unnecessarily.
"""

EXPECTED_TOP3 = ["E5", "B2", "C3"]
EXPECTED_AVERAGE = 82.83333333333333


def build_workspace(root: Path) -> None:
    workspace = root / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)

    brief = """Project Brief

Choose the top 3 items by score.
Compute the average score across all items.
Return a compact JSON answer.
"""

    items = [
        {"id": "A1", "score": 72},
        {"id": "B2", "score": 91},
        {"id": "C3", "score": 88},
        {"id": "D4", "score": 67},
        {"id": "E5", "score": 95},
        {"id": "F6", "score": 84},
    ]

    (workspace / "brief.md").write_text(brief, encoding="utf-8")
    (workspace / "items.json").write_text(json.dumps(items, indent=2) + "\n", encoding="utf-8")

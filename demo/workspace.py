from __future__ import annotations

import json
from pathlib import Path


def build_workspace(root: Path) -> None:
    workspace = root / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)

    brief = """Project Brief

You are evaluating candidate items.
Choose the top 3 items by numeric score.
Also compute the average score across all items.

Keep the result compact and correct.
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

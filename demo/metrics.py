from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class RunMetrics:
    mode: str
    completed: bool = False
    model_calls: int = 0
    tool_calls: int = 0
    repeated_tool_signals: int = 0
    final_output_present: bool = False
    output_path: str = ""
    notes: list[str] = field(default_factory=list)

    parsed_json: bool = False
    selected_ids: list[str] = field(default_factory=list)
    average_score: float | None = None

    correct_top3: bool = False
    correct_average: bool = False
    exact_match: bool = False
    score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2) + "\n", encoding="utf-8")

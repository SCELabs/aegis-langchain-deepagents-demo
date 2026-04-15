from __future__ import annotations

import json
from pathlib import Path
from typing import Any

EXPECTED_TOP3 = ["E5", "B2", "C3"]
EXPECTED_AVERAGE = 82.83333333333333

# Accept normal rounded presentation like 82.83
AVERAGE_TOLERANCE = 0.01


def load_expected_from_workspace(run_root: Path) -> dict[str, Any]:
    items_path = run_root / "workspace" / "items.json"
    items = json.loads(items_path.read_text(encoding="utf-8"))

    ranked = sorted(items, key=lambda x: x["score"], reverse=True)
    top3 = [item["id"] for item in ranked[:3]]
    average = sum(item["score"] for item in items) / len(items)

    return {
        "expected_top3": top3,
        "expected_average": average,
    }


def _strip_code_fences(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return stripped


def parse_output_json(text: str) -> dict[str, Any] | None:
    text = _strip_code_fences(text)
    if not text:
        return None

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Fallback: try extracting the first JSON object region
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = text[start : end + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            return None

    return None


def evaluate_output(run_root: Path, output_text: str) -> dict[str, Any]:
    expected = load_expected_from_workspace(run_root)
    parsed = parse_output_json(output_text)

    result = {
        "parsed_json": False,
        "selected_ids": [],
        "average_score": None,
        "correct_top3": False,
        "correct_average": False,
        "exact_match": False,
        "score": 0.0,
        "expected_top3": expected["expected_top3"],
        "expected_average": expected["expected_average"],
    }

    if not isinstance(parsed, dict):
        return result

    result["parsed_json"] = True

    selected_ids = parsed.get("selected_ids")
    average_score = parsed.get("average_score")

    if isinstance(selected_ids, list) and all(isinstance(x, str) for x in selected_ids):
        result["selected_ids"] = selected_ids
        result["correct_top3"] = selected_ids == expected["expected_top3"]

    if isinstance(average_score, (int, float)):
        avg = float(average_score)
        result["average_score"] = avg
        result["correct_average"] = abs(avg - expected["expected_average"]) <= AVERAGE_TOLERANCE

    result["exact_match"] = result["correct_top3"] and result["correct_average"]

    score = 0.0
    if result["parsed_json"]:
        score += 0.2
    if result["correct_top3"]:
        score += 0.4
    if result["correct_average"]:
        score += 0.4
    result["score"] = score

    return result

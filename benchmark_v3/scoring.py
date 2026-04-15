from __future__ import annotations

import json

TOLERANCE = 0.01

def strip_fences(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        lines = t.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return t

def parse_json(text: str):
    t = strip_fences(text)
    try:
        return json.loads(t)
    except Exception:
        start = t.find("{")
        end = t.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(t[start:end+1])
            except Exception:
                return None
    return None

def evaluate(output_text: str, expected: dict) -> dict:
    parsed = parse_json(output_text)
    result = {
        "parsed_json": False,
        "correct_top3": False,
        "correct_average": False,
        "exact_match": False,
        "score": 0.0,
    }

    if not isinstance(parsed, dict):
        return result

    result["parsed_json"] = True

    ids_ok = parsed.get("selected_ids") == expected["selected_ids"]
    avg = parsed.get("average_score")
    avg_ok = isinstance(avg, (int, float)) and abs(float(avg) - expected["average_score"]) <= TOLERANCE

    result["correct_top3"] = ids_ok
    result["correct_average"] = avg_ok
    result["exact_match"] = ids_ok and avg_ok

    score = 0.0
    if result["parsed_json"]:
        score += 0.2
    if ids_ok:
        score += 0.4
    if avg_ok:
        score += 0.4
    result["score"] = score
    return result

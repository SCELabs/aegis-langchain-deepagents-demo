from __future__ import annotations

SYSTEM_PROMPT = """You are part of a structured agent workflow.

Be accurate, concise, and consistent.
Return JSON only unless explicitly asked otherwise.
"""

def build_solver_prompt(brief: str, items_text: str) -> str:
    return f"""Task brief:
{brief}

Dataset:
{items_text}

Return JSON with:
- selected_ids
- average_score
- rationale
"""

VALIDATOR_PROMPT = """Validate the answer against the task.
If it is already correct and well-formed, return:
VALID

If not, return:
REVISE
"""

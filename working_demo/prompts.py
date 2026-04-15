from __future__ import annotations

SYSTEM_PROMPT = """You are part of a working agent workflow.

Your job:
- analyze the provided task data
- return correct structured output
- be concise
- avoid unnecessary extra reasoning
- do not repeat earlier work unless needed

Output JSON only unless explicitly asked otherwise.
"""

def build_user_prompt(brief: str, items_text: str) -> str:
    return f"""Task brief:
{brief}

Dataset:
{items_text}

Return JSON with:
- selected_ids
- average_score
- rationale
"""

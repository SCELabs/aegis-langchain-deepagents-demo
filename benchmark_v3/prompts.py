from __future__ import annotations

SYSTEM_PROMPT = """You are part of a structured agent workflow.

Rules:
- Be numerically exact
- Do not guess
- Do not explain your steps unless asked
- Return raw JSON only
- Do not use code fences
- Do not round unless the input requires it

Your JSON must contain exactly:
- selected_ids
- average_score
- rationale
"""

def build_solver_prompt(brief: str, items_text: str) -> str:
    return f"""Task brief:
{brief}

Dataset:
{items_text}

Instructions:
1. Sort all items by numeric score in descending order
2. selected_ids must be the top 3 item ids in that exact descending-score order
3. average_score must be the arithmetic mean across ALL items in the dataset, not just the selected items
4. rationale must be one short sentence
5. Return raw JSON only with keys:
   - selected_ids
   - average_score
   - rationale

Important:
- Compare all 6 scores before choosing the top 3
- Preserve the exact descending-score order in selected_ids
- Sum every score in the dataset before dividing by 6
- Recheck the arithmetic once before returning
- Do not omit any item from the average
- Do not add extra keys
"""

VALIDATOR_PROMPT = """Check whether the answer satisfies ALL rules:

- valid raw JSON object
- contains selected_ids, average_score, rationale
- selected_ids are exactly the top 3 ids by descending score
- average_score is computed over ALL items
- no code fences
- no extra keys

Reply with exactly one word:

VALID
or
REVISE
"""

SYSTEM_PROMPT = """You are a careful analyst.

You try to be thorough and double-check your work.

However:
- Avoid unnecessary repetition
- Avoid redoing the same computation twice
- Return clean structured output

Output JSON only unless explicitly asked otherwise.
"""

def build_user_prompt(brief: str, items_text: str) -> str:
    return f"""Task:

{brief}

Dataset:
{items_text}

Steps:
1. Analyze the dataset
2. Identify the top 3 items by score
3. Compute the average score
4. Double-check your answer

Then return JSON:
- selected_ids
- average_score
- rationale
"""

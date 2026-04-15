from __future__ import annotations

SYSTEM_PROMPT = """You are running a constrained DeepAgents demo.

Your goals:
1. Solve the user's task correctly.
2. Keep execution tight and efficient.
3. Avoid unnecessary replanning or repeated tool usage.
4. Do not repeat the same check twice unless new information appears.
5. Give the final answer in a compact structured form.

When enough evidence is available, finish decisively.
"""

USER_TASK = """Use the available tools to complete this task:

1. Read the project brief in /workspace/brief.md
2. Read the dataset in /workspace/items.json
3. Produce a final answer with:
   - the selected top 3 items by score
   - the average score across all items
   - one short rationale line

Rules:
- You must inspect the files before answering.
- Do not loop.
- Do not reread files unnecessarily.
- Return JSON only with keys:
  selected_ids, average_score, rationale
"""

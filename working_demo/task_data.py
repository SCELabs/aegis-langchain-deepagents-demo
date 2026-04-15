from __future__ import annotations

ITEMS = [
    {"id": "A1", "score": 72},
    {"id": "B2", "score": 91},
    {"id": "C3", "score": 88},
    {"id": "D4", "score": 67},
    {"id": "E5", "score": 95},
    {"id": "F6", "score": 84},
]

BRIEF = """Choose the top 3 items by score.
Also compute the average score across all items.
Return compact JSON only.
"""

EXPECTED_TOP3 = ["E5", "B2", "C3"]
EXPECTED_AVERAGE = 82.83333333333333

from __future__ import annotations

from statistics import mean

SEEDS = [
    [72, 91, 88, 67, 95, 84],
    [10, 44, 31, 99, 65, 80],
    [55, 56, 57, 58, 59, 60],
    [100, 30, 40, 50, 60, 70],
    [12, 14, 16, 18, 20, 22],
    [5, 15, 25, 35, 45, 55],
    [77, 12, 83, 49, 91, 68],
    [9, 19, 29, 39, 49, 59],
    [63, 71, 82, 54, 96, 88],
    [11, 22, 33, 44, 66, 99],
    [73, 64, 85, 92, 58, 47],
    [13, 27, 41, 55, 69, 83],
    [90, 81, 72, 63, 54, 45],
    [14, 28, 42, 56, 70, 84],
    [61, 79, 88, 93, 57, 46],
    [18, 26, 34, 42, 50, 58],
    [97, 65, 76, 84, 53, 41],
    [21, 32, 43, 54, 65, 76],
    [87, 74, 69, 91, 58, 62],
    [24, 36, 48, 60, 72, 84],
]


def _make_case(idx: int, scores: list[int]) -> dict:
    ids = [f"C{idx:02d}_{i+1}" for i in range(len(scores))]
    items = [{"id": item_id, "score": score} for item_id, score in zip(ids, scores)]

    ranked = sorted(items, key=lambda x: x["score"], reverse=True)
    expected_top3 = [x["id"] for x in ranked[:3]]
    expected_avg = mean(x["score"] for x in items)

    return {
        "id": f"case_{idx:02d}",
        "brief": "Select the top 3 items by score and compute the average score across all items.",
        "items": items,
        "expected": {
            "selected_ids": expected_top3,
            "average_score": float(expected_avg),
        },
    }


CASES = [_make_case(i + 1, scores) for i, scores in enumerate(SEEDS)]

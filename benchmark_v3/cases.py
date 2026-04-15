from __future__ import annotations

CASES = [
    {
        "id": "case_01",
        "brief": "Select the top 3 items by score and compute the average score.",
        "items": [
            {"id": "A1", "score": 72},
            {"id": "B2", "score": 91},
            {"id": "C3", "score": 88},
            {"id": "D4", "score": 67},
            {"id": "E5", "score": 95},
            {"id": "F6", "score": 84},
        ],
        "expected": {
            "selected_ids": ["E5", "B2", "C3"],
            "average_score": 82.83333333333333,
        },
    },
    {
        "id": "case_02",
        "brief": "Select the top 3 items by score and compute the average score.",
        "items": [
            {"id": "A", "score": 10},
            {"id": "B", "score": 44},
            {"id": "C", "score": 31},
            {"id": "D", "score": 99},
            {"id": "E", "score": 65},
            {"id": "F", "score": 80},
        ],
        "expected": {
            "selected_ids": ["D", "F", "E"],
            "average_score": 54.833333333333336,
        },
    },
    {
        "id": "case_03",
        "brief": "Select the top 3 items by score and compute the average score.",
        "items": [
            {"id": "K1", "score": 55},
            {"id": "K2", "score": 56},
            {"id": "K3", "score": 57},
            {"id": "K4", "score": 58},
            {"id": "K5", "score": 59},
            {"id": "K6", "score": 60},
        ],
        "expected": {
            "selected_ids": ["K6", "K5", "K4"],
            "average_score": 57.5,
        },
    },
    {
        "id": "case_04",
        "brief": "Select the top 3 items by score and compute the average score.",
        "items": [
            {"id": "P1", "score": 100},
            {"id": "P2", "score": 30},
            {"id": "P3", "score": 40},
            {"id": "P4", "score": 50},
            {"id": "P5", "score": 60},
            {"id": "P6", "score": 70},
        ],
        "expected": {
            "selected_ids": ["P1", "P6", "P5"],
            "average_score": 58.333333333333336,
        },
    },
    {
        "id": "case_05",
        "brief": "Select the top 3 items by score and compute the average score.",
        "items": [
            {"id": "R1", "score": 12},
            {"id": "R2", "score": 14},
            {"id": "R3", "score": 16},
            {"id": "R4", "score": 18},
            {"id": "R5", "score": 20},
            {"id": "R6", "score": 22},
        ],
        "expected": {
            "selected_ids": ["R6", "R5", "R4"],
            "average_score": 17.0,
        },
    },
]

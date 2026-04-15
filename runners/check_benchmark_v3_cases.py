from benchmark_v3.cases import CASES

for case in CASES:
    print(case["id"])
    print(" expected_top3:", case["expected"]["selected_ids"])
    print(" expected_avg :", case["expected"]["average_score"])
    print("-" * 60)

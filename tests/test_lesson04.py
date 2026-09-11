from incident.core import Context, Run
from incident.evaluate import CASES, evaluate, grade, judge_agreement


async def test_repeated_trials_and_holdout():
    result = await evaluate(trials=2, split="held_out")
    assert len(result["rows"]) == 4
    assert result["success_rate"] == 1
    assert all(r["split"] == "held_out" for r in result["rows"])


def test_grader_rejects_plausible_but_wrong_answer():
    run = Run(Context(), [], status="completed", answer={"cause": "clock_skew",
        "status": "complete", "evidence": ["log-acme-001"]})
    assert not grade(run, CASES[0])["outcome"]
    assert judge_agreement([True, False], [True, True])["review_indices"] == [1]


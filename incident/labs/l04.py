from incident.evaluate import evaluate, judge_agreement


async def demo():
    result = await evaluate(trials=2)
    assert result["success_rate"] == 1
    return {k: v for k, v in result.items() if k != "rows"} | {
        "calibration": judge_agreement([True, False, True], [True, True, True]),
        "interpretation": "Offline fixture results validate wiring and checks, not live model quality."}


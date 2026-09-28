from app.services.scoring import evaluate

STEPS = [
    {"action": "a", "points": 10},
    {"action": "b", "points": 10},
    {"action": "c", "points": 20},
]


def test_perfect_run():
    result = evaluate(STEPS, ["a", "b", "c"])
    assert result["score"] == 40
    assert result["max_score"] == 40
    assert result["errors"] == []


def test_out_of_order_and_missing():
    result = evaluate(STEPS, ["b", "a", "c"])
    types = [e["type"] for e in result["errors"]]
    assert "out_of_order" in types
    assert "missing" in types


def test_wrong_action():
    result = evaluate(STEPS, ["a", "x", "b", "c"])
    assert result["score"] == 40
    assert result["errors"] == [{"type": "wrong_action", "action": "x"}]


def test_empty_run():
    result = evaluate(STEPS, [])
    assert result["score"] == 0
    assert len(result["errors"]) == 3

def evaluate(steps, performed):
    expected = [s["action"] for s in steps]
    points = {s["action"]: s["points"] for s in steps}
    max_score = sum(points.values())

    score = 0
    errors = []
    pointer = 0
    completed = set()

    for action in performed:
        if pointer < len(expected) and action == expected[pointer]:
            score += points[action]
            completed.add(action)
            pointer += 1
        elif action in points and action not in completed:
            errors.append({"type": "out_of_order", "action": action})
        elif action in completed:
            errors.append({"type": "repeated", "action": action})
        else:
            errors.append({"type": "wrong_action", "action": action})

    for action in expected:
        if action not in completed:
            errors.append({"type": "missing", "action": action})

    return {"score": score, "max_score": max_score, "errors": errors}

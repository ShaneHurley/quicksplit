"""Learning-step helpers: short-term miss requeue (~10–20 min, scales with set)."""

from __future__ import annotations

import json
from typing import List


def scaled_requeue_minutes(set_size: int) -> int:
    """
    Miss reappear gap in minutes.

    Formula from blueprint: clamp(10 + 0.15 * N, 8, 25).
    """
    raw = 10.0 + 0.15 * max(0, set_size)
    return int(max(8, min(25, round(raw))))


def build_learning_steps_minutes(
    set_size: int, base_steps_json: str = "[1,10,1440]"
) -> List[float]:
    """
    Return learning steps in minutes with the mid-step replaced by set-size scaling.

    Default ladder: 1 min → scaled (~10–20) → 1440 min (1 day) then graduate to FSRS.
    """
    try:
        steps = [float(x) for x in json.loads(base_steps_json)]
    except (json.JSONDecodeError, TypeError, ValueError):
        steps = [1.0, 10.0, 1440.0]

    if len(steps) < 2:
        steps = [1.0, float(scaled_requeue_minutes(set_size)), 1440.0]
    else:
        # Replace the second step with the scaled gap.
        steps = list(steps)
        steps[1] = float(scaled_requeue_minutes(set_size))
    return steps


def relearning_steps_minutes(set_size: int) -> List[float]:
    """After a lapse from review, one scaled micro-interval before returning."""
    return [float(scaled_requeue_minutes(set_size))]

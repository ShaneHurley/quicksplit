"""
FSRS-inspired scheduling engine (Difficulty / Stability / Retrievability).

Weights follow the published FSRS-5 spirit (open-spaced-repetition). Values are
named constants so they can later be personalized per profile without schema changes.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Literal, Optional

from app.services.learning_steps import (
    build_learning_steps_minutes,
    relearning_steps_minutes,
)

Grade = Literal[1, 2, 3, 4]  # Again, Hard, Good, Easy

# FSRS forgetting-curve constants — R(S, S) ~= 0.9 when W20 = 0.5
FACTOR = 19.0 / 81.0
W20 = 0.5

# Simplified FSRS-5-style weights (subset used by this MVP engine)
W = (
    0.40255,  # 0  initial stability Again
    1.18385,  # 1  initial stability Hard
    3.173,    # 2  initial stability Good
    15.69105, # 3  initial stability Easy
    7.1949,   # 4  initial difficulty
    0.5345,   # 5  difficulty update
    1.4604,   # 6  difficulty update
    0.0046,   # 7  mean reversion
    1.54575,  # 8  stability growth
    0.1192,   # 9  stability growth
    1.01925,  # 10 stability growth
    1.9395,   # 11 lapse stability
    0.11,     # 12 lapse stability
    0.29605,  # 13 lapse stability
    2.2698,   # 14 lapse stability
    0.2315,   # 15 hard penalty
    2.836,    # 16 easy bonus
)


@dataclass
class MemoryState:
    """Pure memory snapshot — no ORM coupling."""

    state: str  # new | learning | review | relearning
    difficulty: float
    stability: float
    retrievability: float
    learning_step_index: int
    reps: int
    lapses: int
    fail_streak: int
    due_at: datetime
    last_review_at: Optional[datetime]
    last_grade: Optional[int]


@dataclass
class ReviewResult:
    """Engine output after one grade."""

    state: MemoryState
    pre_d: float
    pre_s: float
    pre_r: float
    scheduled_interval_days: float
    was_again: bool


def clamp_difficulty(d: float) -> float:
    return max(1.0, min(10.0, d))


def retrievability(t_days: float, stability: float) -> float:
    """R(t, S) forgetting curve."""
    if stability <= 0:
        return 0.0
    return (1.0 + FACTOR * (t_days / stability)) ** (-W20)


def next_interval_days(stability: float, request_retention: float = 0.9) -> float:
    """Invert R(t,S)=request_retention for t."""
    if stability <= 0:
        return 1.0 / 1440.0  # one minute in days
    return (stability / FACTOR) * (request_retention ** (-1.0 / W20) - 1.0)


def _elapsed_days(state: MemoryState, now: datetime) -> float:
    if state.last_review_at is None:
        return 0.0
    delta = now - state.last_review_at
    return max(0.0, delta.total_seconds() / 86400.0)


def _initial_stability(grade: int) -> float:
    return max(0.1, float(W[grade - 1]))


def _initial_difficulty(grade: int) -> float:
    # Higher grade → easier inherent difficulty
    d = W[4] - (grade - 1) * W[5]
    return clamp_difficulty(d)


def _next_difficulty(d: float, grade: int) -> float:
    # Mean-reverting difficulty update (FSRS-inspired)
    delta = -W[6] * (grade - 3)
    new_d = d + delta * (1 - W[7])  # simple mean reversion toward mid
    # Blend toward initial difficulty for grade
    target = _initial_difficulty(grade)
    new_d = W[7] * target + (1 - W[7]) * (d + delta)
    return clamp_difficulty(new_d)


def _next_stability_success(s: float, d: float, r: float, grade: int) -> float:
    import math

    hard_pen = W[15] if grade == 2 else 1.0
    easy_bon = W[16] if grade == 4 else 1.0
    # Stability grows more when R was low (spacing effect)
    grow = (
        math.exp(W[8])
        * (11 - d)
        * math.pow(s, -W[9])
        * (math.exp((1 - r) * W[10]) - 1)
        * hard_pen
        * easy_bon
    )
    return max(s + grow, s * 1.01 if grade >= 3 else s)


def _next_stability_fail(s: float, d: float, r: float) -> float:
    import math

    return (
        W[11]
        * math.pow(d, -W[12])
        * (math.pow(s + 1.0, W[13]) - 1.0)
        * math.exp((1 - r) * W[14])
    )


class FSRSEngine:
    """Pure pedagogical engine: MemoryState + grade → ReviewResult."""

    def review(
        self,
        state: MemoryState,
        grade: int,
        now: datetime,
        set_size: int,
        request_retention: float = 0.9,
        learning_steps_json: str = "[1,10,1440]",
    ) -> ReviewResult:
        if grade not in (1, 2, 3, 4):
            raise ValueError("grade must be 1–4")

        t_days = _elapsed_days(state, now)
        pre_s = state.stability
        pre_d = state.difficulty
        pre_r = retrievability(t_days, pre_s) if pre_s > 0 else 1.0

        learning_steps = build_learning_steps_minutes(set_size, learning_steps_json)
        was_again = grade == 1

        new = MemoryState(
            state=state.state,
            difficulty=state.difficulty,
            stability=state.stability,
            retrievability=pre_r,
            learning_step_index=state.learning_step_index,
            reps=state.reps + 1,
            lapses=state.lapses,
            fail_streak=state.fail_streak,
            due_at=state.due_at,
            last_review_at=now,
            last_grade=grade,
        )

        # --- New / Learning / Relearning path ---
        if state.state in ("new", "learning", "relearning"):
            steps = (
                relearning_steps_minutes(set_size)
                if state.state == "relearning"
                else learning_steps
            )
            if was_again:
                new.state = "relearning" if state.state == "relearning" else "learning"
                if state.state == "new":
                    new.state = "learning"
                new.learning_step_index = 0
                new.fail_streak = state.fail_streak + 1
                new.lapses = state.lapses + (1 if state.state == "review" else 0)
                new.difficulty = _next_difficulty(pre_d if pre_d else 5.0, grade)
                new.stability = max(0.1, _initial_stability(1))
                interval_min = steps[0]
                new.due_at = now + timedelta(minutes=interval_min)
                new.retrievability = 1.0
                return ReviewResult(
                    state=new,
                    pre_d=pre_d,
                    pre_s=pre_s,
                    pre_r=pre_r,
                    scheduled_interval_days=interval_min / 1440.0,
                    was_again=True,
                )

            # Pass: advance learning step or graduate
            new.fail_streak = 0
            step_i = state.learning_step_index
            if state.state == "new":
                new.state = "learning"
                step_i = 0

            if grade == 4 and step_i < len(steps) - 1:
                # Easy can skip one step
                step_i += 1

            if step_i >= len(steps) - 1 and grade >= 3:
                # Graduate into review with initial FSRS stability
                new.state = "review"
                new.learning_step_index = 0
                new.difficulty = _next_difficulty(pre_d if pre_d else _initial_difficulty(grade), grade)
                new.stability = _initial_stability(grade)
                interval_days = next_interval_days(new.stability, request_retention)
                if grade == 2:
                    interval_days *= 0.5
                if grade == 4:
                    interval_days *= 1.3
                new.due_at = now + timedelta(days=interval_days)
                new.retrievability = 1.0
                return ReviewResult(
                    state=new,
                    pre_d=pre_d,
                    pre_s=pre_s,
                    pre_r=pre_r,
                    scheduled_interval_days=interval_days,
                    was_again=False,
                )

            # Stay in learning — next micro step
            next_i = min(step_i + 1, len(steps) - 1)
            new.state = "learning" if state.state != "relearning" else "relearning"
            # If relearning and completed its single step → back to review
            if state.state == "relearning" and step_i >= len(steps) - 1:
                new.state = "review"
                new.learning_step_index = 0
                new.difficulty = _next_difficulty(pre_d, grade)
                new.stability = max(pre_s, _initial_stability(grade)) * 0.5
                interval_days = next_interval_days(new.stability, request_retention)
                new.due_at = now + timedelta(days=interval_days)
                new.retrievability = 1.0
                return ReviewResult(
                    state=new,
                    pre_d=pre_d,
                    pre_s=pre_s,
                    pre_r=pre_r,
                    scheduled_interval_days=interval_days,
                    was_again=False,
                )

            new.learning_step_index = next_i
            interval_min = steps[next_i]
            new.difficulty = _next_difficulty(pre_d if pre_d else 5.0, grade)
            new.stability = _initial_stability(grade)
            new.due_at = now + timedelta(minutes=interval_min)
            new.retrievability = 1.0
            return ReviewResult(
                state=new,
                pre_d=pre_d,
                pre_s=pre_s,
                pre_r=pre_r,
                scheduled_interval_days=interval_min / 1440.0,
                was_again=False,
            )

        # --- Review path ---
        new.difficulty = _next_difficulty(pre_d, grade)
        if was_again:
            new.lapses = state.lapses + 1
            new.fail_streak = state.fail_streak + 1
            new.state = "relearning"
            new.learning_step_index = 0
            new.stability = max(0.1, _next_stability_fail(pre_s, new.difficulty, pre_r))
            steps = relearning_steps_minutes(set_size)
            interval_min = steps[0]
            new.due_at = now + timedelta(minutes=interval_min)
            new.retrievability = 1.0
            return ReviewResult(
                state=new,
                pre_d=pre_d,
                pre_s=pre_s,
                pre_r=pre_r,
                scheduled_interval_days=interval_min / 1440.0,
                was_again=True,
            )

        new.fail_streak = 0
        new.state = "review"
        new.stability = _next_stability_success(pre_s, new.difficulty, pre_r, grade)
        interval_days = next_interval_days(new.stability, request_retention)
        if grade == 2:
            interval_days = max(interval_days * W[15], 1.0 / 1440.0)
        if grade == 4:
            interval_days *= 1.3
        new.due_at = now + timedelta(days=interval_days)
        new.retrievability = 1.0
        return ReviewResult(
            state=new,
            pre_d=pre_d,
            pre_s=pre_s,
            pre_r=pre_r,
            scheduled_interval_days=interval_days,
            was_again=False,
        )


def default_new_state(now: datetime) -> MemoryState:
    """Fresh card performance defaults."""
    return MemoryState(
        state="new",
        difficulty=5.0,
        stability=0.0,
        retrievability=1.0,
        learning_step_index=0,
        reps=0,
        lapses=0,
        fail_streak=0,
        due_at=now,
        last_review_at=None,
        last_grade=None,
    )

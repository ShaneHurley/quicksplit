"""Quick unit checks for learning-step scaling."""

from app.services.learning_steps import scaled_requeue_minutes


def test_scaled_gap_clamped():
    assert scaled_requeue_minutes(0) == 10
    assert scaled_requeue_minutes(20) == 13
    assert scaled_requeue_minutes(67) == 20
    assert scaled_requeue_minutes(500) == 25

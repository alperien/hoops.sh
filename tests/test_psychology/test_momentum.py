"""Tests for momentum system."""

from __future__ import annotations

from hoops_sim.psychology.momentum import MomentumTracker


class TestMomentum:
    def test_initial_neutral(self):
        m = MomentumTracker()
        assert m.value == 0.0

    def test_home_score_shifts_positive(self):
        m = MomentumTracker()
        m.on_home_score(3)
        assert m.value > 0

    def test_away_score_shifts_negative(self):
        m = MomentumTracker()
        m.on_away_score(2)
        assert m.value < 0

    def test_consecutive_scores_build_momentum(self):
        m = MomentumTracker()
        m.on_home_score(2)
        v1 = m.value
        m.on_home_score(2)
        assert m.value > v1  # Even more momentum

    def test_timeout_resets(self):
        m = MomentumTracker()
        m.on_away_score(3)
        m.on_away_score(3)
        m.on_away_score(3)
        before = abs(m.value)
        m.on_timeout()
        after = abs(m.value)
        assert after < before  # Timeout reduces momentum magnitude

    def test_clamped_to_range(self):
        m = MomentumTracker()
        for _ in range(20):
            m.on_home_score(3)
        assert m.value <= 5.0

    def test_decay(self):
        m = MomentumTracker()
        m.on_home_score(3)
        m.on_home_score(3)
        v = m.value
        m.decay()
        assert abs(m.value) < abs(v)

    def test_modifiers(self):
        m = MomentumTracker()
        m.on_home_score(3)
        m.on_home_score(3)
        assert m.home_modifier() > 1.0
        assert m.away_modifier() < 1.0

    def test_steal_and_block(self):
        m = MomentumTracker()
        m.on_steal(is_home_stealer=True)
        assert m.value > 0
        m.on_block(is_home_blocker=False)
        # Away block reduces home momentum
        assert m.value < 0.5

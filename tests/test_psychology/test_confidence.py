"""Tests for confidence tracker."""

from __future__ import annotations

import pytest

from hoops_sim.psychology.confidence import ConfidenceTracker


class TestConfidence:
    def test_default_neutral(self):
        ct = ConfidenceTracker()
        assert ct.get(1) == 0.0

    def test_made_shot_boosts(self):
        ct = ConfidenceTracker()
        ct.on_made_shot(1)
        assert ct.get(1) > 0

    def test_missed_shot_decreases(self):
        ct = ConfidenceTracker()
        ct.on_missed_shot(1)
        assert ct.get(1) < 0

    def test_three_pointer_bigger_boost(self):
        ct = ConfidenceTracker()
        ct.on_made_shot(1, was_three=True)
        three_conf = ct.get(1)

        ct2 = ConfidenceTracker()
        ct2.on_made_shot(1, was_three=False)
        two_conf = ct2.get(1)

        assert three_conf > two_conf

    def test_clamped(self):
        ct = ConfidenceTracker()
        for _ in range(50):
            ct.on_made_shot(1, was_three=True)
        assert ct.get(1) <= 0.3

        for _ in range(100):
            ct.on_turnover(1)
        assert ct.get(1) >= -0.3

    def test_shooting_modifier(self):
        ct = ConfidenceTracker()
        ct.on_made_shot(1)
        ct.on_made_shot(1)
        assert ct.shooting_modifier(1) > 1.0

        ct.player_confidence[2] = -0.2
        assert ct.shooting_modifier(2) < 1.0

    def test_decay(self):
        ct = ConfidenceTracker()
        ct.on_made_shot(1)
        ct.on_made_shot(1)
        v = ct.get(1)
        ct.decay_all()
        assert abs(ct.get(1)) < abs(v)

    def test_independent_players(self):
        ct = ConfidenceTracker()
        ct.on_made_shot(1)
        ct.on_turnover(2)
        assert ct.get(1) > 0
        assert ct.get(2) < 0

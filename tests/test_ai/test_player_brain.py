"""Tests for player brain AI."""

from __future__ import annotations

from hoops_sim.ai.player_brain import evaluate_ball_handler_options
from hoops_sim.utils.rng import SeededRNG


class TestPlayerBrain:
    def test_shoots_when_open(self):
        result = evaluate_ball_handler_options(
            shot_quality=0.9, drive_quality=0.3,
            pass_qualities=[(2, 0.3), (3, 0.4)],
            post_quality=0.1,
            shot_volume_tendency=0.8, drive_tendency=0.3,
            pass_first_tendency=0.2, post_up_tendency=0.1,
            shot_clock_pct=0.3, confidence=0.15,
            basketball_iq=90, rng=SeededRNG(42),
        )
        assert result.action == "shoot"

    def test_passes_when_teammate_open(self):
        result = evaluate_ball_handler_options(
            shot_quality=0.2, drive_quality=0.2,
            pass_qualities=[(2, 0.9), (3, 0.3)],
            post_quality=0.1,
            shot_volume_tendency=0.3, drive_tendency=0.3,
            pass_first_tendency=0.9, post_up_tendency=0.1,
            shot_clock_pct=0.7, confidence=0.0,
            basketball_iq=90, rng=SeededRNG(42),
        )
        assert result.action == "pass"

    def test_drives_with_open_lane(self):
        result = evaluate_ball_handler_options(
            shot_quality=0.2, drive_quality=0.95,
            pass_qualities=[(2, 0.2)],
            post_quality=0.1,
            shot_volume_tendency=0.2, drive_tendency=0.9,
            pass_first_tendency=0.2, post_up_tendency=0.1,
            shot_clock_pct=0.3, confidence=0.0,
            basketball_iq=90, rng=SeededRNG(42),
        )
        assert result.action == "drive"

    def test_shot_clock_urgency(self):
        # With shot clock expiring, should shoot or drive
        result = evaluate_ball_handler_options(
            shot_quality=0.5, drive_quality=0.4,
            pass_qualities=[(2, 0.3)],
            post_quality=0.1,
            shot_volume_tendency=0.5, drive_tendency=0.5,
            pass_first_tendency=0.5, post_up_tendency=0.2,
            shot_clock_pct=0.05,  # Almost expired
            confidence=0.0,
            basketball_iq=75, rng=SeededRNG(42),
        )
        assert result.action in ("shoot", "drive")

    def test_low_iq_more_noise(self):
        # Run many times: low IQ should produce more varied results
        actions_low_iq = set()
        actions_high_iq = set()
        for seed in range(50):
            r = evaluate_ball_handler_options(
                shot_quality=0.5, drive_quality=0.5,
                pass_qualities=[(2, 0.5)],
                post_quality=0.3,
                shot_volume_tendency=0.5, drive_tendency=0.5,
                pass_first_tendency=0.5, post_up_tendency=0.3,
                shot_clock_pct=0.5, confidence=0.0,
                basketball_iq=20, rng=SeededRNG(seed),
            )
            actions_low_iq.add(r.action)

            r2 = evaluate_ball_handler_options(
                shot_quality=0.5, drive_quality=0.5,
                pass_qualities=[(2, 0.5)],
                post_quality=0.3,
                shot_volume_tendency=0.5, drive_tendency=0.5,
                pass_first_tendency=0.5, post_up_tendency=0.3,
                shot_clock_pct=0.5, confidence=0.0,
                basketball_iq=99, rng=SeededRNG(seed),
            )
            actions_high_iq.add(r2.action)

        # Low IQ should have more variety in choices
        assert len(actions_low_iq) >= len(actions_high_iq)

    def test_deterministic(self):
        r1 = evaluate_ball_handler_options(
            shot_quality=0.6, drive_quality=0.4,
            pass_qualities=[(2, 0.5)], post_quality=0.2,
            shot_volume_tendency=0.5, drive_tendency=0.5,
            pass_first_tendency=0.5, post_up_tendency=0.2,
            shot_clock_pct=0.5, confidence=0.0,
            basketball_iq=80, rng=SeededRNG(42),
        )
        r2 = evaluate_ball_handler_options(
            shot_quality=0.6, drive_quality=0.4,
            pass_qualities=[(2, 0.5)], post_quality=0.2,
            shot_volume_tendency=0.5, drive_tendency=0.5,
            pass_first_tendency=0.5, post_up_tendency=0.2,
            shot_clock_pct=0.5, confidence=0.0,
            basketball_iq=80, rng=SeededRNG(42),
        )
        assert r1.action == r2.action

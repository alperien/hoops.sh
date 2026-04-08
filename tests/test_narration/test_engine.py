"""Tests for narration engine."""

from __future__ import annotations

import pytest

from hoops_sim.narration.engine import NarrationEngine, NarrationIntensity
from hoops_sim.utils.rng import SeededRNG


class TestNarrationEngine:
    def test_made_shot(self):
        engine = NarrationEngine(SeededRNG(42))
        event = engine.narrate_made_shot(
            shooter="Curry", team="Warriors", points=3,
            distance=24.0, zone="Three Top Key", lead=5,
        )
        assert len(event.text) > 0
        assert event.intensity in (NarrationIntensity.MEDIUM, NarrationIntensity.HIGH)

    def test_dunk_is_high_intensity(self):
        engine = NarrationEngine(SeededRNG(42))
        event = engine.narrate_made_shot(
            shooter="LeBron", team="Lakers", points=2,
            distance=3.0, zone="Restricted", lead=2,
            is_dunk=True,
        )
        assert event.intensity == NarrationIntensity.HIGH
        assert "LeBron" in event.text

    def test_and_one(self):
        engine = NarrationEngine(SeededRNG(42))
        event = engine.narrate_made_shot(
            shooter="Butler", team="Heat", points=2,
            distance=5.0, zone="Close", lead=1,
            is_and_one=True,
        )
        assert "AND ONE" in event.text

    def test_missed_shot(self):
        engine = NarrationEngine(SeededRNG(42))
        event = engine.narrate_missed_shot(
            shooter="Westbrook", distance=18.0, zone="Mid Range",
            rebounder="Davis",
        )
        assert len(event.text) > 0

    def test_turnover(self):
        engine = NarrationEngine(SeededRNG(42))
        event = engine.narrate_turnover(player="Harden", team="76ers")
        assert len(event.text) > 0

    def test_steal_turnover(self):
        engine = NarrationEngine(SeededRNG(42))
        event = engine.narrate_turnover(
            player="", passer="Harden", stealer="Butler", team="76ers",
        )
        assert len(event.text) > 0

    def test_block(self):
        engine = NarrationEngine(SeededRNG(42))
        event = engine.narrate_block(blocker="Gobert", shooter="Tatum")
        assert "Gobert" in event.text
        assert event.intensity == NarrationIntensity.HIGH

    def test_free_throw(self):
        engine = NarrationEngine(SeededRNG(42))
        made = engine.narrate_free_throw("Giannis", made=True)
        assert "good" in made.text
        missed = engine.narrate_free_throw("Giannis", made=False)
        assert "no good" in missed.text

    def test_quarter_end(self):
        engine = NarrationEngine(SeededRNG(42))
        event = engine.narrate_quarter_end(
            quarter=2, home_team="Lakers", away_team="Celtics",
            home_score=55, away_score=52,
        )
        assert len(event.text) > 0

    def test_timeout(self):
        engine = NarrationEngine(SeededRNG(42))
        event = engine.narrate_timeout(team="Nuggets", remaining=5)
        assert "Nuggets" in event.text

    def test_deterministic(self):
        e1 = NarrationEngine(SeededRNG(42))
        e2 = NarrationEngine(SeededRNG(42))
        t1 = e1.narrate_made_shot("Curry", "Warriors", 3, 24.0, "Top Key", 5)
        t2 = e2.narrate_made_shot("Curry", "Warriors", 3, 24.0, "Top Key", 5)
        assert t1.text == t2.text

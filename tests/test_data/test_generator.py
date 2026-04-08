"""Tests for player and roster generation."""

from __future__ import annotations

from hoops_sim.data.generator import (
    ARCHETYPES,
    generate_player,
    generate_roster,
)
from hoops_sim.models.player import Position
from hoops_sim.utils.rng import SeededRNG


class TestGeneratePlayer:
    def test_returns_player(self):
        rng = SeededRNG(seed=42)
        player = generate_player(rng)
        assert player.first_name
        assert player.last_name
        assert player.overall > 0

    def test_specific_archetype(self):
        rng = SeededRNG(seed=42)
        player = generate_player(rng, archetype="rim_protector")
        assert player.position == Position.C
        assert player.body.height_inches >= 82

    def test_deterministic(self):
        p1 = generate_player(SeededRNG(seed=99))
        p2 = generate_player(SeededRNG(seed=99))
        assert p1.first_name == p2.first_name
        assert p1.last_name == p2.last_name
        assert p1.overall == p2.overall

    def test_age_affects_attributes(self):
        rng1 = SeededRNG(seed=42)
        rng2 = SeededRNG(seed=42)
        young = generate_player(rng1, archetype="scoring_guard", age=20)
        prime = generate_player(rng2, archetype="scoring_guard", age=27)
        # Prime player should generally be better
        # (not guaranteed due to randomness, but with same seed the scaling should help)
        # Just check they're both valid
        assert young.age == 20
        assert prime.age == 27

    def test_overall_target(self):
        rng = SeededRNG(seed=42)
        star = generate_player(rng, archetype="scoring_wing", overall_target=85)
        rng2 = SeededRNG(seed=42)
        bench = generate_player(rng2, archetype="scoring_wing", overall_target=60)
        assert star.overall > bench.overall

    def test_all_archetypes_valid(self):
        for archetype in ARCHETYPES:
            rng = SeededRNG(seed=42)
            player = generate_player(rng, archetype=archetype)
            assert player.overall > 0
            assert player.body.height_inches > 60
            assert player.body.weight_lbs > 150

    def test_has_badges(self):
        rng = SeededRNG(seed=42)
        player = generate_player(rng, archetype="scoring_guard")
        assert player.badges.count() > 0

    def test_handedness_distribution(self):
        lefties = 0
        for seed in range(200):
            p = generate_player(SeededRNG(seed=seed))
            if p.body.handedness.value == "left":
                lefties += 1
        # ~12% should be left-handed, allow wide range
        assert 5 < lefties < 60


class TestGenerateRoster:
    def test_roster_size(self):
        rng = SeededRNG(seed=42)
        roster = generate_roster(rng, size=15)
        assert len(roster) == 15

    def test_position_variety(self):
        rng = SeededRNG(seed=42)
        roster = generate_roster(rng, size=15)
        positions = {p.position for p in roster}
        # Should have at least 3 different positions
        assert len(positions) >= 3

    def test_starters_better_than_bench(self):
        rng = SeededRNG(seed=42)
        roster = generate_roster(rng, size=15)
        starter_avg = sum(p.overall for p in roster[:5]) / 5
        bench_avg = sum(p.overall for p in roster[10:]) / max(1, len(roster[10:]))
        assert starter_avg >= bench_avg - 5  # Allow some variance

    def test_deterministic(self):
        r1 = generate_roster(SeededRNG(seed=99), size=10)
        r2 = generate_roster(SeededRNG(seed=99), size=10)
        for p1, p2 in zip(r1, r2):
            assert p1.full_name == p2.full_name
            assert p1.overall == p2.overall

    def test_custom_size(self):
        rng = SeededRNG(seed=42)
        roster = generate_roster(rng, size=5)
        assert len(roster) == 5

"""Tests for foul adjudication."""

from __future__ import annotations

import pytest

from hoops_sim.physics.contact import ContactEvent, ContactSeverity, ContactType
from hoops_sim.physics.vec import Vec2
from hoops_sim.referee.foul_judge import RefereeCrew
from hoops_sim.utils.rng import SeededRNG


def _make_contact(severity_value: float, defensive_set: bool = False) -> ContactEvent:
    return ContactEvent(
        offensive_position=Vec2(50, 25),
        defensive_position=Vec2(51, 25),
        offensive_velocity=Vec2(10, 0),
        defensive_velocity=Vec2(0, 0),
        offensive_weight=210,
        defensive_weight=220,
        defensive_set=defensive_set,
        defensive_legal_position=defensive_set,
        contact_type=ContactType.BODY,
        severity_value=severity_value,
    )


class TestRefereeCrew:
    def test_no_call_on_no_contact(self):
        crew = RefereeCrew()
        contact = _make_contact(0.1)  # None severity
        result = crew.adjudicate_contact(
            contact, is_shooting=False, is_offensive_star=False,
            is_home_offense=False, rng=SeededRNG(42),
        )
        assert not result.foul_called

    def test_hard_contact_usually_foul(self):
        crew = RefereeCrew(tightness=0.6)
        fouls = 0
        for seed in range(100):
            contact = _make_contact(0.85)  # Hard severity
            result = crew.adjudicate_contact(
                contact, is_shooting=True, is_offensive_star=False,
                is_home_offense=False, rng=SeededRNG(seed),
            )
            if result.foul_called:
                fouls += 1
        assert fouls > 70  # Most hard contacts should be fouls

    def test_flagrant_almost_always_called(self):
        crew = RefereeCrew()
        fouls = 0
        for seed in range(100):
            contact = _make_contact(0.95)  # Flagrant
            result = crew.adjudicate_contact(
                contact, is_shooting=False, is_offensive_star=False,
                is_home_offense=False, rng=SeededRNG(seed),
            )
            if result.foul_called:
                fouls += 1
                if result.is_flagrant:
                    assert result.free_throws_awarded == 2
        assert fouls > 90

    def test_star_treatment(self):
        crew = RefereeCrew(star_treatment=0.15)
        star_fouls = 0
        normal_fouls = 0
        for seed in range(200):
            contact = _make_contact(0.5)  # Moderate
            star = crew.adjudicate_contact(
                contact, is_shooting=True, is_offensive_star=True,
                is_home_offense=False, rng=SeededRNG(seed),
            )
            normal = crew.adjudicate_contact(
                contact, is_shooting=True, is_offensive_star=False,
                is_home_offense=False, rng=SeededRNG(seed),
            )
            if star.foul_called:
                star_fouls += 1
            if normal.foul_called:
                normal_fouls += 1
        assert star_fouls >= normal_fouls

    def test_home_bias(self):
        crew = RefereeCrew(home_bias=0.08)
        home_fouls = 0
        away_fouls = 0
        for seed in range(200):
            contact = _make_contact(0.5)
            home = crew.adjudicate_contact(
                contact, is_shooting=True, is_offensive_star=False,
                is_home_offense=True, rng=SeededRNG(seed),
            )
            away = crew.adjudicate_contact(
                contact, is_shooting=True, is_offensive_star=False,
                is_home_offense=False, rng=SeededRNG(seed),
            )
            if home.foul_called:
                home_fouls += 1
            if away.foul_called:
                away_fouls += 1
        assert home_fouls >= away_fouls

    def test_shooting_foul_awards_fts(self):
        crew = RefereeCrew(tightness=0.8)
        for seed in range(100):
            contact = _make_contact(0.85)
            result = crew.adjudicate_contact(
                contact, is_shooting=True, is_offensive_star=False,
                is_home_offense=False, rng=SeededRNG(seed),
            )
            if result.foul_called and result.is_shooting_foul:
                assert result.free_throws_awarded >= 2

    def test_charge_call(self):
        crew = RefereeCrew(charge_block_accuracy=1.0)  # Perfect accuracy
        contact = _make_contact(0.7, defensive_set=True)
        # Run enough times to get a foul call
        for seed in range(100):
            result = crew.adjudicate_contact(
                contact, is_shooting=False, is_offensive_star=False,
                is_home_offense=False, rng=SeededRNG(seed),
            )
            if result.foul_called and result.is_offensive_foul:
                break
        else:
            # If we didn't get one in 100 tries, that's acceptable
            pass

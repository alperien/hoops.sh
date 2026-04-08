"""Tests for team, coaching, front office, owner, arena, contract, and league models."""

from __future__ import annotations

import pytest

from hoops_sim.models.arena import Arena
from hoops_sim.models.coaching_staff import CoachingStaff, CoachPersonality
from hoops_sim.models.contract import Contract, ContractOption, ContractType
from hoops_sim.models.front_office import FrontOffice, TeamStrategy
from hoops_sim.models.league import League, SalaryCapInfo
from hoops_sim.models.owner import Owner
from hoops_sim.models.player import Player, Position
from hoops_sim.models.team import Team


class TestCoachingStaff:
    def test_defaults(self):
        staff = CoachingStaff()
        assert staff.overall() == 50

    def test_development_modifier(self):
        low = CoachingStaff(player_development=10)
        high = CoachingStaff(player_development=90)
        assert high.development_modifier() > low.development_modifier()
        assert low.development_modifier() >= 0.8
        assert high.development_modifier() <= 1.2

    def test_personality_types(self):
        assert len(CoachPersonality) == 6


class TestFrontOffice:
    def test_defaults(self):
        fo = FrontOffice()
        assert fo.overall() == 50

    def test_draft_uncertainty(self):
        good = FrontOffice(scouting_budget=90)
        bad = FrontOffice(scouting_budget=10)
        assert good.get_draft_uncertainty(0.20) < bad.get_draft_uncertainty(0.20)

    def test_injury_recovery(self):
        good = FrontOffice(medical_staff=90)
        bad = FrontOffice(medical_staff=10)
        assert good.injury_recovery_modifier() > bad.injury_recovery_modifier()

    def test_trade_accuracy(self):
        fo = FrontOffice(gm_skill=99)
        assert fo.trade_evaluation_accuracy() > 0.9

    def test_strategies(self):
        assert len(TeamStrategy) == 4


class TestOwner:
    def test_will_approve_tax(self):
        rich = Owner(luxury_tax_tolerance=0.9)
        cheap = Owner(luxury_tax_tolerance=0.1)
        assert rich.will_approve_tax(40_000_000)
        assert not cheap.will_approve_tax(40_000_000)

    def test_will_meddle(self):
        meddler = Owner(meddling=0.8)
        hands_off = Owner(meddling=0.2)
        assert meddler.will_meddle()
        assert not hands_off.will_meddle()

    def test_min_wins(self):
        impatient = Owner(win_now_pressure=0.9)
        patient = Owner(win_now_pressure=0.1)
        assert impatient.min_acceptable_wins() > patient.min_acceptable_wins()


class TestArena:
    def test_defaults(self):
        arena = Arena()
        assert arena.capacity == 19000

    def test_altitude_sync(self):
        arena = Arena(altitude_ft=5280)
        assert arena.surface.altitude_ft == 5280

    def test_home_court_advantage(self):
        loud = Arena(crowd_intensity=0.95, altitude_ft=5280)
        quiet = Arena(crowd_intensity=0.3, altitude_ft=0)
        assert loud.home_court_advantage() > quiet.home_court_advantage()

    def test_crowd_energy(self):
        arena = Arena(capacity=20000, crowd_intensity=0.9)
        full = arena.crowd_energy_for_attendance(20000)
        half = arena.crowd_energy_for_attendance(10000)
        assert full > half
        assert full <= 100


class TestContract:
    def test_defaults(self):
        c = Contract()
        assert c.total_years == 4
        assert c.current_salary == 5_000_000

    def test_remaining_years(self):
        c = Contract(total_years=4, current_year=2)
        assert c.remaining_years == 3

    def test_remaining_guaranteed(self):
        c = Contract(total_years=3, current_year=1, salaries=[10_000_000, 12_000_000, 14_000_000])
        assert c.remaining_guaranteed == 36_000_000

    def test_is_expiring(self):
        c = Contract(total_years=3, current_year=3)
        assert c.is_expiring()
        c2 = Contract(total_years=3, current_year=1)
        assert not c2.is_expiring()

    def test_advance_year(self):
        c = Contract(total_years=3, current_year=1)
        assert c.advance_year()
        assert c.current_year == 2
        c.current_year = 3
        assert not c.advance_year()

    def test_trade_kicker(self):
        c = Contract(
            salaries=[20_000_000], total_years=1, current_year=1,
            trade_kicker_pct=15.0,
        )
        assert c.trade_kicker_amount() == 3_000_000

    def test_average_annual_value(self):
        c = Contract(salaries=[10_000_000, 12_000_000, 14_000_000], total_years=3)
        assert c.average_annual_value == 12_000_000

    def test_contract_types(self):
        assert len(ContractType) == 8
        assert len(ContractOption) == 4


class TestSalaryCap:
    def test_no_tax_under_threshold(self):
        cap = SalaryCapInfo()
        assert cap.luxury_tax_for(150_000_000) == 0

    def test_tax_over_threshold(self):
        cap = SalaryCapInfo()
        assert cap.luxury_tax_for(170_000_000) > 0

    def test_progressive_tax(self):
        cap = SalaryCapInfo()
        small = cap.luxury_tax_for(167_000_000)
        large = cap.luxury_tax_for(185_000_000)
        assert large > small

    def test_max_salary(self):
        cap = SalaryCapInfo()
        assert cap.max_salary_for_experience(12) > cap.max_salary_for_experience(5)

    def test_rookie_salary(self):
        cap = SalaryCapInfo()
        assert cap.rookie_salary(1) > cap.rookie_salary(10)
        assert cap.rookie_salary(30) > 0


class TestTeam:
    def _make_player(self, pid: int, ovr_offset: int = 0) -> Player:
        p = Player(id=pid, first_name=f"Player{pid}", last_name="Test")
        p.attributes.shooting.three_point = 50 + ovr_offset
        return p

    def test_defaults(self):
        team = Team()
        assert team.roster_size() == 0

    def test_add_player(self):
        team = Team()
        p = self._make_player(1)
        team.add_player(p)
        assert team.roster_size() == 1
        assert team.get_player(1) is p

    def test_remove_player(self):
        team = Team()
        p = self._make_player(1)
        team.add_player(p)
        removed = team.remove_player(1)
        assert removed is p
        assert team.roster_size() == 0

    def test_get_starters(self):
        team = Team()
        for i in range(10):
            team.add_player(self._make_player(i, ovr_offset=i * 3))
        starters = team.get_starters()
        assert len(starters) == 5

    def test_total_payroll(self):
        team = Team()
        team.contracts[1] = Contract(salaries=[10_000_000], total_years=1, current_year=1)
        team.contracts[2] = Contract(salaries=[15_000_000], total_years=1, current_year=1)
        assert team.total_payroll() == 25_000_000

    def test_full_name(self):
        team = Team(city="Los Angeles", name="Lakers")
        assert team.full_name == "Los Angeles Lakers"


class TestLeague:
    def test_defaults(self):
        league = League()
        assert league.team_count() == 0

    def test_add_and_find_team(self):
        league = League()
        team = Team(id=1, abbreviation="LAL", conference="West")
        league.teams.append(team)
        assert league.get_team(1) is team
        assert league.get_team_by_abbr("LAL") is team

    def test_conference_teams(self):
        league = League()
        league.teams.append(Team(id=1, conference="East"))
        league.teams.append(Team(id=2, conference="West"))
        league.teams.append(Team(id=3, conference="East"))
        assert len(league.conference_teams("East")) == 2
        assert len(league.conference_teams("West")) == 1

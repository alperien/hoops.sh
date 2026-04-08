"""Tests for game statistics."""

from __future__ import annotations

import pytest

from hoops_sim.models.stats import PlayerGameStats, TeamGameStats


class TestPlayerGameStats:
    def test_initial_zeros(self):
        s = PlayerGameStats()
        assert s.points == 0
        assert s.rebounds == 0
        assert s.fg_pct == 0.0

    def test_record_two(self):
        s = PlayerGameStats()
        s.record_made_shot(is_three=False)
        assert s.points == 2
        assert s.fgm == 1
        assert s.fga == 1

    def test_record_three(self):
        s = PlayerGameStats()
        s.record_made_shot(is_three=True)
        assert s.points == 3
        assert s.three_pm == 1

    def test_record_miss(self):
        s = PlayerGameStats()
        s.record_missed_shot(is_three=True)
        assert s.points == 0
        assert s.fga == 1
        assert s.three_pa == 1

    def test_fg_pct(self):
        s = PlayerGameStats()
        s.record_made_shot()
        s.record_missed_shot()
        assert s.fg_pct == pytest.approx(0.5)

    def test_free_throws(self):
        s = PlayerGameStats()
        s.record_made_ft()
        s.record_made_ft()
        s.record_missed_ft()
        assert s.points == 2
        assert s.ft_pct == pytest.approx(2 / 3)

    def test_true_shooting(self):
        s = PlayerGameStats()
        # 10 points on 5 FGA and 2 FTA
        s.fgm = 4
        s.fga = 5
        s.ftm = 2
        s.fta = 2
        s.points = 10
        assert s.ts_pct > 0.5

    def test_efg(self):
        s = PlayerGameStats()
        s.fgm = 5
        s.fga = 10
        s.three_pm = 3
        assert s.efg_pct == pytest.approx(0.65)

    def test_rebounds(self):
        s = PlayerGameStats()
        s.offensive_rebounds = 3
        s.defensive_rebounds = 7
        assert s.rebounds == 10

    def test_double_double(self):
        s = PlayerGameStats(points=20, defensive_rebounds=10)
        assert s.is_double_double()
        s2 = PlayerGameStats(points=20, defensive_rebounds=5)
        assert not s2.is_double_double()

    def test_triple_double(self):
        s = PlayerGameStats(points=15, defensive_rebounds=10, assists=12)
        assert s.is_triple_double()

    def test_stat_line(self):
        s = PlayerGameStats(points=25, defensive_rebounds=8, assists=6, steals=2)
        line = s.stat_line()
        assert "25 PTS" in line
        assert "8 REB" in line
        assert "6 AST" in line


class TestTeamGameStats:
    def test_add_player(self):
        t = TeamGameStats()
        s = t.add_player(1, "Player One")
        assert t.get_player(1) is s

    def test_totals(self):
        t = TeamGameStats()
        s1 = t.add_player(1, "P1")
        s1.record_made_shot(is_three=True)
        s1.assists = 5
        s2 = t.add_player(2, "P2")
        s2.record_made_shot()
        s2.assists = 3
        assert t.total_assists() == 8
        assert t.team_fg_pct() == pytest.approx(1.0)  # 2/2

    def test_leading_scorer(self):
        t = TeamGameStats()
        s1 = t.add_player(1, "Bench")
        s1.points = 5
        s2 = t.add_player(2, "Star")
        s2.points = 30
        assert t.leading_scorer().player_name == "Star"

    def test_empty_team(self):
        t = TeamGameStats()
        assert t.total_rebounds() == 0
        assert t.team_fg_pct() == 0.0

"""Game statistics: traditional, advanced, and tracking stats."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class PlayerGameStats:
    """Per-game statistics for a single player."""

    player_id: int = 0
    player_name: str = ""

    # Minutes
    minutes: float = 0.0

    # Traditional stats
    points: int = 0
    fgm: int = 0  # Field goals made
    fga: int = 0  # Field goals attempted
    three_pm: int = 0  # Three-pointers made
    three_pa: int = 0  # Three-pointers attempted
    ftm: int = 0  # Free throws made
    fta: int = 0  # Free throws attempted
    offensive_rebounds: int = 0
    defensive_rebounds: int = 0
    assists: int = 0
    steals: int = 0
    blocks: int = 0
    turnovers: int = 0
    personal_fouls: int = 0
    plus_minus: int = 0

    @property
    def rebounds(self) -> int:
        return self.offensive_rebounds + self.defensive_rebounds

    @property
    def fg_pct(self) -> float:
        return self.fgm / self.fga if self.fga > 0 else 0.0

    @property
    def three_pct(self) -> float:
        return self.three_pm / self.three_pa if self.three_pa > 0 else 0.0

    @property
    def ft_pct(self) -> float:
        return self.ftm / self.fta if self.fta > 0 else 0.0

    @property
    def ts_pct(self) -> float:
        """True shooting percentage."""
        tsa = self.fga + 0.44 * self.fta
        if tsa == 0:
            return 0.0
        return self.points / (2 * tsa)

    @property
    def efg_pct(self) -> float:
        """Effective field goal percentage."""
        if self.fga == 0:
            return 0.0
        return (self.fgm + 0.5 * self.three_pm) / self.fga

    def record_made_shot(self, is_three: bool = False) -> None:
        """Record a made field goal."""
        self.fgm += 1
        self.fga += 1
        if is_three:
            self.three_pm += 1
            self.three_pa += 1
            self.points += 3
        else:
            self.points += 2

    def record_missed_shot(self, is_three: bool = False) -> None:
        """Record a missed field goal."""
        self.fga += 1
        if is_three:
            self.three_pa += 1

    def record_made_ft(self) -> None:
        self.ftm += 1
        self.fta += 1
        self.points += 1

    def record_missed_ft(self) -> None:
        self.fta += 1

    def is_double_double(self) -> bool:
        """Check for a double-double (10+ in 2 categories)."""
        cats = [self.points, self.rebounds, self.assists, self.steals, self.blocks]
        return sum(1 for c in cats if c >= 10) >= 2

    def is_triple_double(self) -> bool:
        """Check for a triple-double (10+ in 3 categories)."""
        cats = [self.points, self.rebounds, self.assists, self.steals, self.blocks]
        return sum(1 for c in cats if c >= 10) >= 3

    def stat_line(self) -> str:
        """Short stat line like '25 PTS, 8 REB, 6 AST'."""
        parts = [f"{self.points} PTS"]
        if self.rebounds > 0:
            parts.append(f"{self.rebounds} REB")
        if self.assists > 0:
            parts.append(f"{self.assists} AST")
        if self.steals > 0:
            parts.append(f"{self.steals} STL")
        if self.blocks > 0:
            parts.append(f"{self.blocks} BLK")
        return ", ".join(parts)


@dataclass
class TeamGameStats:
    """Aggregate team statistics for a game."""

    team_id: int = 0
    team_name: str = ""
    player_stats: Dict[int, PlayerGameStats] = field(default_factory=dict)

    # Team totals
    points: int = 0
    fast_break_points: int = 0
    points_in_paint: int = 0
    second_chance_points: int = 0
    bench_points: int = 0
    turnovers: int = 0
    team_rebounds: int = 0

    def add_player(self, player_id: int, name: str) -> PlayerGameStats:
        """Add a player to the stats tracker."""
        stats = PlayerGameStats(player_id=player_id, player_name=name)
        self.player_stats[player_id] = stats
        return stats

    def get_player(self, player_id: int) -> PlayerGameStats:
        """Get stats for a player."""
        return self.player_stats.get(player_id, PlayerGameStats())

    def total_rebounds(self) -> int:
        return sum(p.rebounds for p in self.player_stats.values())

    def total_assists(self) -> int:
        return sum(p.assists for p in self.player_stats.values())

    def total_steals(self) -> int:
        return sum(p.steals for p in self.player_stats.values())

    def total_blocks(self) -> int:
        return sum(p.blocks for p in self.player_stats.values())

    def team_fg_pct(self) -> float:
        fgm = sum(p.fgm for p in self.player_stats.values())
        fga = sum(p.fga for p in self.player_stats.values())
        return fgm / fga if fga > 0 else 0.0

    def team_three_pct(self) -> float:
        made = sum(p.three_pm for p in self.player_stats.values())
        attempted = sum(p.three_pa for p in self.player_stats.values())
        return made / attempted if attempted > 0 else 0.0

    def leading_scorer(self) -> PlayerGameStats:
        """Get the player with the most points."""
        if not self.player_stats:
            return PlayerGameStats()
        return max(self.player_stats.values(), key=lambda p: p.points)

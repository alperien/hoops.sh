"""Team momentum system with event triggers and timeout reset."""

from __future__ import annotations

from dataclasses import dataclass

from hoops_sim.utils.math import clamp


@dataclass
class MomentumTracker:
    """Tracks team momentum on a -5 to +5 scale.

    Positive = home team has momentum, negative = away team.
    Momentum affects shooting, defensive effort, and crowd energy.
    """

    value: float = 0.0  # -5.0 to +5.0
    consecutive_home_scores: int = 0
    consecutive_away_scores: int = 0

    def on_home_score(self, points: int) -> None:
        """Home team scored."""
        self.consecutive_home_scores += 1
        self.consecutive_away_scores = 0
        boost = points * 0.3 + (self.consecutive_home_scores - 1) * 0.2
        self.value = clamp(self.value + boost, -5.0, 5.0)

    def on_away_score(self, points: int) -> None:
        """Away team scored."""
        self.consecutive_away_scores += 1
        self.consecutive_home_scores = 0
        boost = points * 0.3 + (self.consecutive_away_scores - 1) * 0.2
        self.value = clamp(self.value - boost, -5.0, 5.0)

    def on_turnover(self, is_home: bool) -> None:
        shift = -0.5 if is_home else 0.5
        self.value = clamp(self.value + shift, -5.0, 5.0)

    def on_block(self, is_home_blocker: bool) -> None:
        shift = 0.4 if is_home_blocker else -0.4
        self.value = clamp(self.value + shift, -5.0, 5.0)

    def on_steal(self, is_home_stealer: bool) -> None:
        shift = 0.5 if is_home_stealer else -0.5
        self.value = clamp(self.value + shift, -5.0, 5.0)

    def on_timeout(self) -> None:
        """Timeout resets momentum toward neutral."""
        self.value *= 0.4
        self.consecutive_home_scores = 0
        self.consecutive_away_scores = 0

    def on_dunk(self, is_home: bool) -> None:
        shift = 0.6 if is_home else -0.6
        self.value = clamp(self.value + shift, -5.0, 5.0)

    def decay(self) -> None:
        """Natural decay toward neutral each possession."""
        self.value *= 0.95

    def home_modifier(self) -> float:
        """Performance modifier for the home team. Range ~0.97 to 1.03."""
        return 1.0 + self.value * 0.006

    def away_modifier(self) -> float:
        """Performance modifier for the away team."""
        return 1.0 - self.value * 0.006

"""Coaching staff model with quality ratings per role."""

from __future__ import annotations

import enum
from dataclasses import dataclass


class CoachPersonality(enum.Enum):
    """Head coach personality archetypes."""

    AGGRESSIVE = "aggressive"  # Blitzes, traps, fast pace
    ADAPTIVE = "adaptive"  # Adjusts to opponent
    DEFENSIVE = "defensive"  # Defense-first, slow pace
    OFFENSIVE = "offensive"  # Prioritizes scoring, space-and-pace
    PLAYER_DEVELOPMENT = "player_development"  # Focuses on developing young talent
    OLD_SCHOOL = "old_school"  # Traditional, post play, half-court


@dataclass
class CoachingStaff:
    """Team coaching staff with quality ratings.

    Each rating is 1-99 and affects the corresponding aspect of the team.
    """

    # Head coach
    head_coach_name: str = "Coach"
    head_coach_personality: CoachPersonality = CoachPersonality.ADAPTIVE
    offensive_scheme: int = 50  # Quality of offensive system
    defensive_scheme: int = 50  # Quality of defensive system
    game_management: int = 50  # Timeout usage, end-of-game decisions
    player_relations: int = 50  # Ability to manage egos, get buy-in
    adjustments: int = 50  # In-game and between-game adjustments

    # Assistant coaches (aggregate ratings)
    offensive_coordinator: int = 50
    defensive_coordinator: int = 50
    player_development: int = 50  # Affects attribute growth rate
    shooting_coach: int = 50  # Affects shooting development specifically
    conditioning_coach: int = 50  # Affects stamina and injury prevention

    def overall(self) -> int:
        """Overall coaching staff rating."""
        vals = [
            self.offensive_scheme, self.defensive_scheme,
            self.game_management, self.player_relations, self.adjustments,
            self.offensive_coordinator, self.defensive_coordinator,
            self.player_development, self.shooting_coach, self.conditioning_coach,
        ]
        return round(sum(vals) / len(vals))

    def development_modifier(self) -> float:
        """Modifier for player development rate. Range: 0.8 to 1.2."""
        return 0.8 + (self.player_development / 100.0) * 0.4

    def scheme_complexity(self) -> float:
        """How complex the offensive/defensive schemes are.

        Higher complexity = better ceiling but longer to learn.
        """
        return (self.offensive_scheme + self.defensive_scheme) / 200.0

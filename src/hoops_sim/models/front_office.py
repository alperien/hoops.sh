"""Front office model: GM, scouting, analytics, development, medical."""

from __future__ import annotations

import enum
from dataclasses import dataclass


class TeamStrategy(enum.Enum):
    """Front office team-building strategy."""

    CONTENDER = "contender"
    RETOOLING = "retooling"
    REBUILDING = "rebuilding"
    TANKING = "tanking"


@dataclass
class FrontOffice:
    """Team front office with quality ratings affecting roster decisions.

    Each rating is 1-99.
    """

    gm_name: str = "GM"
    gm_skill: int = 50  # Overall GM decision-making quality
    scouting_budget: int = 50  # Affects draft prospect evaluation uncertainty
    analytics_department: int = 50  # Quality of advanced metrics usage
    development_staff: int = 50  # Affects player improvement rate
    medical_staff: int = 50  # Affects injury recovery time and prevention
    strategy: TeamStrategy = TeamStrategy.CONTENDER

    def get_draft_uncertainty(self, base_uncertainty: float) -> float:
        """Calculate draft prospect evaluation uncertainty.

        Better scouting reduces uncertainty in prospect ratings.

        Args:
            base_uncertainty: Raw prospect uncertainty (0.05-0.25).

        Returns:
            Adjusted uncertainty.
        """
        scouting_reduction = self.scouting_budget / 100.0 * 0.5
        return base_uncertainty * (1.0 - scouting_reduction)

    def trade_evaluation_accuracy(self) -> float:
        """How accurately the GM evaluates trades. Range: 0.6 to 1.0."""
        return 0.6 + (self.gm_skill / 100.0) * 0.4

    def injury_recovery_modifier(self) -> float:
        """Modifier for injury recovery speed. Range: 0.85 to 1.15."""
        return 0.85 + (self.medical_staff / 100.0) * 0.30

    def injury_prevention_modifier(self) -> float:
        """Modifier for injury risk. Range: 0.85 to 1.0 (lower = better)."""
        return 1.0 - (self.medical_staff / 100.0) * 0.15

    def overall(self) -> int:
        """Overall front office quality."""
        vals = [
            self.gm_skill, self.scouting_budget,
            self.analytics_department, self.development_staff,
            self.medical_staff,
        ]
        return round(sum(vals) / len(vals))

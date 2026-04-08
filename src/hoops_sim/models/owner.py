"""Owner model with traits that constrain front-office decisions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Owner:
    """Team owner with personality traits affecting team operations.

    All trait values range from 0.0 to 1.0.
    """

    name: str = "Owner"
    wealth: float = 0.5  # Affects willingness to spend
    patience: float = 0.5  # How long before firing GM/coach
    win_now_pressure: float = 0.5  # Demands immediate results vs accepts rebuild
    luxury_tax_tolerance: float = 0.5  # Willingness to pay tax for contender
    meddling: float = 0.2  # Overrides GM decisions (bad)
    market_awareness: float = 0.5  # Cares about attendance and PR
    analytics_embrace: float = 0.5  # Supports analytics-driven decisions

    def will_approve_tax(self, tax_amount: int) -> bool:
        """Check if owner will approve going into the luxury tax.

        Args:
            tax_amount: Projected luxury tax bill in dollars.
        """
        threshold = self.luxury_tax_tolerance * 60_000_000
        return tax_amount <= threshold

    def will_meddle(self) -> bool:
        """Check if owner is likely to override GM decisions."""
        return self.meddling > 0.7

    def min_acceptable_wins(self) -> int:
        """Minimum wins before the owner considers firing staff."""
        if self.win_now_pressure > 0.8:
            return 45
        if self.win_now_pressure > 0.5:
            return 35
        if self.win_now_pressure > 0.3:
            return 25
        return 15  # Very patient owner

    def spending_willingness(self) -> float:
        """Overall willingness to spend on the team. 0-1 scale."""
        return (self.wealth * 0.5 + self.win_now_pressure * 0.3
                + self.luxury_tax_tolerance * 0.2)

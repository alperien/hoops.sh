"""Foul adjudication with ref tendencies, star treatment, and home bias."""

from __future__ import annotations

from dataclasses import dataclass

from hoops_sim.physics.contact import ContactEvent, ContactSeverity
from hoops_sim.utils.rng import SeededRNG


@dataclass
class FoulDecision:
    """Result of foul adjudication."""

    foul_called: bool
    is_offensive_foul: bool = False
    is_shooting_foul: bool = False
    is_flagrant: bool = False
    is_technical: bool = False
    free_throws_awarded: int = 0


@dataclass
class RefereeCrew:
    """Referee crew with tendencies that affect foul calling."""

    tightness: float = 0.5  # 0=lenient, 1=tight whistle
    home_bias: float = 0.05  # Slight home advantage in calls
    star_treatment: float = 0.1  # Stars get more calls
    consistency: float = 0.7  # How consistent the calls are
    moving_screen_detection: float = 0.3  # How often moving screens are called
    charge_block_accuracy: float = 0.7  # Accuracy on charge/block calls

    def adjudicate_contact(
        self,
        contact: ContactEvent,
        is_shooting: bool,
        is_offensive_star: bool,
        is_home_offense: bool,
        rng: SeededRNG,
    ) -> FoulDecision:
        """Decide whether a foul should be called on a contact event.

        Args:
            contact: The contact event to adjudicate.
            is_shooting: Whether the offensive player was in a shooting motion.
            is_offensive_star: Whether the offensive player is a star (high OVR).
            is_home_offense: Whether the offensive team is the home team.
            rng: Random number generator.

        Returns:
            FoulDecision with the call.
        """
        severity = contact.severity

        # No-call threshold based on ref tightness
        if severity == ContactSeverity.NONE:
            return FoulDecision(foul_called=False)

        if severity == ContactSeverity.INCIDENTAL:
            # Rarely called
            call_prob = self.tightness * 0.1
            if rng.random() > call_prob:
                return FoulDecision(foul_called=False)

        # Base call probability from severity
        base_prob = {
            ContactSeverity.INCIDENTAL: 0.05,
            ContactSeverity.LIGHT: 0.15,
            ContactSeverity.MODERATE: 0.50,
            ContactSeverity.HARD: 0.85,
            ContactSeverity.FLAGRANT: 0.98,
        }.get(severity, 0.0)

        # Adjust for ref tendencies
        base_prob *= (0.5 + self.tightness)  # Tight refs call more

        # Star treatment
        if is_offensive_star:
            base_prob += self.star_treatment

        # Home bias
        if is_home_offense:
            base_prob += self.home_bias

        # Consistency noise
        noise = (1.0 - self.consistency) * 0.15
        base_prob += rng.gauss(0, noise)

        base_prob = max(0.0, min(1.0, base_prob))

        if rng.random() > base_prob:
            return FoulDecision(foul_called=False)

        # Foul is called -- determine type
        # Charge vs block
        if contact.defensive_set and contact.defensive_legal_position:
            if rng.random() < self.charge_block_accuracy:
                return FoulDecision(foul_called=True, is_offensive_foul=True)

        # Flagrant check
        if severity == ContactSeverity.FLAGRANT:
            return FoulDecision(
                foul_called=True,
                is_shooting_foul=is_shooting,
                is_flagrant=True,
                free_throws_awarded=2,
            )

        # Regular foul
        fts = 0
        if is_shooting:
            fts = 2  # Default; 3 if behind the arc (caller determines)

        return FoulDecision(
            foul_called=True,
            is_shooting_foul=is_shooting,
            free_throws_awarded=fts,
        )

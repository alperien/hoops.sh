"""Utility-based player AI for ball handler decisions.

The player brain evaluates all possible actions (shoot, drive, pass, post, hold)
and picks the highest utility option, with noise based on basketball IQ.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from hoops_sim.utils.rng import SeededRNG


@dataclass
class ActionOption:
    """A possible action the ball handler can take."""

    action: str  # "shoot", "drive", "pass", "post_up", "hold"
    utility: float  # Evaluated utility (higher = better)
    target_id: Optional[int] = None  # For passes: teammate ID
    quality: float = 0.0  # Quality of the opportunity (0-1)


def evaluate_ball_handler_options(
    shot_quality: float,
    drive_quality: float,
    pass_qualities: List[Tuple[int, float]],  # (teammate_id, quality)
    post_quality: float,
    shot_volume_tendency: float,
    drive_tendency: float,
    pass_first_tendency: float,
    post_up_tendency: float,
    shot_clock_pct: float,
    confidence: float,
    basketball_iq: int,
    rng: SeededRNG,
) -> ActionOption:
    """Evaluate all options and pick the best action.

    Args:
        shot_quality: How good the shot opportunity is (0-1).
        drive_quality: How open the driving lane is (0-1).
        pass_qualities: List of (teammate_id, opportunity_quality) pairs.
        post_quality: How favorable a post-up would be (0-1).
        shot_volume_tendency: Player's shot volume tendency (0-1).
        drive_tendency: Player's drive tendency (0-1).
        pass_first_tendency: Player's pass-first tendency (0-1).
        post_up_tendency: Player's post-up tendency (0-1).
        shot_clock_pct: Shot clock remaining as percentage (0-1, 0=expired).
        confidence: Player's current confidence modifier.
        basketball_iq: Player's basketball IQ (0-99).
        rng: Random number generator.

    Returns:
        The best ActionOption.
    """
    options: List[ActionOption] = []

    # Shot clock urgency (increases as clock runs down)
    urgency = max(0.0, 1.0 - shot_clock_pct * 2.5)

    # Option: Shoot
    shoot_utility = (
        shot_quality * 0.40
        + shot_volume_tendency * 0.15
        + confidence * 0.10
        + urgency * 0.15
    )
    options.append(ActionOption("shoot", shoot_utility, quality=shot_quality))

    # Option: Drive
    drive_utility = (
        drive_quality * 0.35
        + drive_tendency * 0.15
        + urgency * 0.15
    )
    options.append(ActionOption("drive", drive_utility, quality=drive_quality))

    # Option: Pass to each teammate
    for teammate_id, pass_quality in pass_qualities:
        pass_utility = (
            pass_quality * 0.30
            + pass_first_tendency * 0.15
            + (1.0 - urgency) * 0.10  # More patience = more passing
        )
        options.append(ActionOption("pass", pass_utility, target_id=teammate_id, quality=pass_quality))

    # Option: Post up
    if post_quality > 0.2:
        post_utility = (
            post_quality * 0.40
            + post_up_tendency * 0.20
            + urgency * 0.10
        )
        options.append(ActionOption("post_up", post_utility, quality=post_quality))

    # Option: Hold (wait for play to develop)
    hold_utility = 0.25 + (1.0 - urgency) * 0.25
    options.append(ActionOption("hold", hold_utility))

    # Add noise based on basketball IQ (smarter = more consistent)
    noise_scale = (100 - basketball_iq) * 0.003
    for opt in options:
        opt.utility += rng.gauss(0, noise_scale)

    # Pick highest utility
    return max(options, key=lambda o: o.utility)

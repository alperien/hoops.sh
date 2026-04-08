"""Backboard bank shot physics."""

from __future__ import annotations

from dataclasses import dataclass

from hoops_sim.physics.vec import Vec3
from hoops_sim.utils.constants import (
    BACKBOARD_OFFSET,
    BACKBOARD_WIDTH,
    BASKET_HEIGHT,
    BASKET_Y,
    COURT_LENGTH,
)


@dataclass
class BackboardContact:
    """Result of a ball hitting the backboard."""

    hit: bool
    contact_point: Vec3 | None = None
    reflected_velocity: Vec3 | None = None


# Backboard center positions for each side
LEFT_BACKBOARD_X = BACKBOARD_OFFSET
RIGHT_BACKBOARD_X = COURT_LENGTH - BACKBOARD_OFFSET
BACKBOARD_COR = 0.65  # Coefficient of restitution for glass backboard


def check_backboard_hit(
    ball_position: Vec3,
    ball_velocity: Vec3,
    attacking_right: bool = True,
) -> BackboardContact:
    """Check if the ball hits the backboard and calculate the reflection.

    Supports both baskets. The backboard is a vertical plane centered at
    y = BASKET_Y, with width BACKBOARD_WIDTH and height ~3.5 feet.

    Args:
        ball_position: Current ball position.
        ball_velocity: Current ball velocity.
        attacking_right: True if attacking the right basket.

    Returns:
        BackboardContact with hit status and reflected velocity if hit.
    """
    backboard_x = RIGHT_BACKBOARD_X if attacking_right else LEFT_BACKBOARD_X

    # Check if ball is past the backboard plane (moving away)
    if attacking_right:
        if ball_position.x < backboard_x - 1.0:
            return BackboardContact(hit=False)
    else:
        if ball_position.x > backboard_x + 1.0:
            return BackboardContact(hit=False)

    # Check if ball is in the backboard's y-range and z-range
    half_width = BACKBOARD_WIDTH / 2.0
    y_min = BASKET_Y - half_width
    y_max = BASKET_Y + half_width
    z_min = BASKET_HEIGHT - 0.5
    z_max = BASKET_HEIGHT + 3.0

    if not (y_min <= ball_position.y <= y_max
            and z_min <= ball_position.z <= z_max):
        return BackboardContact(hit=False)

    # Check if ball is close to the backboard plane
    if abs(ball_position.x - backboard_x) > 0.5:
        return BackboardContact(hit=False)

    # Ball hits the backboard: reflect the x-velocity
    contact_point = Vec3(
        backboard_x, ball_position.y, ball_position.z,
    )
    reflected = Vec3(
        -ball_velocity.x * BACKBOARD_COR,
        ball_velocity.y * 0.95,  # Slight energy loss in y
        ball_velocity.z * 0.95,  # Slight energy loss in z
    )

    return BackboardContact(
        hit=True, contact_point=contact_point,
        reflected_velocity=reflected,
    )

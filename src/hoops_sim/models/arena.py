"""Arena model: capacity, altitude, surface, crowd factor."""

from __future__ import annotations

from dataclasses import dataclass, field

from hoops_sim.physics.court_surface import CourtSurface


@dataclass
class Arena:
    """Team arena / venue.

    Models the physical venue and its effects on gameplay.
    """

    name: str = "Arena"
    city: str = "City"
    capacity: int = 19000
    altitude_ft: int = 0
    surface: CourtSurface = field(default_factory=CourtSurface)
    crowd_intensity: float = 0.7  # 0-1: how loud/engaged the home crowd is
    jumbotron_quality: float = 0.5  # Flavor stat

    def __post_init__(self) -> None:
        # Sync altitude between arena and surface
        if self.surface.altitude_ft != self.altitude_ft:
            self.surface.altitude_ft = self.altitude_ft

    def home_court_advantage(self) -> float:
        """Home court advantage modifier.

        Combines crowd intensity, altitude, and capacity fill rate.
        Returns a modifier (0.0 to ~0.05) added to home team performance.
        """
        return self.crowd_intensity * 0.03 + (self.altitude_ft / 100000.0)

    def crowd_energy_for_attendance(self, attendance: int) -> float:
        """Calculate crowd energy based on attendance.

        A full arena is louder than a half-empty one.
        Returns: 0-100 crowd energy score.
        """
        if self.capacity <= 0:
            return 50.0
        fill_pct = min(1.0, attendance / self.capacity)
        return fill_pct * self.crowd_intensity * 100.0

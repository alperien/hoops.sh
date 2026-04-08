"""League structure: conferences, divisions, salary cap."""

from __future__ import annotations

from dataclasses import dataclass, field

from hoops_sim.models.team import Team

# NBA Division/Conference structure
CONFERENCES = {
    "East": ["Atlantic", "Central", "Southeast"],
    "West": ["Northwest", "Pacific", "Southwest"],
}

DIVISIONS = {
    "Atlantic": 5,
    "Central": 5,
    "Southeast": 5,
    "Northwest": 5,
    "Pacific": 5,
    "Southwest": 5,
}


@dataclass
class SalaryCapInfo:
    """NBA salary cap and related thresholds for a season."""

    salary_cap: int = 136_000_000
    luxury_tax_threshold: int = 165_000_000
    first_apron: int = 172_000_000
    second_apron: int = 183_000_000
    max_salary_0_6: int = 32_000_000  # Max for 0-6 years experience
    max_salary_7_9: int = 39_000_000  # Max for 7-9 years experience
    max_salary_10_plus: int = 46_000_000  # Max for 10+ years
    minimum_salary: int = 1_100_000
    mid_level_exception: int = 12_800_000
    bi_annual_exception: int = 4_500_000
    rookie_scale_year1: list[int] = field(
        default_factory=lambda: [
            12_000_000, 10_800_000, 9_700_000, 8_600_000, 7_500_000,
            6_500_000, 5_600_000, 4_800_000, 4_100_000, 3_500_000,
            3_000_000, 2_600_000, 2_300_000, 2_100_000, 2_000_000,
            1_900_000, 1_800_000, 1_700_000, 1_600_000, 1_500_000,
            1_400_000, 1_300_000, 1_200_000, 1_200_000, 1_100_000,
            1_100_000, 1_100_000, 1_100_000, 1_100_000, 1_100_000,
        ]
    )

    def luxury_tax_for(self, payroll: int) -> int:
        """Calculate luxury tax bill for a given payroll."""
        if payroll <= self.luxury_tax_threshold:
            return 0
        overage = payroll - self.luxury_tax_threshold
        # Simplified progressive tax
        if overage <= 5_000_000:
            return int(overage * 1.5)
        if overage <= 10_000_000:
            return int(5_000_000 * 1.5 + (overage - 5_000_000) * 1.75)
        if overage <= 15_000_000:
            return int(5_000_000 * 1.5 + 5_000_000 * 1.75 + (overage - 10_000_000) * 2.5)
        return int(
            5_000_000 * 1.5 + 5_000_000 * 1.75 + 5_000_000 * 2.5
            + (overage - 15_000_000) * 3.25
        )

    def max_salary_for_experience(self, years: int) -> int:
        """Get maximum salary based on years of experience."""
        if years >= 10:
            return self.max_salary_10_plus
        if years >= 7:
            return self.max_salary_7_9
        return self.max_salary_0_6

    def rookie_salary(self, pick: int) -> int:
        """Get rookie scale salary for a draft pick (1-indexed)."""
        if 1 <= pick <= len(self.rookie_scale_year1):
            return self.rookie_scale_year1[pick - 1]
        return self.minimum_salary


@dataclass
class League:
    """The NBA league structure."""

    name: str = "NBA"
    season_year: int = 2025
    teams: list[Team] = field(default_factory=list)
    salary_cap: SalaryCapInfo = field(default_factory=SalaryCapInfo)

    def get_team(self, team_id: int) -> Team | None:
        """Find a team by ID."""
        for t in self.teams:
            if t.id == team_id:
                return t
        return None

    def get_team_by_abbr(self, abbr: str) -> Team | None:
        """Find a team by abbreviation."""
        for t in self.teams:
            if t.abbreviation == abbr:
                return t
        return None

    def conference_teams(self, conference: str) -> list[Team]:
        """Get all teams in a conference."""
        return [t for t in self.teams if t.conference == conference]

    def division_teams(self, division: str) -> list[Team]:
        """Get all teams in a division."""
        return [t for t in self.teams if t.division == division]

    def team_count(self) -> int:
        return len(self.teams)

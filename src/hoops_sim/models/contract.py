"""Player contract model with full NBA contract details."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional


class ContractType(enum.Enum):
    """Types of NBA contracts."""

    STANDARD = "standard"
    MAX = "max"
    ROOKIE_SCALE = "rookie_scale"
    VETERAN_MINIMUM = "veteran_minimum"
    MID_LEVEL = "mid_level"
    BI_ANNUAL = "bi_annual"
    TWO_WAY = "two_way"
    TEN_DAY = "ten_day"


class ContractOption(enum.Enum):
    """Contract option types for the final year."""

    NONE = "none"
    PLAYER_OPTION = "player_option"
    TEAM_OPTION = "team_option"
    EARLY_TERMINATION = "early_termination"


@dataclass
class Contract:
    """A player's contract.

    Models NBA contract details including salary, years, options,
    and special clauses.
    """

    total_years: int = 4
    current_year: int = 1  # Which year of the contract (1-indexed)
    salaries: List[int] = field(default_factory=lambda: [5_000_000] * 4)
    contract_type: ContractType = ContractType.STANDARD
    option_type: ContractOption = ContractOption.NONE
    option_year: int = 0  # Which year has the option (0 = none)
    no_trade_clause: bool = False
    trade_kicker_pct: float = 0.0  # Percentage bonus if traded (0-15%)
    incentives: Dict[str, int] = field(default_factory=dict)  # e.g., {"all_star": 500000}
    bird_rights: bool = True
    restricted_fa: bool = False  # Is the player a restricted free agent after this?

    @property
    def current_salary(self) -> int:
        """Current year's salary."""
        if 0 < self.current_year <= len(self.salaries):
            return self.salaries[self.current_year - 1]
        return 0

    @property
    def remaining_years(self) -> int:
        """Years remaining on the contract including current year."""
        return max(0, self.total_years - self.current_year + 1)

    @property
    def remaining_guaranteed(self) -> int:
        """Total guaranteed money remaining."""
        if self.current_year > len(self.salaries):
            return 0
        return sum(self.salaries[self.current_year - 1:])

    @property
    def average_annual_value(self) -> int:
        """Average annual value of the contract."""
        if not self.salaries:
            return 0
        return sum(self.salaries) // len(self.salaries)

    def is_expiring(self) -> bool:
        """Check if this is the last year of the contract."""
        return self.current_year == self.total_years

    def has_option(self) -> bool:
        """Check if the contract has an option."""
        return self.option_type != ContractOption.NONE

    def is_tradeable(self) -> bool:
        """Check if the player can be traded (no NTC or NTC waived)."""
        return not self.no_trade_clause

    def trade_kicker_amount(self) -> int:
        """Calculate the trade kicker bonus amount."""
        return int(self.current_salary * self.trade_kicker_pct / 100.0)

    def advance_year(self) -> bool:
        """Advance to the next contract year. Returns False if contract expired."""
        if self.current_year >= self.total_years:
            return False
        self.current_year += 1
        return True

    def is_rookie_deal(self) -> bool:
        return self.contract_type == ContractType.ROOKIE_SCALE

    def is_two_way(self) -> bool:
        return self.contract_type == ContractType.TWO_WAY

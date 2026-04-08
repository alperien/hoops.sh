"""Team model combining identity, roster, staff, and facilities."""

from __future__ import annotations

from dataclasses import dataclass, field

from hoops_sim.models.arena import Arena
from hoops_sim.models.coaching_staff import CoachingStaff
from hoops_sim.models.contract import Contract
from hoops_sim.models.front_office import FrontOffice
from hoops_sim.models.owner import Owner
from hoops_sim.models.player import Player, Position
from hoops_sim.models.relationships import RelationshipMatrix


@dataclass
class Team:
    """A complete NBA team.

    Combines identity, roster, coaching staff, front office,
    owner, arena, and relationship matrix.
    """

    # Identity
    id: int = 0
    city: str = ""
    name: str = ""  # e.g., "Lakers"
    abbreviation: str = ""  # e.g., "LAL"
    conference: str = ""  # "East" or "West"
    division: str = ""

    # Staff and facilities
    coaching_staff: CoachingStaff = field(default_factory=CoachingStaff)
    front_office: FrontOffice = field(default_factory=FrontOffice)
    owner: Owner = field(default_factory=Owner)
    arena: Arena = field(default_factory=Arena)

    # Roster
    roster: list[Player] = field(default_factory=list)
    contracts: dict[int, Contract] = field(default_factory=dict)  # player_id -> contract

    # Chemistry
    relationships: RelationshipMatrix = field(default_factory=RelationshipMatrix)

    @property
    def full_name(self) -> str:
        return f"{self.city} {self.name}"

    def roster_size(self) -> int:
        return len(self.roster)

    def get_player(self, player_id: int) -> Player | None:
        """Find a player on the roster by ID."""
        for p in self.roster:
            if p.id == player_id:
                return p
        return None

    def get_players_at_position(self, pos: Position) -> list[Player]:
        """Get all players who can play a given position."""
        return [p for p in self.roster if p.can_play_position(pos)]

    def get_starters(self) -> list[Player]:
        """Get the top 5 players by overall rating (simple default)."""
        sorted_roster = sorted(self.roster, key=lambda p: p.overall, reverse=True)
        return sorted_roster[:5]

    def total_payroll(self) -> int:
        """Total current salary commitments."""
        return sum(c.current_salary for c in self.contracts.values())

    def average_age(self) -> float:
        """Average age of the roster."""
        if not self.roster:
            return 0.0
        return sum(p.age for p in self.roster) / len(self.roster)

    def average_overall(self) -> float:
        """Average overall rating of the roster."""
        if not self.roster:
            return 0.0
        return sum(p.overall for p in self.roster) / len(self.roster)

    def best_player(self) -> Player | None:
        """Get the highest-rated player on the roster."""
        if not self.roster:
            return None
        return max(self.roster, key=lambda p: p.overall)

    def add_player(self, player: Player, contract: Contract | None = None) -> None:
        """Add a player to the roster."""
        self.roster.append(player)
        if contract is not None:
            self.contracts[player.id] = contract

    def remove_player(self, player_id: int) -> Player | None:
        """Remove a player from the roster."""
        for i, p in enumerate(self.roster):
            if p.id == player_id:
                self.roster.pop(i)
                self.contracts.pop(player_id, None)
                return p
        return None

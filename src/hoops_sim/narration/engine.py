"""Narration engine: generates play-by-play text from game events."""

from __future__ import annotations

import enum
from dataclasses import dataclass

from hoops_sim.utils.rng import SeededRNG


class NarrationIntensity(enum.Enum):
    """Intensity level of narration."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAXIMUM = "maximum"


@dataclass
class NarrationEvent:
    """A narrated game event."""

    text: str
    intensity: NarrationIntensity = NarrationIntensity.MEDIUM
    is_milestone: bool = False


# Template collections for different event types
SHOT_MADE_TEMPLATES = [
    "{shooter} pulls up from {distance}... GOT IT! {team} by {lead}.",
    "{shooter} catches and shoots... BANG! {points}-pointer is good.",
    "{shooter} with the jumper from {zone}... SWISH!",
    "{shooter} drives... finishes at the rim!",
    "{shooter} from downtown... DRAINS IT!",
]

SHOT_MISSED_TEMPLATES = [
    "{shooter} fires from {distance}... no good. {rebounder} grabs the board.",
    "{shooter} pulls up... rimmed out.",
    "{shooter} with the attempt from {zone}... off the mark.",
    "{shooter} contested shot... won't go.",
]

DUNK_TEMPLATES = [
    "{dunker} THROWS IT DOWN! What a slam!",
    "{dunker} with the powerful dunk!",
    "{dunker} drives and FLUSHES it!",
    "{dunker} soars and HAMMERS it home!",
]

TURNOVER_TEMPLATES = [
    "{player} loses the handle. Turnover.",
    "Pass from {passer} is PICKED OFF by {stealer}!",
    "{player} steps out of bounds. Turnover, {team} ball.",
    "Bad pass by {passer}. {stealer} comes up with the steal!",
]

BLOCK_TEMPLATES = [
    "{blocker} SWATS {shooter}'s shot away! What a block!",
    "{blocker} comes from the weak side... REJECTED!",
    "{shooter} tries to finish... BLOCKED by {blocker}!",
]

FREE_THROW_TEMPLATES = [
    "{shooter} at the line... {result}.",
    "{shooter} shoots the free throw... {result}.",
]

FOUL_TEMPLATES = [
    "Foul called on {fouler}. That's {team_fouls} team fouls this quarter.",
    "{fouler} reaches in... foul. {player} will shoot {fts} free throws.",
    "Whistle blows. {fouler} with the contact on {player}.",
]

TIMEOUT_TEMPLATES = [
    "Timeout called by {team}. They have {remaining} remaining.",
    "{team} takes a timeout to stop the bleeding.",
]

QUARTER_END_TEMPLATES = [
    "End of the {quarter}. Score: {home_team} {home_score}, {away_team} {away_score}.",
    "Buzzer sounds to end the {quarter}!",
]


class NarrationEngine:
    """Generates play-by-play narration text from game events."""

    def __init__(self, rng: SeededRNG) -> None:
        self.rng = rng
        self.play_count = 0

    def narrate_made_shot(
        self,
        shooter: str,
        team: str,
        points: int,
        distance: float,
        zone: str,
        lead: int,
        is_dunk: bool = False,
        is_and_one: bool = False,
    ) -> NarrationEvent:
        """Narrate a made basket."""
        self.play_count += 1

        if is_dunk:
            template = self.rng.choice(DUNK_TEMPLATES)
            text = template.format(dunker=shooter)
            intensity = NarrationIntensity.HIGH
        else:
            template = self.rng.choice(SHOT_MADE_TEMPLATES)
            text = template.format(
                shooter=shooter, team=team, points=points,
                distance=f"{distance:.0f} feet", zone=zone,
                lead=abs(lead),
            )
            intensity = NarrationIntensity.HIGH if points == 3 else NarrationIntensity.MEDIUM

        if is_and_one:
            text += " AND ONE! He's fouled on the play!"
            intensity = NarrationIntensity.HIGH

        return NarrationEvent(text=text, intensity=intensity)

    def narrate_missed_shot(
        self,
        shooter: str,
        distance: float,
        zone: str,
        rebounder: str | None = None,
    ) -> NarrationEvent:
        self.play_count += 1
        template = self.rng.choice(SHOT_MISSED_TEMPLATES)
        text = template.format(
            shooter=shooter, distance=f"{distance:.0f} feet",
            zone=zone, rebounder=rebounder or "Rebound",
        )
        return NarrationEvent(text=text, intensity=NarrationIntensity.LOW)

    def narrate_turnover(
        self,
        player: str,
        passer: str | None = None,
        stealer: str | None = None,
        team: str = "",
    ) -> NarrationEvent:
        self.play_count += 1
        if stealer and passer:
            templates = [t for t in TURNOVER_TEMPLATES if "{stealer}" in t]
        else:
            templates = [t for t in TURNOVER_TEMPLATES if "{stealer}" not in t]
        template = self.rng.choice(templates) if templates else TURNOVER_TEMPLATES[0]
        text = template.format(
            player=player, passer=passer or player,
            stealer=stealer or "Defense", team=team,
        )
        return NarrationEvent(text=text, intensity=NarrationIntensity.MEDIUM)

    def narrate_block(self, blocker: str, shooter: str) -> NarrationEvent:
        self.play_count += 1
        template = self.rng.choice(BLOCK_TEMPLATES)
        text = template.format(blocker=blocker, shooter=shooter)
        return NarrationEvent(text=text, intensity=NarrationIntensity.HIGH)

    def narrate_free_throw(self, shooter: str, made: bool) -> NarrationEvent:
        template = self.rng.choice(FREE_THROW_TEMPLATES)
        result = "good!" if made else "no good."
        text = template.format(shooter=shooter, result=result)
        return NarrationEvent(text=text, intensity=NarrationIntensity.LOW)

    def narrate_foul(
        self, fouler: str, player: str, team_fouls: int, fts: int, team: str = "",
    ) -> NarrationEvent:
        template = self.rng.choice(FOUL_TEMPLATES)
        text = template.format(
            fouler=fouler, player=player, team_fouls=team_fouls,
            fts=fts, team=team,
        )
        return NarrationEvent(text=text, intensity=NarrationIntensity.MEDIUM)

    def narrate_quarter_end(
        self, quarter: int, home_team: str, away_team: str,
        home_score: int, away_score: int,
    ) -> NarrationEvent:
        quarter_names = {1: "1st quarter", 2: "2nd quarter", 3: "3rd quarter", 4: "4th quarter"}
        q_name = quarter_names.get(quarter, f"overtime period {quarter - 4}")
        template = self.rng.choice(QUARTER_END_TEMPLATES)
        text = template.format(
            quarter=q_name, home_team=home_team, away_team=away_team,
            home_score=home_score, away_score=away_score,
        )
        return NarrationEvent(text=text, intensity=NarrationIntensity.MEDIUM)

    def narrate_timeout(self, team: str, remaining: int) -> NarrationEvent:
        template = self.rng.choice(TIMEOUT_TEMPLATES)
        text = template.format(team=team, remaining=remaining)
        return NarrationEvent(text=text, intensity=NarrationIntensity.LOW)

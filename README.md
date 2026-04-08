# hoops.sh

A maximum-fidelity basketball simulation engine written in Python. hoops.sh models NBA games at 0.1-second tick resolution with realistic physics, player AI, and full season management -- all from the terminal.

## Overview

hoops.sh is not a stats-based box score generator. It simulates games from the ground up: real ball trajectories under gravity and drag, player acceleration and deceleration physics, rim collision geometry, contact detection between bodies, and utility-based decision-making for every player on the court. The result is emergent gameplay that produces realistic stat lines because the underlying mechanics are realistic.

The project is in **Phase 1: Foundation & Physics**, building the core systems that everything else will sit on top of.

## Features

### Physics Engine
- **3D ball flight** with gravity, air drag, backspin, and sidespin (`physics/ball.py`, `physics/shot_trajectory.py`)
- **Rim interaction model** with swish, rattle-in, rim-out, backboard bank, and airball outcomes (`physics/rim_interaction.py`)
- **Carom direction** after misses influenced by shot angle, spin, and entry offset (`physics/rim_interaction.py`)
- **Player kinematics** with attribute-driven acceleration, deceleration, sprint, jog, lateral, and backpedal movement types (`physics/kinematics.py`)
- **Contact detection** between players with severity classification (incidental through flagrant) and force calculation (`physics/contact.py`)
- **Court surface** modeling with grip coefficients affected by humidity and wear (`physics/court_surface.py`)
- **Backboard physics** for bank shots (`physics/backboard.py`)
- **Vec2/Vec3 math** library with full operator overloading, normalization, dot/cross products, rotation, and interpolation (`physics/vec.py`)

### Tick Engine
- **0.1-second resolution** game loop that advances clock, movement, ball physics, and event checks every tick (`engine/tick.py`)
- **Game clock and shot clock** with proper NBA timing rules, overtime, and clutch time detection (`engine/clock.py`)
- **Possession state machine** with 13 states from pre-inbound through made basket, including transitions, free throws, jump balls, and dead ball (`engine/possession.py`)
- **Game state orchestrator** managing score, team fouls, timeouts, quarter flow, and overtime logic (`engine/game.py`)

### Player Model
- **60+ attributes** across 7 categories: shooting, finishing, playmaking, defense, rebounding, athleticism, and mental (`models/attributes.py`)
- **Physical body model** with height, weight, wingspan, standing reach, hand size, body fat, and handedness (`models/body.py`)
- **Badge system** with 30+ badges across 4 tiers (Bronze through Hall of Fame) covering shooting, finishing, playmaking, defense, rebounding, and mental categories (`models/badges.py`)
- **Tendencies** controlling shot selection, drive frequency, passing inclination, defensive aggression, and more (`models/tendencies.py`)
- **Shooting profile** with per-zone hot/cold modifiers across 17 court zones (`models/shooting_profile.py`)
- **Personality traits** including competitiveness, work ethic, ego, and coachability (`models/personality.py`)
- **Lifestyle factors** that can influence conditioning and availability (`models/lifestyle.py`)
- **Relationships** between teammates via a relationship matrix (`models/relationships.py`)

### Team Model
- **Full roster management** with contracts and salary tracking (`models/team.py`, `models/contract.py`)
- **Coaching staff** with head coach, assistants, and scheme preferences (`models/coaching_staff.py`)
- **Front office** management (`models/front_office.py`)
- **Owner model** and **arena model** with home court properties (`models/owner.py`, `models/arena.py`)

### Court & Zones
- **17 shooting zones** with polygon boundaries from restricted area through deep three (`court/zones.py`)
- **Court geometry** with full NBA dimensions, three-point line, paint, restricted area, and free throw line (`court/model.py`)
- **Passing lane analysis** for pass quality evaluation (`court/passing_lanes.py`)
- **Driving lane analysis** for drive opportunity evaluation (`court/driving_lanes.py`)
- **Spacing analysis** for offensive floor spacing quality (`court/spacing.py`)

### Shot Model
- **18-factor shot probability calculator** incorporating base rating, energy, contest quality, defender distance, badges, hot/cold zones, clutch situation, and more (`shot/probability.py`)
- **Trajectory calculation** with distance-based optimal release angles, skill-driven variance, and spin generation (`physics/shot_trajectory.py`)
- **Free throw system** (`shot/free_throw.py`)

### AI
- **Utility-based player brain** that evaluates shoot, drive, pass, post-up, and hold options weighted by opportunity quality, tendencies, shot clock urgency, and confidence (`ai/player_brain.py`)
- **Coach AI** handling rotation management, timeout decisions (reacting to opponent runs and turnover streaks), substitution urgency evaluation, and in-game adjustments (`ai/coach_brain.py`)

### Psychology
- **Per-player confidence tracker** that rises on makes and positive plays, falls on misses and turnovers, and feeds back into shot probability (`psychology/confidence.py`)
- **Team momentum system** on a -5 to +5 scale affected by scoring runs, blocks, steals, dunks, and timeouts (`psychology/momentum.py`)

### Physical / Fatigue
- **Tick-level energy drain** based on movement type (standing, walking, jogging, sprinting) with 5 fatigue tiers that progressively penalize performance (`physical/energy.py`)
- **Stamina-driven max energy** so higher-stamina players can sustain effort longer
- **Recovery** on the bench, during timeouts, and at halftime

### Injury System
- **25+ injury types** across 4 severity tiers (minor: 1-3 games, moderate: 4-15, serious: 16-40, severe: 40+ / season-ending) (`injury/risk.py`)
- **Risk factors** including fatigue, contact severity, age, durability, and injury history

### Referee
- **Foul adjudication** with referee crew tendencies: whistle tightness, home bias, star treatment, consistency, moving screen detection, and charge/block accuracy (`referee/foul_judge.py`)

### Narration
- **Play-by-play text generation** from game events with template-based narration for made/missed shots, dunks, turnovers, blocks, free throws, fouls, timeouts, and quarter endings (`narration/engine.py`)

### Season
- **Schedule generation** producing an 82-game round-robin schedule with home/away balance (`season/schedule.py`)
- **Standings tracking** with wins, losses, conference/division records, and tiebreakers (`season/standings.py`)

### Data Generation
- **Player generator** with 8+ archetype templates (scoring guard, playmaking guard, 3-and-D wing, scoring wing, stretch big, paint beast, two-way wing, floor general) that produce attribute distributions, body types, tendencies, and badge loadouts (`data/generator.py`)

### Actions
- **Dribble moves** and ball handling (`actions/dribble.py`)
- **Passing** mechanics (`actions/passing.py`)

### Movement
- **Off-ball movement** for players without the ball (`movement/off_ball.py`)
- **Defensive movement** positioning (`movement/defensive_movement.py`)
- **Locomotion** base layer (`movement/locomotion.py`)

### Defense
- **Pick-and-roll coverage** schemes (`defense/pnr_coverage.py`)

## Project Structure

```
src/hoops_sim/
  main.py              # CLI entry point
  physics/             # Ball flight, rim, contact, kinematics, court surface, vectors
  engine/              # Tick loop, game clock, possession state machine, game state
  models/              # Player, team, attributes, badges, body, tendencies, contracts, etc.
  court/               # Court geometry, 17 zones, passing/driving lanes, spacing
  shot/                # 18-factor probability, free throws
  ai/                  # Player brain (utility-based), coach brain (rotations/timeouts)
  psychology/          # Confidence tracker, team momentum
  physical/            # Energy drain/recovery, fatigue tiers
  injury/              # 25+ injury types, risk calculation
  referee/             # Foul adjudication with ref tendencies
  narration/           # Play-by-play text generation
  season/              # Schedule generation, standings
  data/                # Player/team generators with archetype templates
  actions/             # Dribble, passing
  movement/            # Off-ball, defensive, locomotion
  defense/             # PnR coverage
  utils/               # Constants, math helpers, seeded RNG
  tui/                 # Terminal UI (screens, widgets) -- placeholder
  plays/               # Play system -- placeholder
  history/             # Game history -- placeholder
  off_court/           # Off-court events -- placeholder
  offseason/           # Offseason logic -- placeholder
tests/                 # Mirrors src structure with tests for every module
```

## Requirements

- Python 3.9+
- [Textual](https://github.com/Textualize/textual) >= 0.40 (for the TUI)

## Installation

```bash
# Clone the repository
git clone https://github.com/alperien/hoops.sh.git
cd hoops.sh

# Install in development mode
pip install -e ".[dev]"
```

## Usage

```bash
# Run the CLI (currently prints version info)
hoops

# Run the test suite
pytest

# Run with coverage
pytest --cov=hoops_sim

# Type checking
mypy src/

# Linting
ruff check src/ tests/
```

## Development

The project uses:
- **[Hatch](https://hatch.pypa.io/)** as the build backend
- **[pytest](https://docs.pytest.org/)** for testing
- **[mypy](https://mypy-lang.org/)** for static type checking
- **[ruff](https://docs.astral.sh/ruff/)** for linting and formatting

All tunable simulation constants live in a single file at `src/hoops_sim/utils/constants.py`, making calibration straightforward.

The simulation uses a `SeededRNG` wrapper around Python's random module to ensure reproducible game outcomes from a given seed.

## License

MIT

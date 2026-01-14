---
name: decode
description: DECODE 2025-2026 FTC game reference. Use when programming autonomous routines, calculating scores, understanding field layout, or working with game-specific coordinates.
---

# DECODE 2025-2026 FTC Game

DECODE presented by RTX is the 2025-2026 FIRST Tech Challenge game where teams collect, classify, and score artifacts to unlock patterns and motifs.

## Quick Reference

| Element | Description |
|---------|-------------|
| **Artifacts** | Ball-shaped game pieces (Purple and Green) |
| **Control Limit** | Maximum 3 artifacts at a time |
| **Cycle** | Collect → Classify/Score → Repeat |
| **Field** | 144" × 144" (12ft × 12ft) |

## Match Structure

| Period | Duration | Notes |
|--------|----------|-------|
| Autonomous | 30 seconds | Pre-programmed robot actions |
| Driver-Controlled | 2 minutes | Manual control with gamepad |
| End Game | Last 30 seconds | Bonus scoring opportunities |

## Field Layout (Pedro Coordinates)

```
        Y = 144" (back wall)
    ┌────────────────────────────────────┐
    │                                    │
    │     [GOALS]      [GOALS]           │
    │                                    │
    │  ┌─────────┐                       │
    │  │CLASSIFIER                       │
    │  └─────────┘                       │
    │                                    │
    │        [ARTIFACTS]                 │
    │                                    │
    │  ┌──────┐              ┌──────┐    │
    │  │ RED  │              │ BLUE │    │
    │  │START │              │START │    │
    │  └──────┘              └──────┘    │
    └────────────────────────────────────┘
        Y = 0" (audience wall)

    X = 0"                          X = 144"
```

## Key Positions (Pedro Coordinates)

See [FIELD_POSITIONS.md](FIELD_POSITIONS.md) for complete coordinates.

| Location | X (in) | Y (in) | Heading (°) |
|----------|--------|--------|-------------|
| Red Start | 7 | 7 | 0 |
| Blue Start | 137 | 7 | 180 |
| Classifier | 24 | 72 | 90 |

## Robot Mechanisms

Based on game strategy:

1. **Intake** - Collect artifacts from field
2. **Indexer** - Hold up to 3 artifacts, feed to shooter
3. **Shooter** - Flywheel + turret + hood for launching
4. **Vision** - Limelight 3A for target tracking

## Coordinate Conversion Scripts

Use `uv run` to execute conversion scripts:

```bash
# FTC (meters) to Pedro (inches)
uv run .claude/skills/decode/scripts/convert.py ftc-to-pedro 0 0 90

# Tile coordinates to Pedro
uv run .claude/skills/decode/scripts/convert.py tile-to-pedro 3 3
uv run .claude/skills/decode/scripts/convert.py tile-center 2 4

# Mirror red alliance pose for blue
uv run .claude/skills/decode/scripts/convert.py mirror-blue 7 6.75 0

# Show all coordinate systems for a point
uv run .claude/skills/decode/scripts/convert.py all 72 72
```

## Reference Documentation

- [SCORING.md](SCORING.md) - Point values and strategies
- [FIELD_POSITIONS.md](FIELD_POSITIONS.md) - All positions in Pedro coordinates
- [COORDINATES.md](COORDINATES.md) - Coordinate system details
- [STRATEGY.md](STRATEGY.md) - Autonomous and teleop strategies

## Official Resources

- [Competition Manual](https://ftc-resources.firstinspires.org/ftc/game/manual)
- [Game Animation](https://www.firstinspires.org/programs/ftc/game-and-season)
- [Team Q&A](https://ftc-qa.firstinspires.org/)

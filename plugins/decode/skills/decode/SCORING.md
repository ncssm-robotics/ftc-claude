# DECODE Scoring Reference

*Note: Point values are estimates. Verify with official Game Manual.*

## Autonomous Period (30 seconds)

| Action | Points | Notes |
|--------|--------|-------|
| Park in zone | TBD | End of auto position |
| Score artifact | TBD | Higher than teleop |
| Complete pattern | TBD | Bonus multiplier |

## Teleop Period (2 minutes)

| Action | Points | Notes |
|--------|--------|-------|
| Artifact in High Goal | TBD | Long-range shot |
| Artifact in Low Goal | TBD | Easier, fewer points |
| Classifier match | TBD | Color-matched bonus |

## End Game (Last 30 seconds)

| Action | Points | Notes |
|--------|--------|-------|
| Park in zone | TBD | Position bonus |
| Pattern complete | TBD | All artifacts matched |

## Penalties

| Violation | Penalty |
|-----------|---------|
| Control >3 artifacts | Warning, then points |
| Excessive control (5+) | Major penalty |
| Pinning | Warning after 5 seconds |

## Strategy Considerations

### Cycle Time Analysis

Target cycle time: ~8-10 seconds per cycle
- Intake: 1-2 seconds
- Drive to goal: 2-3 seconds
- Aim and shoot: 2-3 seconds
- Return for next: 2-3 seconds

### Expected Match Performance

| Level | Cycles | Score Range |
|-------|--------|-------------|
| Beginner | 5-8 | Low |
| Competitive | 12-15 | Medium |
| Elite | 18-22 | High |

### Autonomous Priority

1. Score preloaded artifacts (guaranteed points)
2. Collect and score additional artifacts
3. End in advantageous position for teleop

### Teleop Priority

1. Fast, consistent cycles
2. Prioritize high-value goals
3. Coordinate with alliance partner
4. Reserve time for end game

## Control Limit Strategy

Maximum 3 artifacts at a time (Rule G408):
- Collect 3 artifacts
- Score all 3
- Repeat cycle

Exceeding limit:
- 4 artifacts momentary: Warning
- 5+ artifacts: Major penalty
- Repeated violations: Escalating penalties

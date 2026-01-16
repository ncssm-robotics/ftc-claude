# Autonomous Controller Tuning

Guide for using the `/tune` command to autonomously tune PID and feedforward gains.

## Quick Start

```bash
/tune

# Follow prompts:
# 1. Select mechanism (elevator, arm, flywheel, turret)
# 2. Enter physical limits
# 3. Choose tuning algorithm
# 4. Deploy generated OpMode
# 5. Run tuning iterations
# 6. Accept final gains
```

## Prerequisites

**Required:** robot-dev skill for `/deploy`, `/init`, `/start`, `/stop`

**Recommended:** panels skill for real-time parameter updates

## Supported Mechanisms

| Mechanism | Parameters | Use Case |
|-----------|------------|----------|
| Elevator | kP, kD, kG | Vertical linear slides |
| Arm | kP, kD, kG | Rotating arms |
| Flywheel | kP, kV | Launcher wheels |
| Turret | kP, kD | Rotating turrets |

## Tuning Algorithms

### 1. Step Response (SAFE - Recommended)

- Applies step input, analyzes rise time/overshoot/settling
- Conservative gains, minimal risk
- **Best for:** First-time tuning, safety-critical mechanisms

### 2. Ziegler-Nichols (MEDIUM RISK)

- Uses critical gain (Ku) and period (Tu)
- Industry-standard tuning rules
- **Best for:** Experienced teams, well-secured mechanisms
- **Warning:** Mechanism will oscillate during Ku finding

### 3. Relay Feedback (HIGHER RISK)

- Bang-bang control induces stable oscillation
- Automated Ku/Tu measurement
- **Best for:** Automated tuning with adequate clearance
- **Warning:** Significant oscillation during test

### 4. Optimization (MEDIUM RISK)

- Numerical optimization using scipy
- 5-20 iterations required
- **Best for:** Performance-critical mechanisms

## Workflow

### Phase 1: Setup
- Select mechanism type
- Enter position/velocity limits
- Choose algorithm

### Phase 2: OpMode Generation
Generates tuning OpMode for your library (NextFTC, FTCLib, or Plain SDK):
- Safety limits
- Telemetry logging
- Configurable parameters

### Phase 3: Deployment
Uses `/deploy` to build and install OpMode.

### Phase 4: Safety Checks
- [ ] Battery >12V
- [ ] Mechanism at safe position
- [ ] No obstacles in range
- [ ] Emergency stop accessible

### Phase 5: Tuning Iterations
```
for each iteration:
    1. Init OpMode
    2. Start and record telemetry
    3. Analyze and calculate new gains
    4. User decides: Continue / Revert / Accept / Abort
```

### Phase 6: Finalization
Applies gains via Sloth Load or Panels configurables.

## Safety

### Generated OpMode Safety
```kotlin
// Hard position limits
if (position < MIN || position > MAX) {
    motor.power = 0.0
    requestOpModeStop()
}

// Timeout protection
if (runtime.seconds() > TEST_DURATION + 5) {
    requestOpModeStop()
}
```

### Human-in-the-Loop
- Explicit approval before EVERY test run
- Real-time telemetry display
- Emergency abort: Ctrl+C

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Can't connect to Panels | Falls back to logcat automatically |
| Battery voltage too low | Charge >12V before tuning |
| OpMode not found | Check build.gradle dependencies |
| Gains unstable | Use Step Response, reduce kP |
| Mechanism hits limits | Adjust limits in setup, reduce range |
| No telemetry data | Check OpMode running, logcat output |

## Best Practices

### Before Tuning
- Secure mechanism from damage
- Fresh battery (>12.5V)
- Measure accurate limits
- Start with Step Response

### During Tuning
- Monitor telemetry in real-time
- Don't rush iterations
- Keep emergency stop ready

### After Tuning
- Test with full OpModes
- Document final gains
- Save to version control

### Key Principle
**Feedforward first.** Tune kG/kV before PID. Feedforward should do 80-90% of the work.

## Example Session

```
$ /tune

Select mechanism: Elevator
Enter limits: 0-2000 ticks, 1500 ticks/sec max

Select algorithm: Step Response (SAFE)

✓ OpMode generated
✓ Deployed to robot
✓ Panels connected

SAFETY CHECK - Ready? yes

─── RUN 1/5 ───
Current: kP=0.001 kD=0.000 kG=0.000
Analysis: Steady-state error → kG=0.15 needed
Proposed: kP=0.001 kD=0.000 kG=0.150
Continue? c

─── RUN 2/5 ───
Current: kP=0.001 kD=0.000 kG=0.150
Analysis: Rise time 2.5s → increase kP
Proposed: kP=0.005 kD=0.000 kG=0.150
Continue? c

─── RUN 3/5 ───
Current: kP=0.005 kD=0.000 kG=0.150
Analysis: Good response, slight oscillation
Proposed: kP=0.004 kD=0.0002 kG=0.150
Accept? a

✓ FINAL GAINS:
  kP = 0.0040
  kD = 0.0002
  kG = 0.150

✓ Applied via Sloth Load
✓ Saved to tuning_results.json
```

## See Also

- [TUNING_GUIDE.md](TUNING_GUIDE.md) - Manual tuning reference
- [MECHANISMS.md](MECHANISMS.md) - Mechanism implementations
- [DIAGNOSTICS.md](DIAGNOSTICS.md) - Troubleshooting

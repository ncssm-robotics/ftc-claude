# Autonomous Controller Tuning Guide

Comprehensive guide for using the `/tune-controller` command to autonomously tune PID and feedforward gains.

## Overview

The autonomous tuning system provides a complete workflow for tuning FTC robot mechanisms:
- **Automatic OpMode generation** using your existing libraries (NextFTC, FTCLib, or Plain SDK)
- **Real-time telemetry capture** via Panels or logcat
- **Multiple tuning algorithms** from safe to optimal
- **Live parameter updates** via Sloth Load (prioritized) or Panels configurables (if Sloth not installed)
- **Voltage regularization** with 12V nominal voltage compensation
- **Safety-first design** with human approval at each step

## Quick Start

```bash
/tune-controller

# Follow prompts:
# 1. Select mechanism (elevator, arm, flywheel, turret)
# 2. Enter physical limits
# 3. Choose tuning algorithm
# 4. Deploy generated OpMode
# 5. Position robot safely
# 6. Run tuning iterations
# 7. Accept final gains
```

## Prerequisites

### Required Skills
- **robot-dev** - For `/deploy`, `/init`, `/start`, `/stop` commands

### Recommended Skills (at least one)
- **panels** - For real-time parameter updates via WebSocket (will prompt to install if missing)
- **sloth-load** - For hot-reload code changes (prioritized if both installed)

### Library Requirements
The system detects and uses your existing FTC libraries:
- **NextFTC** - Uses `ControlSystem.builder()` patterns
- **FTCLib** - Uses `PIDController` and `PIDFController`
- **Plain FTC SDK** - Generates manual PID implementations

### Hardware Requirements
- Robot with your chosen FTC library (NextFTC, FTCLib, or Plain SDK)
- FTC Control Hub or RC Phone
- USB or WiFi connection via ADB
- Battery voltage monitoring (nominal: 12V for voltage regularization)

## Supported Mechanisms

| Mechanism | Control Type | Parameters | Typical Use Case |
|-----------|--------------|------------|------------------|
| **Elevator/Lift** | Position + Gravity FF | kP, kD, kG | Vertical linear slides |
| **Arm/Pivot** | Position + Arm FF | kP, kD, kG, angle | Rotating arms |
| **Flywheel/Shooter** | Velocity + Velocity FF | kP, kV | Launcher wheels |
| **Turret** | Position only | kP, kD | Rotating turrets, intakes |

## Tuning Algorithms

### 1. Step Response (SAFE - Recommended)

**Best for:** First-time tuning, safety-critical mechanisms

**How it works:**
- Applies a step input (move to target position)
- Analyzes rise time, overshoot, settling time
- Calculates conservative gains to avoid oscillation

**Pros:**
- Very safe, minimal risk of damage
- Fast (1-2 test runs)
- No oscillation during tuning
- Good starting point for manual refinement

**Cons:**
- Produces conservative (under-tuned) gains
- May be slower than optimal response

**Safety:** LOW risk

### 2. Ziegler-Nichols (MEDIUM RISK)

**Best for:** Experienced teams, well-secured mechanisms

**How it works:**
- Requires critical gain (Ku) and period (Tu)
- Applies industry-standard tuning rules
- Three variants: Classic, No Overshoot, Pessen

**Pros:**
- Industry standard, proven methodology
- Well-documented and widely used
- Balances performance and stability

**Cons:**
- Requires finding Ku/Tu (via relay feedback or manual testing)
- Mechanism will oscillate during Ku finding
- Can be aggressive with classic rule

**Safety:** MEDIUM risk (oscillation during testing)

### 3. Relay Feedback Test (HIGHER RISK)

**Best for:** Automated Ku/Tu finding, mechanisms with adequate clearance

**How it works:**
- Bang-bang control (full power on/off)
- Induces stable oscillation
- Measures amplitude and period to calculate Ku/Tu
- Feeds into Ziegler-Nichols rules

**Pros:**
- Fully automated Ku/Tu finding
- Objective measurement (no manual guessing)
- Produces accurate Z-N gains

**Cons:**
- Significant oscillation during test
- Requires adequate space/clearance
- Can be alarming to watch

**Safety:** MEDIUM-HIGH risk (significant oscillation)

### 4. Optimization (scipy) (MEDIUM RISK, TIME INTENSIVE)

**Best for:** Performance-critical mechanisms, teams with time to iterate

**How it works:**
- Numerical optimization using scipy
- Minimizes error metric (IAE, ISE, or ITAE)
- Runs multiple test iterations
- Converges to mathematically optimal gains

**Pros:**
- Finds truly optimal gains
- Can optimize for specific metrics
- Handles complex dynamics

**Cons:**
- 5-20 test runs required
- Time-consuming (15-30 minutes)
- Each iteration could be unstable
- Computationally intensive

**Safety:** MEDIUM risk (multiple runs, some may be unstable)

## Workflow Phases

### Phase 1: Setup

Interactive prompts guide you through:
1. **Mechanism Selection** - Choose elevator, arm, flywheel, or turret
2. **Physical Limits** - Enter min/max position, velocity, acceleration
3. **Algorithm Selection** - Choose tuning method with safety warnings

**Configuration is saved** to `mechanism_config.json` for reproducibility.

### Phase 2: OpMode Generation

The system generates a tuning OpMode using your detected libraries:
- **NextFTC**: Uses `ControlSystem.builder()` with voltage regularization
- **FTCLib**: Uses `PIDController`/`PIDFController` with manual voltage compensation
- **Plain SDK**: Manual PID implementation with voltage regularization
- **Parameter Updates**: @Configurable parameters (unless using Sloth Load only)
- Safety limits (position, velocity, timeout)
- Structured telemetry (Panels + JSON logging)
- Test command (step input, oscillation, or velocity ramp)

**Output files:**
- `TeamCode/src/.../tuning/{Mechanism}TuningOpMode.kt`
- `TeamCode/src/.../tuning/TuningConfig.kt`

### Phase 3: Deployment

Uses robot-dev `/deploy` command to:
- Build project with Gradle
- Install APK via ADB
- Restart Robot Controller
- Verify Panels connection

### Phase 4: Safety Checks

Pre-flight checklist:
- ☐ Battery voltage monitored (nominal: 12V for voltage regularization)
- ☐ Mechanism at safe starting position
- ☐ No obstacles in range of motion
- ☐ Emergency stop accessible
- ☐ Someone monitoring robot

**Explicit "yes" required** to proceed.

### Phase 5: Tuning Iterations

Iterative loop:
```
for each iteration:
    1. Init OpMode (via /init)
    2. Start telemetry capture
    3. Start OpMode (via /start)
    4. Wait for test completion (20-60 seconds)
    5. Stop OpMode (via /stop)
    6. Analyze telemetry with selected algorithm
    7. Calculate new gains
    8. Display: current → proposed gains
    9. User decides:
       - Continue (c): Apply gains, run next iteration
       - Revert (r): Go back to previous gains
       - Accept (a): Finalize current gains
       - Abort (q): Stop tuning
```

**Real-time telemetry** displayed during runs:
- Position, velocity, error, power
- Current PID gains
- Time remaining
- On-target status

### Phase 6: Finalization

Parameter application (priority order):
1. **Sloth Load + Panels** → Use Sloth Load (hot-reload code)
2. **Sloth Load only** → Use Sloth Load (hot-reload code, no @Configurable needed)
3. **Panels only** → Update configurables (persist in dashboard)
4. **Neither** → Display gains for manual entry, offer Panels install

**Results saved** to `tuning_results.json`:
- Mechanism configuration
- Algorithm used
- Final gains
- Number of iterations
- Telemetry data

## Safety Architecture

### Pre-Flight Checks
- Battery voltage monitoring (nominal: 12V for voltage regularization)
- ADB connection validation
- Panels connectivity verification
- User acknowledgment of mechanism-specific risks

### Generated OpMode Safety
```kotlin
// Hard position limits
if (position < MIN || position > MAX) {
    motor.power = 0.0
    requestOpModeStop()
}

// Velocity limiting
power = power.coerceIn(-1.0, 1.0)

// Timeout protection
if (runtime.seconds() > TEST_DURATION + 5) {
    requestOpModeStop()
}
```

### Human-in-the-Loop
- Explicit approval before EVERY test run
- Real-time telemetry display
- Emergency abort: Ctrl+C stops script
- Conservative initial gains (first run barely moves)

### Algorithm-Specific Warnings

| Algorithm | Warning | Required Actions |
|-----------|---------|-----------------|
| Step Response | Minimal movement | Ensure mechanism can move freely |
| Ziegler-Nichols | Will oscillate | Provide adequate clearance |
| Relay Feedback | Significant oscillation | Double-check clearance, secure mechanism |
| Optimization | Multiple runs | Be patient, monitor for instability |

## Telemetry Capture

### Dual-Mode System

**Primary: Panels WebSocket**
- Real-time structured data
- Cleaner signal
- Works with Panels dashboard running

**Fallback: Logcat Parsing**
- Parses JSON from log messages
- More robust (works without Panels)
- Requires structured logging in OpMode

**Automatic fallback** if Panels unavailable.

## Troubleshooting

### "Cannot connect to Panels"
- **Solution:** Falls back to logcat automatically
- Verify robot powered on and on WiFi (192.168.43.x)
- Check Panels dashboard accessible at http://192.168.43.1:8001

### "Battery voltage too low"
- **Solution:** Charge battery >12V before tuning
- Low voltage causes inconsistent motor behavior
- Gains tuned on low battery won't work at full voltage

### "OpMode not found after deploy"
- **Solution:** Check `build.gradle` has NextFTC control dependency
- Verify TeamCode module builds successfully
- Look for compilation errors in build output

### "Gains are unstable/oscillating"
- **Solution:** Choose "Step Response" for more conservative gains
- Reduce kP by 50%
- Add small kD (start with kP/10)
- Ensure kG (feedforward) is tuned first

### "Mechanism hits limits during tuning"
- **Solution:** OpMode includes emergency stop on limit violation
- Review and adjust physical limits in setup phase
- Start with smaller range of motion for first test

### "Telemetry capture returns no data"
- **Solution:** Verify OpMode is running
- Check logcat output includes "TUNING" tag
- For Panels: Ensure on robot WiFi
- Try `--logcat-only` flag

## Tips and Best Practices

### Before Tuning
1. **Secure the mechanism** - Ensure it can't damage itself or surroundings
2. **Fresh battery** - Voltage affects motor behavior significantly
3. **Measure limits accurately** - Use encoders to find actual min/max positions
4. **Start safe** - Always use Step Response for first-time tuning

### During Tuning
1. **Monitor telemetry** - Watch position/velocity/power in real-time
2. **Don't rush** - Take time to understand each iteration's behavior
3. **Document observations** - Note any unusual behavior or patterns
4. **Emergency stop ready** - Keep finger near stop button

### After Tuning
1. **Test thoroughly** - Run full OpModes with tuned gains
2. **Document gains** - Save to version control with notes
3. **Iterate if needed** - Can re-run `/tune-controller` to refine
4. **Share results** - Help teammates understand the tuning process

### Feedforward First
- Always tune kG (gravity) or kV (velocity) BEFORE PID
- Feedforward should do 80-90% of the work
- PID corrects the remaining 10-20%

### Conservative is Better
- Under-tuned is safer than over-tuned
- Can always increase gains later
- Over-tuned gains can damage hardware

## Example Session

### Elevator Tuning (Step Response)

```
$ /tune-controller

Detecting libraries in build.gradle...
✓ NextFTC detected - using ControlSystem.builder() patterns
✓ Panels detected - using @Configurable parameters
✓ Sloth Load not detected - will use Panels configurables

Select mechanism type:
  1. Elevator/Lift
  2. Arm/Pivot
  3. Flywheel/Shooter
  4. Turret
> 1

Enter physical limits for Elevator:
  Min position (ticks): 0
  Max position (ticks): 2000
  Max velocity (ticks/sec): 1500
  Max acceleration (ticks/sec²): 3000

Select tuning algorithm:
  [1] Step Response (SAFE)
  [2] Ziegler-Nichols (MEDIUM RISK)
  [3] Relay Feedback (HIGHER RISK)
  [4] Optimization (MEDIUM RISK, TIME INTENSIVE)
> 1

✓ Configuration saved
✓ OpMode generated: ElevatorTuningOpMode.kt (NextFTC with voltage regularization)
✓ TuningConfig.kt created

Deploying... (running /deploy)
✓ Build successful
✓ Installed to robot
✓ Panels connected

SAFETY CHECKLIST:
  ☐ Battery voltage >12V ✓ (12.4V)
  ☐ Elevator at safe mid-height ✓
  ☐ No obstacles above/below ✓
  ☐ Emergency stop accessible ✓
  ☐ Someone monitoring robot ✓

Ready? yes

─────────────────────────────────────
TUNING RUN 1/5
─────────────────────────────────────
Current: kP=0.001 kD=0.000 kG=0.000

(Init OpMode via /init)
(Start OpMode via /start)
Recording telemetry... 2.5Hz ████████

Analysis: Steady-state error indicates kG=0.15 needed
Proposed: kP=0.001 kD=0.000 kG=0.150

Continue? c

─────────────────────────────────────
TUNING RUN 2/5
─────────────────────────────────────
Current: kP=0.001 kD=0.000 kG=0.150

Recording telemetry... 2.5Hz ████████

Analysis: Rise time 2.5s → increase kP
Proposed: kP=0.005 kD=0.000 kG=0.150

Continue? c

─────────────────────────────────────
TUNING RUN 3/5
─────────────────────────────────────
Current: kP=0.005 kD=0.000 kG=0.150

Recording telemetry... 2.5Hz ████████

Analysis: Good response, slight oscillation
Proposed: kP=0.004 kD=0.0002 kG=0.150

Continue? a

✓ Gains accepted!

FINAL TUNED PARAMETERS:
  kP = 0.0040
  kD = 0.0002
  kG = 0.150 (gravity feedforward)

Detecting parameter application...
  ✓ Sloth Load detected
  ✓ Panels installed

Applying via Sloth Load (prioritized)...
✓ Updated: TeamCode/.../TuningConfig.kt
✓ Hot-reloaded successfully
✓ Voltage regularization: 12V nominal applied

Verify final behavior? yes
(Run final test with tuned gains)

✓ Verification complete!
✓ Results saved to tuning_results.json

Tuning complete in 8 minutes, 3 iterations
```

## Advanced Topics

### Gain Scheduling
For mechanisms with varying dynamics (e.g., arm at different angles):
1. Tune at multiple operating points
2. Interpolate gains based on position/angle
3. Update gains in real-time via `periodic()`

### Cascade Control
For elevator velocity → position control:
1. Tune inner loop (velocity) first
2. Then tune outer loop (position)
3. Use separate TuningConfig variables

### Disturbance Rejection
Test tuned gains under load:
1. Apply external forces during operation
2. Measure recovery time and overshoot
3. Adjust kI if steady-state error remains

## Implementation Details

### File Structure
```
plugins/
├── control-engineer/
│   ├── commands/
│   │   └── tune-controller.md          # Command definition
│   ├── scripts/
│   │   ├── telemetry_recorder.py       # Telemetry capture
│   │   └── tuning_algorithms.py        # PID algorithms
│   └── skills/control-engineer/
│       └── AUTONOMOUS_TUNING.md         # This file
├── robot-dev/
│   └── scripts/
│       ├── opmode_generator.py          # OpMode generation
│       ├── config_updater.py            # Panels WebSocket updates
│       └── tuning_orchestrator.py       # Main coordinator
```

### Dependencies
- Python 3.8+ with uv
- websocket-client (Panels communication)
- numpy (numerical analysis)
- scipy (optimization algorithms)

## See Also

- [TUNING_GUIDE.md](TUNING_GUIDE.md) - Manual tuning reference
- [MECHANISMS.md](MECHANISMS.md) - Mechanism-specific implementations
- [DIAGNOSTICS.md](DIAGNOSTICS.md) - Troubleshooting control problems
- Robot-dev skill: `/deploy`, `/init`, `/start`, `/stop` commands
- Panels skill: Real-time configurables and telemetry

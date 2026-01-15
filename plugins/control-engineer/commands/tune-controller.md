---
description: Autonomously tune PID and feedforward gains for robot mechanisms
argument-hint: ""
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion]
---

# /tune-controller - Autonomous Controller Tuning

Provides fully autonomous PID and feedforward tuning for FTC robot mechanisms. Generates test OpModes, runs experiments, captures telemetry, analyzes data, and tunes parameters in real-time.

## What This Command Does

This command orchestrates a complete tuning workflow:

1. **Interactive Setup**: Guides you through mechanism type selection, physical limits, and tuning algorithm choice
2. **Library Detection**: Scans build.gradle to detect NextFTC, FTCLib, or Plain SDK
3. **OpMode Generation**: Creates a tuning OpMode using your detected libraries with voltage regularization (12V nominal)
4. **Deployment**: Uses `/deploy` to build and install the OpMode
5. **Safety Checks**: Verifies battery, connection, and positioning before running
6. **Automated Tuning**: Runs multiple test iterations, captures telemetry, analyzes responses, and adjusts gains
7. **Parameter Application**: Updates gains via Sloth Load (prioritized), Panels configurables (if Sloth not installed), or displays for manual entry

## Prerequisites

**Required Skills:**
- `robot-dev` - For `/deploy`, `/init`, `/start`, `/stop`, `/log` commands

**Recommended (at least one):**
- `panels` - For real-time parameter updates via WebSocket (will prompt to install if missing)
- `sloth-load` - For hot-reload code changes (prioritized if both installed)

**Library Requirements:**
The system detects and uses your existing FTC libraries:
- **NextFTC** - Uses `ControlSystem.builder()` patterns with voltage regularization
- **FTCLib** - Uses `PIDController` and `PIDFController` with voltage compensation
- **Plain FTC SDK** - Generates manual PID implementations with voltage regularization

## Supported Mechanisms

| Mechanism | Control Type | Parameters Tuned |
|-----------|--------------|------------------|
| **Elevator/Lift** | Position + Gravity FF | kP, kD, kG |
| **Arm/Pivot** | Position + Arm FF | kP, kD, kG |
| **Flywheel/Shooter** | Velocity + Velocity FF | kP, kV |
| **Turret** | Position only | kP, kD |

## Tuning Algorithms

### 1. Step Response (SAFE - Recommended)
- **Safety**: LOW risk
- **Speed**: 1-2 test runs
- **Method**: Analyze step response (rise time, overshoot, settling time)
- **Result**: Conservative, stable gains
- **Best for**: First-time tuning, safety-critical mechanisms

### 2. Ziegler-Nichols (MEDIUM RISK)
- **Safety**: MEDIUM risk (oscillation during testing)
- **Speed**: 3-5 test runs
- **Method**: Find critical gain (Ku) and period (Tu), apply tuning rules
- **Result**: Industry-standard gains, potentially aggressive
- **Best for**: Experienced teams, well-secured mechanisms

### 3. Relay Feedback Test (HIGHER RISK)
- **Safety**: MEDIUM-HIGH risk (significant oscillation)
- **Speed**: 2-3 test runs for Ku/Tu finding
- **Method**: Automated bang-bang control to find oscillation parameters
- **Result**: Accurate Ku/Tu for Ziegler-Nichols
- **Best for**: Automated Ku finding, mechanisms with adequate clearance

### 4. Optimization (scipy) (MEDIUM RISK, TIME INTENSIVE)
- **Safety**: MEDIUM risk (multiple iterations, some potentially unstable)
- **Speed**: 5-20 test runs
- **Method**: Numerical optimization minimizing error metrics (IAE, ISE, ITAE)
- **Result**: Mathematically optimal gains
- **Best for**: Performance-critical mechanisms, teams with time to iterate

## Process Overview

```
User: /tune-controller

↓

1. Mechanism Selection
   - Choose: Elevator, Arm, Flywheel, or Turret
   - Enter physical limits (min/max position, velocity, acceleration)

↓

2. Algorithm Selection
   - Choose tuning method (with safety warnings)
   - Review algorithm-specific dangers

↓

3. OpMode Generation
   - Generate NextFTC tuning OpMode
   - Includes @Configurable parameters
   - Built-in safety limits and telemetry

↓

4. Deployment
   - Build and install via /deploy
   - Verify Panels connection
   - Check battery voltage (>12V)

↓

5. Safety Confirmation
   - Position robot safely
   - Review checklist (obstacles, emergency stop, etc.)
   - Explicit "ready" confirmation required

↓

6. Tuning Iterations
   - Init and start OpMode
   - Capture telemetry (Panels WebSocket + logcat fallback)
   - Analyze response with selected algorithm
   - Calculate new gains
   - Display proposed changes
   - User approval: Continue / Revert / Accept / Abort

↓

7. Finalization
    - Apply final parameters:
      * Sloth Load + Panels: Hot-reload code
      * Sloth Load only: Hot-reload code (no @Configurable needed)
      * Panels only: Update configurables
      * Neither: Display for manual entry (offer Panels install)
   - Optional verification run
```

## Safety Architecture

### Pre-Flight Checks
- Battery voltage monitoring (warn <12V, abort <11.5V)
- ADB connection validation
- Panels connectivity verification (with fallback to logcat)
- User acknowledgment of mechanism-specific risks

### Generated OpMode Safety Features
```kotlin
// Hard position limits
if (position < MIN || position > MAX) {
    motor.power = 0.0
    telemetry.addData("ERROR", "LIMIT EXCEEDED")
    requestOpModeStop()
}

// Timeout protection
if (runtime.seconds() > TEST_DURATION + 5) {
    requestOpModeStop()
}

// Velocity limiting
val targetVelocity = targetVelocity.coerceIn(-MAX_VEL, MAX_VEL)
```

### Human-in-the-Loop Control
- **Explicit approval** required before EVERY test run
- **Real-time telemetry** displayed during runs
- **Emergency abort**: Ctrl+C stops script, can `/stop` OpMode manually
- **Conservative initialization**: First run uses very low gains (minimal movement)

## Example Usage

```bash
/tune-controller

# Select mechanism type:
# 1. Elevator/Lift
# 2. Arm/Pivot
# 3. Flywheel/Shooter
# 4. Turret
> 1

# Enter physical limits:
Min position (ticks): 0
Max position (ticks): 2000
Max velocity (ticks/sec): 1500
Max acceleration (ticks/sec²): 3000

# Select tuning algorithm:
# [1] Step Response (SAFE)
# [2] Ziegler-Nichols (MEDIUM RISK)
# [3] Relay Feedback (HIGHER RISK)
# [4] Optimization (MEDIUM RISK, TIME INTENSIVE)
> 1

# Library Detection: NextFTC detected ✓
# Generated: ElevatorTuningOpMode.kt (with voltage regularization)
# Deploying... ✓
# Battery: 12.4V (nominal: 12V) ✓
# Panels: Connected ✓

# SAFETY CHECKLIST:
#   ☐ Elevator at safe mid-height position
#   ☐ No obstacles above/below
#   ☐ Emergency stop accessible
#   ☐ Someone monitoring robot

Ready? (yes/no): yes

# Tuning run 1/5...
#   kP=0.001, kD=0.0, kG=0.0
#   [telemetry streaming]
#   Analysis: kG=0.15 needed
#   Proposed: kP=0.001, kD=0.0, kG=0.15

Continue? (c/r/a/q): c

# [Iterations continue...]

# TUNING COMPLETE!
# Final: kP=0.004, kD=0.0002, kG=0.15
#
# Applying via Sloth Load... ✓
# Updated: TuningConfig.kt
```

## Implementation Details

This command coordinates multiple scripts across robot-dev and control-engineer skills:

**robot-dev/scripts/**:
- `opmode_generator.py` - Generate mechanism-specific tuning OpModes
- `config_updater.py` - Update Panels configurables via WebSocket
- `tuning_orchestrator.py` - Main workflow coordinator (called by this command)

**control-engineer/scripts/**:
- `telemetry_recorder.py` - Capture telemetry (Panels + logcat fallback)
- `tuning_algorithms.py` - Step response, Ziegler-Nichols, relay feedback, scipy optimization

## When the Command is Invoked

Execute the tuning orchestrator script:

```bash
cd plugins/robot-dev/scripts
uv run tuning_orchestrator.py
```

The orchestrator will:
1. Present interactive prompts (using Python `input()`)
2. Call `opmode_generator.py` to create the tuning OpMode
3. Execute robot-dev commands (`/deploy`, `/init`, `/start`, `/stop`)
4. Call control-engineer scripts for telemetry and analysis
5. Update parameters via Sloth Load or Panels
6. Display results and final recommendations

## Troubleshooting

**"Cannot connect to Panels"**
- Solution: Falls back to logcat telemetry capture automatically
- Verify robot is powered on and you're on robot WiFi (192.168.43.x)

**"Battery voltage too low"**
- Solution: Charge battery >12V before tuning
- Low voltage causes inconsistent motor behavior

**"OpMode not found after deploy"**
- Solution: Check build.gradle has NextFTC control dependency
- Verify TeamCode module builds successfully

**"Gains are unstable/oscillating"**
- Solution: Choose "Step Response" algorithm for more conservative gains
- Reduce kP by 50% and add small kD (kP/10)

**"Mechanism hits limits during tuning"**
- Solution: Generated OpMode includes safety stops
- OpMode will emergency-stop and log error
- Review and adjust physical limits in setup phase

## Tips

1. **Start Safe**: Always use Step Response for first-time tuning
2. **Secure Mechanism**: Ensure mechanism can't damage itself or surroundings
3. **Monitor Telemetry**: Watch real-time position/velocity/power during runs
4. **Battery Matters**: Voltage affects motor behavior - tune with fresh battery
5. **Iterate if Needed**: Can re-run `/tune-controller` to refine gains
6. **Document Gains**: Final gains are saved to JSON file for future reference

## Related Documentation

- Control-engineer skill: [AUTONOMOUS_TUNING.md](../skills/control-engineer/AUTONOMOUS_TUNING.md) - Detailed tuning guide
- Control-engineer skill: [TUNING_GUIDE.md](../skills/control-engineer/TUNING_GUIDE.md) - Manual tuning reference
- Robot-dev skill commands: `/deploy`, `/init`, `/start`, `/stop`, `/log`

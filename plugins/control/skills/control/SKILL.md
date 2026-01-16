---
name: control
description: >-
  Design, implement, tune, and debug control systems for FTC robot mechanisms.
  Use when implementing PID controllers, tuning PID gains, adding feedforward
  control (kG for elevators, kG*cos(θ) for arms, kV for flywheels), choosing
  between PID/feedforward/state-space control, performing system identification
  (sysid), identifying physical parameters (inertia, damping, friction, time
  constant, gain), calculating optimal gains via pole placement or Ziegler-Nichols,
  validating identified models, creating custom transfer functions, or diagnosing
  control problems: motor not moving, not reaching target, oscillating, overshooting,
  steady-state error, drifting, jittering, poor tracking, slow response. Also use
  for elevator control, lift control, arm control, pivot control, flywheel control,
  shooter control, turret control, horizontal slide control, motion profiling,
  state-space control, LQR, Kalman filters, or reviewing control code for
  improvements. Supports NextFTC, FTCLib, Plain FTC SDK, RoadRunner, and Pedro Pathing.
license: MIT
metadata:
  author: ncssm-robotics
  version: "2.2.0"
  category: tools
---

# Control System Implementation for FTC

Guidance for implementing PID controllers and feedforward for FTC robot mechanisms.

## Library Detection

**Check your `build.gradle` (TeamCode) first:**

| Library | Search For | Control System Available |
|---------|------------|-------------------------|
| **NextFTC** | `dev.nextftc:control` | Full `ControlSystem.builder()` with PID, FF, filters |
| **FTCLib** | `com.arcrobotics.ftclib` | `PIDController`, `MotorEx` with built-in PID |
| **RoadRunner** | `com.acmerobotics.roadrunner` | Drivetrain feedforward and path following |
| **Pedro Pathing** | `pedroPathing` | Path following with built-in PIDs |
| **Plain FTC SDK** | (always available) | Manual implementation required |

**Quick Decision:**
- **NextFTC**: Use `ControlSystem.builder()` - see [LIBRARY_REFERENCE.md](LIBRARY_REFERENCE.md)
- **FTCLib**: Use `PIDController` class - see [LIBRARY_REFERENCE.md](LIBRARY_REFERENCE.md)
- **RoadRunner/Pedro**: Drivetrain handled; use this skill for other mechanisms
- **Plain SDK**: This skill guides manual implementation

## Quick Reference: Choose Your Controller

| Mechanism | Controller | Feedforward |
|-----------|-----------|-------------|
| **Elevator/Lift** | Position PID | `kG` (constant) |
| **Arm/Pivot** | Position PID | `kG * cos(angle)` |
| **Flywheel/Shooter** | Velocity PID | `kV * velocity` |
| **Turret** | Position PID | None |
| **Horizontal Slide** | Position PID | `kS * sign(velocity)` |
| **Intake** | Bang-bang or none | None |
| **Drivetrain** | **Use RoadRunner/Pedro** | (handled internally) |

## When NOT to Use This Skill

- ❌ **Drivetrain path following** → Use `pedro-pathing` or `roadrunner` skills instead - they handle all control internally
- ❌ **Simple on/off mechanisms** → Intakes, claws, and other binary mechanisms don't need control systems - just set power to 0 or 1
- ❌ **Mechanisms already working well** → If your elevator/arm is stable and accurate, don't over-tune it
- ❌ **Library-specific syntax questions** → Check `nextftc` or library documentation for API usage
- ❌ **When you just need code to copy** → This skill teaches concepts; use it to understand WHY, not just copy/paste

**Use this skill for:**
- ✅ Tuning PID gains for elevators, arms, flywheels, and other mechanisms
- ✅ Understanding why your mechanism oscillates, overshoots, or has steady-state error
- ✅ Choosing the right control approach for a new mechanism
- ✅ Implementing feedforward for gravity or velocity compensation
- ✅ Diagnosing control problems and improving existing implementations

## Autonomous Tuning

**Want to automate tuning?** The `/tune-controller` command provides fully autonomous PID and feedforward tuning:

- Generates test OpModes automatically (NextFTC/FTCLib/Plain SDK)
- Runs experiments and captures telemetry (Panels WebSocket or logcat)
- Analyzes data with multiple algorithms (step response, Ziegler-Nichols, relay feedback, scipy)
- Tunes parameters in real-time (Panels configurables, Sloth Load hot-reload, or manual entry)
- Includes voltage regularization (compensates for battery variations, nominal 12V)

**Quick Example:**

```bash
/tune-controller

# System detects libraries → select mechanism → choose algorithm
# Deploys OpMode → runs tests → tunes gains
# Result: kP=0.004, kD=0.0002, kG=0.15 in 8 minutes
```

**Prerequisites:**
- `robot-dev` skill (for `/deploy`, `/init`, `/start`)
- `panels` or `sloth-load` skill (for parameter updates)

See [AUTONOMOUS_TUNING.md](AUTONOMOUS_TUNING.md) for the complete guide.

## Documentation Guide

| Document | When to Use |
|----------|-------------|
| **SKILL.md** (this file) | Quick start, common patterns, basic implementation |
| [MECHANISMS.md](MECHANISMS.md) | Complete examples for elevator, arm, flywheel, turret |
| [TUNING_GUIDE.md](TUNING_GUIDE.md) | Step-by-step empirical tuning without sysid |
| [SYSTEM_IDENTIFICATION.md](SYSTEM_IDENTIFICATION.md) | Physics-based automated parameter identification |
| [MODEL_SELECTION.md](MODEL_SELECTION.md) | Choose model structure before running sysid |
| [CUSTOM_MODELS.md](CUSTOM_MODELS.md) | Define custom transfer functions for novel mechanisms |
| [DIAGNOSTICS.md](DIAGNOSTICS.md) | Troubleshooting oscillation, overshoot, tracking errors |
| [LIBRARY_REFERENCE.md](LIBRARY_REFERENCE.md) | NextFTC vs FTCLib vs Plain SDK syntax |
| [ADVANCED_CONTROL.md](ADVANCED_CONTROL.md) | State-space, LQR, Kalman filters |
| [AUTONOMOUS_TUNING.md](AUTONOMOUS_TUNING.md) | `/tune-controller` command guide |

## Implementation Patterns

### Pattern 1: Elevator with Gravity Compensation

```java
// Plain FTC SDK implementation
public class ElevatorController {
    // kG: Power needed to counteract gravity when stationary
    // Find by: Raise elevator to mid-height, increase power until it holds position
    private double kG = 0.15;

    // kP: Proportional gain for position error
    // Tune after kG: Start at 0.001, double until oscillation, then reduce to 60-70%
    private double kP = 0.005;

    public double calculate(double currentPos, double targetPos) {
        double error = targetPos - currentPos;
        double pidOutput = kP * error;
        double gravityFF = kG;  // Constant - gravity doesn't change with position
        return pidOutput + gravityFF;
    }
}
```

```kotlin
// NextFTC implementation (if available)
val controller = ControlSystem.builder()
    .posPid(kP = 0.005, kI = 0.0, kD = 0.001)
    .elevatorFF(kG = 0.15)
    .build()
```

### Pattern 2: Arm with Angle-Dependent Gravity

```java
// Plain FTC SDK implementation
public class ArmController {
    // kG: Power needed to hold arm at horizontal (90° from vertical)
    // Find by: Move arm to horizontal, increase power until it holds, that's your kG
    // cos(angle) scales this: horizontal=max load, vertical=no load
    private double kG = 0.3;

    // kP: Proportional gain for position error
    // Tune after kG: Start small (0.001), increase until responsive without oscillation
    private double kP = 0.01;

    // Encoder resolution: depends on motor (e.g., 28 counts/rev) and gearing
    // Calculate: ticks_per_rev * gear_ratio / (2 * PI) = ticks per radian
    private double ticksPerRadian = 1000.0;

    public double calculate(double currentTicks, double targetTicks) {
        double error = targetTicks - currentTicks;
        double pidOutput = kP * error;

        // Convert to radians (0 = horizontal, pi/2 = vertical up)
        double angleRad = currentTicks / ticksPerRadian;
        // Gravity torque varies with angle: max at horizontal, zero at vertical
        double gravityFF = kG * Math.cos(angleRad);

        return pidOutput + gravityFF;
    }
}
```

```kotlin
// NextFTC implementation
val controller = ControlSystem.builder()
    .posPid(kP = 0.01, kI = 0.0, kD = 0.002)
    .armFF(kG = 0.3)
    .build()
```

### Pattern 3: Flywheel Velocity Control

```java
// Plain FTC SDK implementation
public class FlywheelController {
    // kV: Power required per unit of velocity (accounts for friction/air resistance)
    // Find by: Apply known power, measure velocity at steady state, kV = power / velocity
    // Example: 0.5 power → 3000 ticks/sec → kV = 0.5/3000 = 0.00016
    private double kV = 0.00015;

    // kP: Proportional gain for velocity error
    // Tune after kV: Start very small (0.00001), increase until recovery is fast
    // Flywheels need small kP since kV does most of the work
    private double kP = 0.0001;

    public double calculate(double currentVel, double targetVel) {
        double error = targetVel - currentVel;
        double pidOutput = kP * error;
        // Feedforward: power needed to maintain target velocity (not fight error)
        double velocityFF = kV * targetVel;
        return pidOutput + velocityFF;
    }
}
```

### Pattern 4: Simple Position Control (Turret)

```java
// Plain FTC SDK implementation
public class TurretController {
    // kP: Proportional gain for position error
    // Horizontal mechanisms often don't need feedforward (no gravity/friction)
    // Tune: Start at 0.001, increase until responsive
    private double kP = 0.005;

    // kD: Derivative gain to dampen oscillation and overshoot
    // Add if kP alone causes oscillation
    // Tune: Start at kP/10, increase until smooth, reduce if jittery
    private double kD = 0.001;

    private double lastError = 0;

    public double calculate(double currentPos, double targetPos) {
        double error = targetPos - currentPos;
        // Derivative: rate of change of error (how fast we're approaching target)
        // Opposes rapid changes, provides damping
        double derivative = error - lastError;
        lastError = error;
        return kP * error + kD * derivative;
    }
}
```

For complete mechanism examples, see [MECHANISMS.md](MECHANISMS.md).

## Common Mistakes & Examples

### Good: Elevator with Feedforward First

```java
public class ElevatorController {
    // Start with feedforward to do most of the work
    private double kG = 0.15;   // Found by: lift to mid-height, increase power until holds
    private double kP = 0.005;  // Added after kG to handle positioning

    public double calculate(double currentPos, double targetPos) {
        double error = targetPos - currentPos;
        double pidOutput = kP * error;
        double gravityFF = kG;  // Always fighting gravity
        return pidOutput + gravityFF;
    }
}
```

**Why it works:** Feedforward (kG) does 90% of the work holding against gravity. PID only corrects the remaining error.

### Bad: Elevator with Only PID (No Feedforward)

```java
// ❌ Missing gravity compensation
public class ElevatorController {
    private double kP = 0.05;   // Had to crank this way up!
    private double kI = 0.001;  // Added I to fight steady-state error

    public double calculate(double currentPos, double targetPos) {
        double error = targetPos - currentPos;
        return kP * error;  // PID is fighting gravity AND positioning
    }
}
```

**Why it fails:** PID has to do ALL the work. Requires huge kP, still has steady-state error, and oscillates badly.

### Good: Arm with Angle-Dependent Gravity

```java
public class ArmController {
    private double kP = 0.01;
    private double kG = 0.3;    // Power at horizontal position
    private double ticksPerRadian = 1000.0;

    public double calculate(double currentTicks, double targetTicks) {
        double error = targetTicks - currentTicks;
        double pidOutput = kP * error;

        // Convert to radians (0 = horizontal, pi/2 = vertical up)
        double angleRad = currentTicks / ticksPerRadian;
        double gravityFF = kG * Math.cos(angleRad);  // Varies with angle

        return pidOutput + gravityFF;
    }
}
```

**Why it works:** Gravity compensation changes with arm angle. When vertical, cos(90°)=0 (no gravity load). When horizontal, cos(0°)=1 (max gravity load).

### Bad: Arm with Constant Gravity

```java
// ❌ Treating arm like an elevator
public class ArmController {
    private double kP = 0.01;
    private double kG = 0.3;    // Constant gravity compensation

    public double calculate(double currentTicks, double targetTicks) {
        double error = targetTicks - currentTicks;
        return kP * error + kG;  // Wrong! Gravity varies with angle
    }
}
```

**Why it fails:** When arm is vertical, constant kG pushes it too far. When horizontal, not enough compensation. Unstable at all positions.

### Good: Proper Unit Handling

```java
public class ArmController {
    // All constants calibrated in encoder ticks
    private double kP = 0.01;           // Per tick error
    private double kG = 0.3;            // Power at horizontal
    private double ticksPerDegree = 28 * 5.2 * 3 / 360.0;  // Documented calculation

    public double calculate(double currentTicks, double targetTicks) {
        double error = targetTicks - currentTicks;  // In ticks
        double angleRad = (currentTicks / ticksPerDegree) * Math.PI / 180.0;
        return kP * error + kG * Math.cos(angleRad);
    }
}
```

**Why it works:** Units are consistent. Error in ticks, kP calibrated for ticks, angle conversion clearly documented.

### Bad: Mixed Units

```java
// ❌ Mixing degrees and ticks without conversion
public class ArmController {
    private double kP = 0.01;           // Calibrated for ticks
    private double kG = 0.3;

    public double calculate(double currentTicks, double targetDegrees) {  // ❌ Mixed units!
        double error = targetDegrees - currentTicks;  // Comparing apples to oranges
        double angleRad = currentTicks * Math.PI / 180.0;  // ❌ Assumes ticks = degrees
        return kP * error + kG * Math.cos(angleRad);
    }
}
```

**Why it fails:** Comparing degrees to ticks gives nonsense error values. kP is meaningless. Angle calculation is wrong.

## Tuning Process

**Rule**: Tune feedforward FIRST, then PID.

### Step 1: Find Feedforward Constants

**For Elevators (kG):**
1. Set all PID gains to 0
2. Raise elevator to mid-height manually
3. Slowly increase constant power until it holds position
4. That power value is your `kG`

**For Arms (kG):**
1. Set all PID gains to 0
2. Move arm to horizontal (90 degrees from vertical)
3. Find power to hold at horizontal
4. That value is your `kG` (will be multiplied by cos internally)

**For Flywheels (kV):**
1. Set all PID gains to 0
2. Apply known power, measure resulting velocity
3. `kV = power / velocity`

### Step 2: Add P Gain

1. Start with very small kP (0.001 for position, 0.0001 for velocity)
2. Double until you see oscillation
3. Back off to 60-70% of oscillating value

### Step 3: Add D Gain (if needed)

1. If still oscillating after P tuning, add small kD
2. Increase until oscillation stops
3. Too much D causes jitter on noisy sensors

### Step 4: Add I Gain (rarely needed)

1. **Only** if there's persistent steady-state error AND feedforward is correct
2. Start very small (kI = kP / 100)
3. Too much I causes overshoot and windup

For detailed tuning methodology, see [TUNING_GUIDE.md](TUNING_GUIDE.md).

## Common Problems and Solutions

| Problem | Likely Cause | Solution |
|---------|--------------|----------|
| Oscillation | P too high | Reduce P, add D |
| Slow response | P too low | Increase P |
| Overshoot | P too high, no D | Add D, reduce P |
| Won't hold position | Missing feedforward | Add kG for gravity systems |
| Steady-state error | No FF or I too low | Add feedforward first, then small I |
| Jitter/noise | D too high | Reduce D, add sensor filter |
| Drifts over time | Integrator windup | Add integral limits, check mechanical |

For detailed troubleshooting, see [DIAGNOSTICS.md](DIAGNOSTICS.md).

## Anti-Patterns

- ❌ **Starting with PID before feedforward** - FF should do 90% of the work
- ❌ **Using drivetrain gains for mechanisms** - Different physics require different tuning
- ❌ **Copying gains from other robots** - Physical properties differ; always tune your own
- ❌ **Adding I gain first** - I causes instability; use only for steady-state error
- ❌ **Reinventing path following** - Use RoadRunner or Pedro instead
- ❌ **Over-engineering simple mechanisms** - An intake doesn't need state-space control
- ❌ **Ignoring units** - Encoder ticks vs inches vs radians matters for gain values
- ❌ **Deploying model-based gains without validation** - Always check R² > 0.85
- ❌ **Using sysid with noisy data** - Garbage in, garbage out
- ❌ **Ignoring confidence intervals** - Low confidence → use empirical tuning

## Advanced: System Identification (Physics-Based Tuning)

System identification (sysid) identifies physical parameters (inertia, damping, gravity) from test data and calculates optimal PID gains.

**When to Use:**
- Understanding system physics → SysID
- Optimal performance → SysID + refinement
- Quick competition tuning → Empirical (step response)
- Limited test time → Empirical

**Workflow:**
```bash
uv run scripts/select_model.py --mechanism elevator --quick
uv run scripts/identify_params.py --data sysid_data.json --auto-select
uv run scripts/validate_model.py --model identified_model.json
uv run scripts/calculate_gains.py --model identified_model.json --rise-time 1.0
```

**Output:** Physical parameters (J, b, kg, τ), mathematically optimal gains, predicted performance (R² > 0.85).

**Model Library:** 6 built-in types (first-order, first-order+gravity, second-order, angle-dependent, friction, variable-inertia) + custom models via JSON.

**See:** [SYSTEM_IDENTIFICATION.md](SYSTEM_IDENTIFICATION.md) for complete guide, [MODEL_SELECTION.md](MODEL_SELECTION.md) for choosing models, [CUSTOM_MODELS.md](CUSTOM_MODELS.md) for custom transfer functions.

## Utilities

All scripts support `--help` for detailed options:

```bash
# System identification workflow
uv run scripts/select_model.py --help
uv run scripts/identify_params.py --help
uv run scripts/validate_model.py --help
uv run scripts/calculate_gains.py --help

# List available model structures
uv run scripts/select_model.py --list-models

# Compare multiple tuning runs
uv run scripts/compare_runs.py run1.json run2.json run3.json
```

## Reference Documentation

- [SYSTEM_IDENTIFICATION.md](SYSTEM_IDENTIFICATION.md) - Complete sysid guide (NEW)
  - Physics background (transfer functions, pole placement)
  - Data collection best practices
  - Identification methods (least-squares, frequency response)
  - Model validation techniques
  - Troubleshooting poor fits

- [MODEL_SELECTION.md](MODEL_SELECTION.md) - Choosing the right model structure (NEW)
  - 6-model library with decision matrix
  - Interactive selection process
  - Complexity vs accuracy trade-offs
  - Troubleshooting model selection

- [MECHANISMS.md](MECHANISMS.md) - Complete mechanism examples with code
- [TUNING_GUIDE.md](TUNING_GUIDE.md) - Detailed step-by-step tuning methodology
- [LIBRARY_REFERENCE.md](LIBRARY_REFERENCE.md) - Library-specific syntax (NextFTC/FTCLib/SDK)
- [DIAGNOSTICS.md](DIAGNOSTICS.md) - Troubleshooting and code review checklists
- [ADVANCED_CONTROL.md](ADVANCED_CONTROL.md) - State-space, LQR, Kalman filters
- [AUTONOMOUS_TUNING.md](AUTONOMOUS_TUNING.md) - Automated tuning guide

## External Resources

- [CTRL ALT FTC](https://www.ctrlaltftc.com/) - Comprehensive control theory for FTC
- [Game Manual 0 - Control Loops](https://gm0.org/en/latest/docs/software/concepts/control-loops.html)
- [WPILib Control System Basics](https://docs.wpilib.org/en/stable/docs/software/advanced-controls/introduction/index.html)

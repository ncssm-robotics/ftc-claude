---
name: control-engineer
description: >-
  Helps design, implement, debug, and improve control systems for FTC robot mechanisms.
  Use when tuning PID, implementing feedforward, choosing between control methods,
  implementing elevator/lift control, arm/pivot control, flywheel/shooter control,
  drivetrain control, motion profiling, sensor filtering, state-space control,
  LQR, Kalman filters, or when asking "what control approach should I use?"
  Also use when diagnosing control problems: motor not moving, not reaching target,
  oscillating, overshooting, drifting, jittering, or when reviewing existing control
  code for improvements and best practices.
license: MIT
compatibility: Claude Code, Codex CLI, VS Code Copilot, Cursor
metadata:
  author: ncssm-robotics
  version: "1.0.0"
  category: library
---

# Control Engineer

A decision-making guide for choosing and implementing control systems in FTC. This skill helps you pick the RIGHT control approach for your mechanism, understand the physics, and implement it correctly.

## First: Check Your Existing Libraries

**IMPORTANT:** Before implementing new controllers, check what libraries your project already has.

### Library Detection Checklist

Search your `build.gradle` (TeamCode) for these dependencies:

| Library | Search For | Control System Available |
|---------|------------|-------------------------|
| **NextFTC** | `dev.nextftc:control` | Full `ControlSystem.builder()` with PID, FF, filters |
| **FTCLib** | `com.arcrobotics.ftclib` | `PIDController`, `MotorEx` with built-in PID |
| **RoadRunner** | `com.acmerobotics.roadrunner` | Drivetrain feedforward and path following |
| **Pedro Pathing** | `pedroPathing` | Path following with built-in PIDs |
| **Plain FTC SDK** | (always available) | Manual implementation required |

### Quick Decision: Use Existing or Build New?

- **NextFTC users**: Use `ControlSystem.builder()` - see [LIBRARY_REFERENCE.md](LIBRARY_REFERENCE.md)
- **FTCLib users**: Use `PIDController` class - see [LIBRARY_REFERENCE.md](LIBRARY_REFERENCE.md)
- **RoadRunner/Pedro users**: Drivetrain is handled; use this skill for other mechanisms
- **Plain SDK**: This skill guides manual implementation

## Quick Start: What Are You Controlling?

> **Before we begin:** Do you need simple or advanced control methods?
> - **Simple** (recommended for most teams): PID, feedforward, motion profiling
> - **Advanced**: State-space, LQR, observers, Kalman filters
>
> For advanced methods, see [ADVANCED_CONTROL.md](ADVANCED_CONTROL.md).

| Mechanism | Primary Challenge | Recommended Approach | FF Type |
|-----------|------------------|---------------------|---------|
| **Elevator/Lift** | Constant gravity | Position PID + Gravity FF | `kG` constant |
| **Arm/Pivot** | Angle-dependent gravity | Position PID + Arm FF | `kG * cos(angle)` |
| **Flywheel/Shooter** | Velocity accuracy | Velocity PID + Velocity FF | `kV * velocity` |
| **Turret** | Position accuracy | Position PID only | None needed |
| **Drivetrain** | Path following | Use RoadRunner/Pedro | (handled internally) |

## Autonomous Tuning (NEW!)

**Want to automate the entire tuning process?** The `/tune-controller` command provides fully autonomous PID and feedforward tuning:

- **Generates test OpModes automatically** - Uses your existing libraries (NextFTC, FTCLib, or Plain SDK)
- **Runs experiments and captures telemetry** - Via Panels WebSocket or logcat
- **Analyzes data with multiple algorithms** - Step response, Ziegler-Nichols, relay feedback, scipy optimization
- **Tunes parameters in real-time** - Via Panels configurables (unless using Sloth Load), Sloth Load hot-reload, or manual entry
- **Includes voltage regularization** - Compensates for battery voltage variations (nominal: 12V)

### Quick Example

```bash
/tune-controller

# System detects your libraries (NextFTC/FTCLib/SDK)
# Select: Elevator, enter limits, choose "Step Response"
# System generates OpMode with voltage regularization (12V nominal)
# Deploys, runs tests, tunes gains with voltage compensation
# Result: kP=0.004, kD=0.0002, kG=0.15 in 8 minutes
```

### Prerequisites

- `robot-dev` skill (for `/deploy`, `/init`, `/start` commands)
- `panels` or `sloth-load` skill (for parameter updates)
- Library detection (NextFTC, FTCLib, or Plain SDK) for OpMode generation

### When to Use Autonomous Tuning

**Use autonomous tuning for:**
- First-time tuning of new mechanisms
- Quick iteration on existing gains
- Learning what good gains look like
- Mechanisms where manual tuning is tedious

**Use manual tuning for:**
- Fine-tuning already-good gains
- Understanding control theory deeply
- Mechanisms with complex dynamics
- When you have limited robot access

See [AUTONOMOUS_TUNING.md](AUTONOMOUS_TUNING.md) for the complete guide.

## Control Method Selection

### Master Decision Tree

```
START: What are you controlling?
  │
  ├─ Drivetrain/chassis?
  │   └─ YES → Use RoadRunner or Pedro Pathing (STOP - don't reinvent)
  │
  ├─ Does it fight gravity?
  │   ├─ YES, linear vertical (elevator/lift)
  │   │   └─ Position PID + elevatorFF(kG)
  │   │
  │   └─ YES, rotational (arm/pivot)
  │       └─ Position PID + armFF(kG) with cos(angle)
  │
  ├─ Is it velocity control (flywheel/shooter)?
  │   └─ YES → Velocity PID + basicFF(kV)
  │
  └─ Is it pure position (turret, intake pivot)?
      └─ YES → Position PID only (no feedforward needed)
```

For detailed decision trees, see [DECISION_TREES.md](DECISION_TREES.md).

## Understanding Feedforward vs Feedback

**Feedforward (FF)**: Predicts the power needed based on physics. Does 80-90% of the work.

**Feedback (PID)**: Corrects for errors. Handles the remaining 10-20%.

**Key insight**: Always tune feedforward FIRST. If you start with PID, you're doing it wrong.

### Feedforward Types

| Type | Formula | When to Use | Physical Meaning |
|------|---------|-------------|------------------|
| **kV** | `kV * velocity` | Flywheels, drivetrains | Power per unit velocity |
| **kS** | `kS * sign(velocity)` | Any moving system | Overcome static friction |
| **kA** | `kA * acceleration` | Fast-moving systems | Power for acceleration |
| **kG (elevator)** | `kG` (constant) | Vertical linear | Hold against gravity |
| **kG (arm)** | `kG * cos(angle)` | Rotational | Gravity varies with angle |

## Implementation Patterns

### Pattern 1: Elevator with Gravity Compensation

**The physics**: Gravity pulls down constantly. You need power just to hold position.

```java
// Plain FTC SDK implementation
public class ElevatorController {
    private double kP = 0.005;   // Tune this
    private double kG = 0.15;   // Power to hold against gravity

    public double calculate(double currentPos, double targetPos) {
        double error = targetPos - currentPos;
        double pidOutput = kP * error;
        double gravityFF = kG;  // Always fighting gravity (up is positive)
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

**The physics**: Gravity torque varies with angle. Maximum when horizontal, zero when vertical.

```java
// Plain FTC SDK implementation
public class ArmController {
    private double kP = 0.01;
    private double kG = 0.3;    // Power at horizontal position
    private double ticksPerRadian = 1000.0;  // Your encoder conversion

    public double calculate(double currentTicks, double targetTicks) {
        double error = targetTicks - currentTicks;
        double pidOutput = kP * error;

        // Convert to radians (0 = horizontal, pi/2 = vertical up)
        double angleRad = currentTicks / ticksPerRadian;
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

**The physics**: Need power proportional to velocity (kV) plus PID correction.

```java
// Plain FTC SDK implementation
public class FlywheelController {
    private double kP = 0.0001;
    private double kV = 0.00015;  // Power per tick/second

    public double calculate(double currentVel, double targetVel) {
        double error = targetVel - currentVel;
        double pidOutput = kP * error;
        double velocityFF = kV * targetVel;  // Base power for target speed
        return pidOutput + velocityFF;
    }
}
```

### Pattern 4: Simple Position Control (Turret)

**The physics**: No gravity to fight, just position error.

```java
// Plain FTC SDK implementation
public class TurretController {
    private double kP = 0.005;
    private double kD = 0.001;
    private double lastError = 0;

    public double calculate(double currentPos, double targetPos) {
        double error = targetPos - currentPos;
        double derivative = error - lastError;
        lastError = error;
        return kP * error + kD * derivative;
    }
}
```

For complete mechanism examples, see [MECHANISMS.md](MECHANISMS.md).

## Tuning Process

**Golden Rule**: Tune feedforward FIRST, then PID.

### Step 1: Find Feedforward Constants

#### For Elevators (kG)
1. Set all PID gains to 0
2. Raise elevator to mid-height manually
3. Slowly increase constant power until it holds position
4. That power value is your `kG`

#### For Arms (kG)
1. Set all PID gains to 0
2. Move arm to horizontal (90 degrees from vertical)
3. Find power to hold at horizontal
4. That value is your `kG` (will be multiplied by cos internally)

#### For Flywheels (kV)
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
| Drifts over time | Integrator windup | Add integral limits, check for mechanical issues |

For detailed troubleshooting, see [DIAGNOSTICS.md](DIAGNOSTICS.md).

## Diagnosing Control Problems

### Quick Diagnosis Flowchart

```
SYMPTOM: What's happening?
  │
  ├─ Motor doesn't move at all
  │   → Check: output reaching motor? gains too low? wrong error sign?
  │
  ├─ Doesn't reach target (steady-state error)
  │   → Check: missing feedforward? kG/kV tuned? friction compensation?
  │
  ├─ Oscillates around target
  │   → Check: kP too high? add kD? kI causing windup?
  │
  ├─ Overshoots then corrects
  │   → Check: kP too high? add kD? too much velocity?
  │
  ├─ Drifts slowly over time
  │   → Check: encoder issues? mechanical slip? wrong FF direction?
  │
  └─ Jittery / noisy output
      → Check: kD too high? sensor needs filtering?
```

### Code Review Checklist

When reviewing existing control code, look for:

**Structure Issues**
- [ ] Motor set to BRAKE mode for position control
- [ ] Output clamped to [-1, 1]
- [ ] Integral has anti-windup limits
- [ ] Position limits enforced

**Control Design Issues**
- [ ] Feedforward used for gravity/velocity systems
- [ ] Error calculated as `target - current` (not reversed)
- [ ] kI only used if steady-state error exists
- [ ] Loop timing accounted for in derivative

**Common Code Smells**
```java
// RED FLAG: PID without feedforward on gravity system
output = kP * error;  // Where's the kG?

// RED FLAG: Integral without limits
integral += error;  // Will wind up!

// RED FLAG: Wrong error direction
error = current - target;  // Should be target - current!
```

For complete diagnostic procedures, see [DIAGNOSTICS.md](DIAGNOSTICS.md).

## Anti-Patterns

- **Starting with PID before feedforward** - FF should do 90% of the work
- **Using drivetrain gains for mechanisms** - Different physics require different tuning
- **Copying gains from other robots** - Physical properties differ; always tune your own
- **Adding I gain first** - I causes instability; use only for steady-state error
- **Reinventing path following** - Use RoadRunner or Pedro instead
- **Over-engineering simple mechanisms** - An intake doesn't need state-space control
- **Ignoring units** - Encoder ticks vs inches vs radians matters for gain values

## When to Use Advanced Control

Consider advanced methods ([ADVANCED_CONTROL.md](ADVANCED_CONTROL.md)) when:

- Simple PID+FF gives >10% steady-state error after proper tuning
- Mechanism has multiple coupled degrees of freedom
- You need optimal performance (state competitions, worlds)
- You have a controls mentor to help debug
- You've maxed out what PID+FF can do

**Most FTC teams don't need advanced control.** Get PID+FF working well first.

## Reference Documentation

- [DECISION_TREES.md](DECISION_TREES.md) - Visual decision flowcharts
- [MECHANISMS.md](MECHANISMS.md) - Complete mechanism examples
- [TUNING_GUIDE.md](TUNING_GUIDE.md) - Step-by-step tuning process
- [LIBRARY_REFERENCE.md](LIBRARY_REFERENCE.md) - Quick syntax for NextFTC/FTCLib/SDK
- [DIAGNOSTICS.md](DIAGNOSTICS.md) - Troubleshooting and code review
- [ADVANCED_CONTROL.md](ADVANCED_CONTROL.md) - State-space, LQR, Kalman filters

## External Resources

- [CTRL ALT FTC](https://www.ctrlaltftc.com/) - Comprehensive control theory for FTC
- [Game Manual 0 - Control Loops](https://gm0.org/en/latest/docs/software/concepts/control-loops.html)
- [WPILib Control System Basics](https://docs.wpilib.org/en/stable/docs/software/advanced-controls/introduction/index.html)

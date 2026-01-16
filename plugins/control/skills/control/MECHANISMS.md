# Mechanism-Specific Control

Complete implementation examples for common FTC mechanisms.

## Mechanism Overview

| Mechanism | Control Type | Feedforward | Key Parameter |
|-----------|-------------|-------------|---------------|
| Elevator | Position PID | kG (constant) | Gravity compensation |
| Arm | Position PID | kG * cos(θ) | Angle-dependent gravity |
| Flywheel | Velocity PID | kV * velocity | Velocity feedforward |
| Turret | Position PID | None | Simple positioning |

## Elevator/Lift

**Physics:** Constant gravity force at all positions.

```java
public class ElevatorController {
    private double kP = 0.005;
    private double kD = 0.001;
    private double kG = 0.15;  // Power to hold against gravity

    private double lastError = 0;
    private int targetPosition = 0;

    public void setTarget(int position) {
        targetPosition = Math.max(0, Math.min(3000, position));
    }

    public double calculate(int currentPosition) {
        double error = targetPosition - currentPosition;
        double derivative = error - lastError;
        lastError = error;

        double pidOutput = kP * error + kD * derivative;
        double feedforward = kG;

        return Math.max(-1.0, Math.min(1.0, pidOutput + feedforward));
    }
}
```

**Tuning kG:**
1. Set kP = 0
2. Raise elevator to mid-height
3. Increase power until it holds position
4. That value is kG

## Arm/Pivot

**Physics:** Gravity torque = kG * cos(angle). Maximum at horizontal, zero at vertical.

```java
public class ArmController {
    private double kP = 0.01;
    private double kD = 0.002;
    private double kG = 0.3;  // Power at horizontal

    // Encoder ticks per radian (calculate from gear ratio)
    private double ticksPerRadian = (28 * 50) / (2 * Math.PI);

    private double lastError = 0;
    private double targetAngle = 0;  // radians

    public double calculate(int currentTicks) {
        double currentAngle = currentTicks / ticksPerRadian;
        double error = targetAngle - currentAngle;
        double derivative = error - lastError;
        lastError = error;

        double pidOutput = kP * error + kD * derivative;
        double feedforward = kG * Math.cos(currentAngle);

        return Math.max(-1.0, Math.min(1.0, pidOutput + feedforward));
    }
}
```

**Tuning kG:**
1. Move arm to horizontal (0 radians)
2. Find power to hold position
3. That value is kG

## Flywheel/Shooter

**Physics:** Velocity control with friction compensation.

```java
public class FlywheelController {
    private double kP = 0.0001;
    private double kV = 0.00015;  // Power per velocity unit
    private double kS = 0.05;     // Static friction

    private double targetVelocity = 0;

    public double calculate(double currentVelocity) {
        if (targetVelocity == 0) return 0;

        double error = targetVelocity - currentVelocity;
        double pidOutput = kP * error;
        double feedforward = kV * targetVelocity + kS * Math.signum(targetVelocity);

        return Math.max(-1.0, Math.min(1.0, pidOutput + feedforward));
    }
}
```

**Tuning kV:**
1. Apply known power (e.g., 0.5)
2. Measure steady-state velocity
3. kV = power / velocity

## Turret

**Physics:** Horizontal rotation, no gravity compensation needed.

```java
public class TurretController {
    private double kP = 0.005;
    private double kD = 0.001;

    private double lastError = 0;

    public double calculate(int currentPosition, int targetPosition) {
        double error = targetPosition - currentPosition;
        double derivative = error - lastError;
        lastError = error;

        double output = kP * error + kD * derivative;
        return Math.max(-0.5, Math.min(0.5, output));  // Limit turret speed
    }
}
```

## NextFTC Examples

### Elevator
```kotlin
val controller = ControlSystem.builder()
    .posPid(kP = 0.005, kI = 0.0, kD = 0.001)
    .elevatorFF(kG = 0.15)
    .build()
```

### Arm
```kotlin
val controller = ControlSystem.builder()
    .posPid(kP = 0.01, kI = 0.0, kD = 0.002)
    .armFF(kG = 0.3)  // NextFTC handles cos(angle) internally
    .build()
```

### Flywheel
```kotlin
val controller = ControlSystem.builder()
    .velPid(kP = 0.0001, kI = 0.0, kD = 0.0)
    .basicFF(kV = 0.00015, kS = 0.05)
    .build()
```

## Drivetrain

**Use RoadRunner or Pedro Pathing.** These libraries handle:
- Odometry/localization
- Motion profiling
- Feedforward (kS, kV, kA)
- Path following

Only implement custom drivetrain control for:
- Simple teleop heading hold
- Point turns to angle

### Simple Heading Hold
```java
public double getHeadingCorrection(double currentHeading, double targetHeading) {
    double error = normalizeAngle(targetHeading - currentHeading);
    return 0.02 * error;  // Simple P control
}

private double normalizeAngle(double angle) {
    while (angle > Math.PI) angle -= 2 * Math.PI;
    while (angle < -Math.PI) angle += 2 * Math.PI;
    return angle;
}
```

## Setup Checklist

For all mechanisms:
- [ ] Motor set to BRAKE mode
- [ ] Encoder zero position defined
- [ ] Position/velocity limits set
- [ ] Feedforward tuned BEFORE PID
- [ ] Safety limits in code

## Typical Gain Ranges

| Mechanism | kP | kD | kG/kV |
|-----------|-----|-----|-------|
| Elevator | 0.001-0.01 | 0.0001-0.002 | 0.1-0.3 |
| Arm | 0.005-0.02 | 0.001-0.005 | 0.2-0.5 |
| Flywheel | 0.00005-0.0002 | 0 | 0.0001-0.0003 |
| Turret | 0.002-0.01 | 0.0005-0.002 | N/A |

**Start low and increase.** These are starting points - your mechanism will differ.

# Library Quick Reference

Quick syntax reference for implementing control systems in different FTC libraries. Each library below has dedicated skills to help you learn more:

- **[NextFTC Skill](../../../nextftc)** - Full framework with control systems, commands, subsystems
- **[RoadRunner Skill](../../../roadrunner)** - Path planning and drivetrain control
- **[Pedro Pathing Skill](../../../pedro-pathing)** - Alternative path following library

## Detecting Your Libraries

Check your `TeamCode/build.gradle` dependencies:

```gradle
dependencies {
    // NextFTC Control
    implementation 'dev.nextftc:control:1.0.0'

    // FTCLib
    implementation 'com.arcrobotics.ftclib:core:2.1.1'

    // RoadRunner (for reference)
    implementation 'com.acmerobotics.roadrunner:core:1.0.0'
}
```

---

## NextFTC (dev.nextftc:control)

**For more details on the NextFTC framework, see the [NextFTC Skill](../../../nextftc).**

### Installation

```gradle
implementation 'dev.nextftc:control:1.0.0'
```

### Position PID + Elevator Feedforward

```kotlin
import dev.nextftc.control.ControlSystem
import dev.nextftc.control.KineticState

val controller = ControlSystem.builder()
    .posPid(kP = 0.005, kI = 0.0, kD = 0.001)
    .elevatorFF(kG = 0.15)
    .build()

// In update loop
controller.goal = KineticState(position = targetPosition)
val output = controller.calculate(KineticState(position = currentPosition))
motor.power = output.coerceIn(-1.0, 1.0)
```

### Position PID + Arm Feedforward

```kotlin
val controller = ControlSystem.builder()
    .posPid(kP = 0.01, kI = 0.0, kD = 0.002)
    .armFF(kG = 0.3)  // Handles cos(angle) internally
    .build()

// Pass angle in radians
controller.goal = KineticState(position = targetAngleRad)
val output = controller.calculate(KineticState(position = currentAngleRad))
```

### Velocity PID + Basic Feedforward

```kotlin
val controller = ControlSystem.builder()
    .velPid(kP = 0.0001, kI = 0.0, kD = 0.0)
    .basicFF(kV = 0.00015, kS = 0.05)
    .build()

controller.goal = KineticState(velocity = targetVelocity)
val output = controller.calculate(KineticState(velocity = currentVelocity))
```

### Tolerance Checking

```kotlin
val tolerance = KineticState(position = 20.0)  // 20 ticks
if (controller.isWithinTolerance(tolerance)) {
    // On target
}
```

### Live Tuning Pattern

```kotlin
// Rebuild each loop to pick up tuning changes
override fun periodic() {
    controller = buildController()
    // ... rest of control logic
}
```

### All Builder Methods

| Method | Description |
|--------|-------------|
| `.posPid(kP, kI, kD)` | Position PID |
| `.velPid(kP, kI, kD)` | Velocity PID |
| `.posSquID(kP, kI, kD)` | Position SquID (square root integral) |
| `.velSquID(kP, kI, kD)` | Velocity SquID |
| `.basicFF(kV, kA, kS)` | Basic feedforward |
| `.elevatorFF(kG, kV, kA, kS)` | Elevator with gravity |
| `.armFF(kG, kV, kA, kS)` | Arm with cos(angle) gravity |
| `.posFilter { ... }` | Position filter |
| `.velFilter { ... }` | Velocity filter |

---

## FTCLib (com.arcrobotics.ftclib)

### Installation

```gradle
implementation 'com.arcrobotics.ftclib:core:2.1.1'
```

### Basic PID Controller

```java
import com.arcrobotics.ftclib.controller.PIDController;

PIDController pid = new PIDController(kP, kI, kD);

// In update loop
double output = pid.calculate(currentPosition, targetPosition);
motor.setPower(output);
```

### PID with Feedforward (Manual)

```java
PIDController pid = new PIDController(kP, kI, kD);

// Add feedforward manually
double pidOutput = pid.calculate(current, target);
double feedforward = kG;  // or kV * velocity, etc.
double output = pidOutput + feedforward;
motor.setPower(Math.max(-1, Math.min(1, output)));
```

### PIDF Controller (Built-in F term)

```java
import com.arcrobotics.ftclib.controller.PIDFController;

// F term is added to output: output = PID + F
PIDFController pidf = new PIDFController(kP, kI, kD, kF);
double output = pidf.calculate(current, target);
```

### Tolerance Checking

```java
pid.setTolerance(positionTolerance);
if (pid.atSetPoint()) {
    // On target
}
```

### Using MotorEx with Built-in PID

```java
import com.arcrobotics.ftclib.hardware.motors.MotorEx;

MotorEx motor = new MotorEx(hardwareMap, "motor");
motor.setRunMode(Motor.RunMode.PositionControl);
motor.setPositionCoefficient(kP);
motor.setPositionTolerance(tolerance);

motor.setTargetPosition(targetPosition);
motor.set(1.0);  // Run at full power toward target

if (motor.atTargetPosition()) {
    // On target
}
```

---

## Plain FTC SDK

### Manual PID Implementation

```java
public class SimplePID {
    private double kP, kI, kD;
    private double integral = 0;
    private double lastError = 0;
    private double maxIntegral = 1000;

    public SimplePID(double kP, double kI, double kD) {
        this.kP = kP;
        this.kI = kI;
        this.kD = kD;
    }

    public double calculate(double current, double target) {
        double error = target - current;

        // Integral with anti-windup
        integral += error;
        integral = Math.max(-maxIntegral, Math.min(maxIntegral, integral));

        // Derivative
        double derivative = error - lastError;
        lastError = error;

        return kP * error + kI * integral + kD * derivative;
    }

    public void reset() {
        integral = 0;
        lastError = 0;
    }
}
```

### PID + Elevator Feedforward

```java
public class ElevatorController {
    private SimplePID pid;
    private double kG;

    public ElevatorController(double kP, double kI, double kD, double kG) {
        this.pid = new SimplePID(kP, kI, kD);
        this.kG = kG;
    }

    public double calculate(double current, double target) {
        double pidOutput = pid.calculate(current, target);
        double feedforward = kG;
        return pidOutput + feedforward;
    }
}
```

### PID + Arm Feedforward

```java
public class ArmController {
    private SimplePID pid;
    private double kG;
    private double ticksPerRadian;

    public ArmController(double kP, double kI, double kD, double kG, double ticksPerRadian) {
        this.pid = new SimplePID(kP, kI, kD);
        this.kG = kG;
        this.ticksPerRadian = ticksPerRadian;
    }

    public double calculate(double currentTicks, double targetTicks) {
        double pidOutput = pid.calculate(currentTicks, targetTicks);

        // Gravity varies with angle
        double angleRad = currentTicks / ticksPerRadian;
        double feedforward = kG * Math.cos(angleRad);

        return pidOutput + feedforward;
    }
}
```

### PID + Velocity Feedforward

```java
public class FlywheelController {
    private SimplePID pid;
    private double kV;
    private double kS;

    public FlywheelController(double kP, double kI, double kD, double kV, double kS) {
        this.pid = new SimplePID(kP, kI, kD);
        this.kV = kV;
        this.kS = kS;
    }

    public double calculate(double currentVel, double targetVel) {
        double pidOutput = pid.calculate(currentVel, targetVel);
        double velocityFF = kV * targetVel;
        double staticFF = kS * Math.signum(targetVel);
        return pidOutput + velocityFF + staticFF;
    }
}
```

---

## Cross-Reference Table

| Concept | NextFTC | FTCLib | Plain SDK |
|---------|---------|--------|-----------|
| Position PID | `.posPid(kP, kI, kD)` | `PIDController(kP, kI, kD)` | Manual |
| Velocity PID | `.velPid(kP, kI, kD)` | `PIDFController` | Manual |
| Elevator FF | `.elevatorFF(kG)` | Manual addition | Manual |
| Arm FF | `.armFF(kG)` | Manual addition | Manual |
| Velocity FF | `.basicFF(kV, kS)` | Manual addition | Manual |
| Tolerance check | `.isWithinTolerance()` | `.atSetPoint()` | Manual |
| Reset | Rebuild controller | `.reset()` | Manual |
| Live tuning | Rebuild each loop | Update coefficients | Update variables |

---

## Choosing a Library

| If you need... | Use | Skill |
|----------------|-----|-------|
| Simplest API for mechanisms | NextFTC | [NextFTC Skill](../../../nextftc) |
| FRC-style motor wrappers | FTCLib | — |
| Maximum control/customization | Plain SDK | — |
| Path following | RoadRunner | [RoadRunner Skill](../../../roadrunner) |
| Path following (alternative) | Pedro Pathing | [Pedro Pathing Skill](../../../pedro-pathing) |
| Already using NextFTC framework | NextFTC control | [NextFTC Skill](../../../nextftc) |
| Already using FTCLib | FTCLib PIDController | — |
| Learning how control works | Plain SDK first | — |

---

## Migration Patterns

### Plain SDK → NextFTC

**Before (Plain SDK):**
```java
double error = target - current;
integral += error;
double derivative = error - lastError;
double pid = kP * error + kI * integral + kD * derivative;
double output = pid + kG;
```

**After (NextFTC):**
```kotlin
val controller = ControlSystem.builder()
    .posPid(kP, kI, kD)
    .elevatorFF(kG)
    .build()
val output = controller.calculate(KineticState(position = current))
```

### FTCLib → NextFTC

**Before (FTCLib):**
```java
PIDController pid = new PIDController(kP, kI, kD);
double output = pid.calculate(current, target) + kG;
```

**After (NextFTC):**
```kotlin
val controller = ControlSystem.builder()
    .posPid(kP, kI, kD)
    .elevatorFF(kG)
    .build()
```

---

## Related Skills

For more information about implementing control systems with these libraries:

- **[NextFTC Skill](../../../nextftc)** - Full NextFTC framework documentation, command-based programming, and integration patterns
- **[RoadRunner Skill](../../../roadrunner)** - Detailed guide to path planning, trajectories, and drivetrain control
- **[Pedro Pathing Skill](../../../pedro-pathing)** - Complete reference for Bezier curves, path building, and autonomous routines

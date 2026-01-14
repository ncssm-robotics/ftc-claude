# NextControl

NextControl provides PID control, feedforward, motion profiling, and filters for precise robot control.

## Installation

```gradle
implementation 'dev.nextftc:control:1.0.0'
```

## Core Concepts

NextControl uses a **builder pattern** with `ControlSystem`. You compose controllers from elements:

- **Feedback Elements**: PID (position or velocity), SquID, BangBang
- **Feedforward Elements**: Basic (kV, kA, kS), Elevator (gravity), Arm (gravity)
- **Filter Elements**: Low-pass filter for noisy sensors
- **Interpolator Elements**: EMA smoothing for motion profiles

## Basic Usage

```kotlin
import dev.nextftc.control.ControlSystem
import dev.nextftc.control.KineticState

// Build a position PID controller
val positionController = ControlSystem.builder()
    .posPid(kP = 0.05, kI = 0.001, kD = 0.002)
    .build()

// In your update loop
positionController.goal = KineticState(position = targetPosition)
val output = positionController.calculate(KineticState(position = currentPosition))
motor.power = output
```

## Velocity Control (Flywheel Example)

```kotlin
// Velocity PID with feedforward
val flywheelController = ControlSystem.builder()
    .velPid(kP = 0.0001, kI = 0.0, kD = 0.0)
    .basicFF(kV = 0.00015)  // Velocity feedforward
    .build()

// In update loop
flywheelController.goal = KineticState(velocity = targetVelocity)
val output = flywheelController.calculate(KineticState(velocity = motor.velocity))
motor.power = output.coerceIn(-1.0, 1.0)
```

## Position Control (Turret Example)

```kotlin
val turretController = ControlSystem.builder()
    .posPid(kP = 0.005, kI = 0.0, kD = 0.001)
    .build()

// In update loop
turretController.goal = KineticState(position = targetTicks.toDouble())
val output = turretController.calculate(KineticState(position = motor.currentPosition.toDouble()))
motor.power = output.coerceIn(-0.5, 0.5)
```

## Feedforward Types

### Basic Feedforward (Velocity Systems)

```kotlin
ControlSystem.builder()
    .velPid(kP, kI, kD)
    .basicFF(kV = 0.01, kA = 0.001, kS = 0.05)  // kV, kA, kS
    .build()
```

- `kV` - Velocity coefficient (power per unit velocity)
- `kA` - Acceleration coefficient
- `kS` - Static friction compensation

### Elevator Feedforward (Gravity Compensation)

```kotlin
ControlSystem.builder()
    .posPid(kP, kI, kD)
    .elevatorFF(kG = 0.15)  // Constant to hold against gravity
    .build()
```

### Arm Feedforward (Angle-Dependent Gravity)

```kotlin
ControlSystem.builder()
    .posPid(kP, kI, kD)
    .armFF(kG = 0.3)  // Varies with cos(angle)
    .build()
```

## Checking Tolerance

```kotlin
// Check if within tolerance of goal
val tolerance = KineticState(position = 10.0)  // 10 ticks
if (controller.isWithinTolerance(tolerance)) {
    // On target
}
```

## Live Tuning with Panels

To support live tuning, rebuild the controller each cycle:

```kotlin
object MySubsystem : Subsystem {
    private fun buildController() = ControlSystem.builder()
        .posPid(TuningConfig.MY_KP, TuningConfig.MY_KI, TuningConfig.MY_KD)
        .build()

    private var controller = buildController()

    override fun periodic() {
        // Rebuild to pick up tuning changes
        controller = buildController()

        controller.goal = KineticState(position = target)
        val output = controller.calculate(KineticState(position = current))
        motor.power = output
    }
}
```

## KineticState

`KineticState` holds position, velocity, and acceleration:

```kotlin
// Position only
KineticState(position = 100.0)

// Velocity only
KineticState(velocity = 500.0)

// Full state
KineticState(position = 100.0, velocity = 50.0, acceleration = 10.0)
```

## Complete Subsystem Example

```kotlin
object LiftSubsystem : Subsystem {
    private val motor by lazy {
        ActiveOpMode.hardwareMap.get(DcMotorEx::class.java, "lift").apply {
            mode = DcMotor.RunMode.RUN_USING_ENCODER
            zeroPowerBehavior = DcMotor.ZeroPowerBehavior.BRAKE
        }
    }

    private fun buildController() = ControlSystem.builder()
        .posPid(TuningConfig.LIFT_KP, TuningConfig.LIFT_KI, TuningConfig.LIFT_KD)
        .elevatorFF(kG = TuningConfig.LIFT_KG)
        .build()

    private var controller = buildController()
    private var targetPosition = 0

    override fun periodic() {
        controller = buildController()
        controller.goal = KineticState(position = targetPosition.toDouble())
        val output = controller.calculate(KineticState(position = motor.currentPosition.toDouble()))
        motor.power = output.coerceIn(-1.0, 1.0)
    }

    fun goTo(position: Int) = LambdaCommand()
        .setStart { targetPosition = position }
        .setIsDone {
            controller.isWithinTolerance(KineticState(position = TuningConfig.LIFT_TOLERANCE))
        }
        .requires(this)

    val toHigh = goTo(2000)
    val toLow = goTo(0)
}
```

## Builder Methods Reference

| Method | Description |
|--------|-------------|
| `.posPid(kP, kI, kD)` | Position PID feedback |
| `.velPid(kP, kI, kD)` | Velocity PID feedback |
| `.posSquID(kP, kI, kD)` | Position SquID (square root integral) |
| `.velSquID(kP, kI, kD)` | Velocity SquID |
| `.basicFF(kV, kA, kS)` | Basic feedforward |
| `.elevatorFF(kG, kV, kA, kS)` | Elevator with gravity |
| `.armFF(kG, kV, kA, kS)` | Arm with gravity |
| `.posFilter { ... }` | Position filter |
| `.velFilter { ... }` | Velocity filter |

## Resources

- [CTRL ALT FTC](https://www.ctrlaltftc.com/) - Control theory for FTC
- [Game Manual 0 - Control](https://gm0.org/en/latest/docs/software/concepts/control-loops.html)

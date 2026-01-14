# NextFTC Hardware Module

The hardware module provides wrappers and commands for motors and servos.

## Installation

```gradle
implementation 'dev.nextftc:hardware:1.0.1'
```

## Hardware Interfaces

| Interface | Description | Example Devices |
|-----------|-------------|-----------------|
| `Powerable` | Has power (get/set) | Motors |
| `Positionable` | Has position (get/set target) | Servos |
| `Controllable` | Powerable + current position/velocity | Motors with encoders |

## Motor Wrappers

### MotorEx

```kotlin
import dev.nextftc.hardware.impl.MotorEx

// Direct initialization (recommended)
private val liftMotor = MotorEx("lift")

// Can also configure immediately
private val driveMotor = MotorEx("drive").apply {
    zeroPowerBehavior = DcMotor.ZeroPowerBehavior.BRAKE
    direction = DcMotorSimple.Direction.REVERSE
}
```

### Write Caching

All wrappers cache writes with 0.01 tolerance to reduce I2C traffic:

```kotlin
motor.power = 0.5   // Writes to hardware
motor.power = 0.51  // Cached, no write (within tolerance)
motor.power = 0.6   // Writes to hardware
```

## Servo Wrappers

### ServoEx

```kotlin
import dev.nextftc.hardware.impl.ServoEx

// Direct initialization
private val clawServo = ServoEx("claw")
```

## Built-in Commands

### SetPower

Set motor power:

```kotlin
import dev.nextftc.hardware.motor.commands.SetPower

SetPower(motor, 0.5)  // Set to 50% power
SetPower(motor, 0.0)  // Stop
```

### SetPosition / SetPositions

Set servo position:

```kotlin
import dev.nextftc.hardware.positionable.SetPosition
import dev.nextftc.hardware.positionable.SetPositions

// Single servo
SetPosition(clawServo, 1.0)  // Open
SetPosition(clawServo, 0.0)  // Close

// Multiple servos simultaneously (using vararg Pair syntax)
SetPositions(
    leftServo to 0.5,
    rightServo to 0.5
)

// Example: Moving multiple servos together
val deployIntake = SetPositions(
    leftArmServo to 0.8,
    rightArmServo to 0.2,
    wristServo to 0.5
).requires(this).named("Deploy Intake")
```

**When to use:**
- Use `SetPosition` for single servo commands
- Use `SetPositions` when you need to move multiple servos simultaneously as one atomic operation
- Both commands complete immediately unless you override `.setIsDone()`

### RunToState

Run motor to encoder position:

```kotlin
import dev.nextftc.hardware.motor.commands.RunToState

RunToState(liftMotor, targetPosition = 1000, power = 0.8)
```

## Using Commands in Subsystems

```kotlin
import dev.nextftc.hardware.positionable.SetPosition
import dev.nextftc.hardware.powerable.SetPower

object ClawSubsystem : Subsystem {
    private val servo = ServoEx("claw")

    val open = SetPosition(servo, 1.0).requires(this)
    val close = SetPosition(servo, 0.0).requires(this)
}

object LiftSubsystem : Subsystem {
    private val motor = MotorEx("lift")

    val toHigh = RunToState(motor, 2000, 1.0).requires(this)
    val toLow = RunToState(motor, 0, 0.8).requires(this)
    val stop = SetPower(motor, 0.0).requires(this)
}
```

## Continuous Rotation Servos

For CR servos, use `CRServoEx`:

```kotlin
import dev.nextftc.hardware.impl.CRServoEx
import dev.nextftc.hardware.powerable.SetPower

private val intakeServo = CRServoEx("intake")

// CRServos use power instead of position
val intake = SetPower(intakeServo, 1.0).requires(this)
val outtake = SetPower(intakeServo, -1.0).requires(this)
val stop = SetPower(intakeServo, 0.0).requires(this)
```

## Servo with Feedback

For servos with position feedback (like Axon servos):

```kotlin
import dev.nextftc.ftc.hardware.FeedbackServoEx

private val armServo by lazy {
    FeedbackServoEx("armFeedback", "arm", 0.01)
}

// Can read actual position from feedback sensor
val currentPosition = armServo.currentPosition  // Returns 0 to 2π radians (absolute encoder)
```

**Constructor parameters:**
- `"armFeedback"` - AnalogInput device name for position feedback
- `"arm"` - Servo device name
- `0.01` - Write caching tolerance

### IMPORTANT: SetPosition Does NOT Automatically Wait for Feedback

`SetPosition` commands **do not** automatically use feedback to wait for the servo to reach the target. You must override `.setIsDone()` manually:

```kotlin
// ❌ WRONG - completes immediately without waiting
val moveArm = SetPosition(armServo, 0.5)
    .requires(this)

// ✅ CORRECT - waits for servo to reach target using feedback
val moveArm = SetPosition(armServo, 0.5)
    .setIsDone { abs(armServo.currentPosition - 0.5) < SERVO_TOLERANCE }
    .requires(this)
```

**Best Practice:** Store tolerance in TuningConfig for dashboard tuning:

```kotlin
// In TuningConfig.kt
@JvmField
var SERVO_TOLERANCE: Double = 0.02  // ±2%

// In subsystem
val moveArm = SetPosition(armServo, targetPosition)
    .setIsDone { abs(armServo.currentPosition - targetPosition) < TuningConfig.SERVO_TOLERANCE }
    .requires(this)
    .named("Move Arm")
```

## Module Structure

- **hardware module**: Interfaces and commands (SetPower, SetPosition, etc.)
- **ftc module**: Implementations (MotorEx, ServoEx, etc.)

The ftc module has a compile-only dependency on hardware, allowing you to use just the interfaces if preferred.

# NextFTC Subsystems

Subsystems organize hardware and commands for discrete robot mechanisms (lift, claw, arm, etc.).

## Why Subsystems?

1. **Organization**: Group related hardware and commands
2. **Conflict Prevention**: Only one command per subsystem at a time
3. **Lifecycle Management**: Automatic initialization and periodic updates
4. **Better Alternative**: Replaces the "robot class" antipattern

## Creating a Subsystem

```kotlin
object LiftSubsystem : Subsystem {
    // Hardware (lazy initialization)
    private val motor by lazy {
        ActiveOpMode.hardwareMap.get(DcMotorEx::class.java, "lift")
    }

    override fun initialize() {
        motor.mode = DcMotor.RunMode.RUN_USING_ENCODER
        motor.zeroPowerBehavior = DcMotor.ZeroPowerBehavior.BRAKE
    }

    override fun periodic() {
        // Runs every loop - use for telemetry, state updates
        ActiveOpMode.telemetry.addData("Lift Position", motor.currentPosition)
        ActiveOpMode.telemetry.update()  // REQUIRED after adding telemetry
    }

    // Commands as properties
    val toHigh = LambdaCommand()
        .setStart { motor.targetPosition = 1000 }
        .setIsDone { motor.currentPosition >= 990 }
        .requires(this)

    val toLow = LambdaCommand()
        .setStart { motor.targetPosition = 0 }
        .setIsDone { motor.currentPosition <= 10 }
        .requires(this)
}
```

## Registering Subsystems

In your OpMode:

```kotlin
init {
    addComponents(
        SubsystemComponent(LiftSubsystem, ClawSubsystem),
        // ... other components
    )
}
```

## Subsystem Interface

```kotlin
interface Subsystem {
    fun initialize() { }  // Called during init phase
    fun periodic() { }    // Called every loop
}
```

Both methods are optional - override only what you need.

## Requirements Pattern

Commands should require their subsystem:

```kotlin
object ClawSubsystem : Subsystem {
    private val servo by lazy { /* ... */ }

    val open = SetPosition(servo, 1.0).requires(this)
    val close = SetPosition(servo, 0.0).requires(this)
}
```

This ensures only one claw command runs at a time.

## Multiple Degrees of Freedom

For subsystems with independent mechanisms, use hardware as requirements:

```kotlin
object ArmSubsystem : Subsystem {
    private val clawServo by lazy { /* ... */ }
    private val pivotServo by lazy { /* ... */ }

    // Each can run independently
    val openClaw = SetPosition(clawServo, 1.0).requires(clawServo)
    val closeClaw = SetPosition(clawServo, 0.0).requires(clawServo)
    val pivotLeft = SetPosition(pivotServo, 0.0).requires(pivotServo)
    val pivotRight = SetPosition(pivotServo, 1.0).requires(pivotServo)
}
```

## Subsystem Groups

Group multiple subsystems for convenience:

```kotlin
val MechanismSubsystems = SubsystemGroup(LiftSubsystem, ClawSubsystem, ArmSubsystem)

// Register all at once
SubsystemComponent(MechanismSubsystems)
```

## Example: Complete Lift Subsystem

```kotlin
object LiftSubsystem : Subsystem {
    private val motor by lazy {
        ActiveOpMode.hardwareMap.get(DcMotorEx::class.java, "lift").apply {
            mode = DcMotor.RunMode.RUN_TO_POSITION
            zeroPowerBehavior = DcMotor.ZeroPowerBehavior.BRAKE
        }
    }

    // Position constants
    private const val HIGH = 2000
    private const val MEDIUM = 1200
    private const val LOW = 400
    private const val GROUND = 0
    private const val TOLERANCE = 20

    override fun periodic() {
        ActiveOpMode.telemetry.addData("Lift", motor.currentPosition)
        ActiveOpMode.telemetry.update()  // REQUIRED after adding telemetry
    }

    private fun goToPosition(target: Int) = LambdaCommand()
        .setStart {
            motor.targetPosition = target
            motor.power = 1.0
        }
        .setIsDone { abs(motor.currentPosition - target) < TOLERANCE }
        .setStop { motor.power = 0.0 }
        .requires(this)

    val toHigh = goToPosition(HIGH)
    val toMedium = goToPosition(MEDIUM)
    val toLow = goToPosition(LOW)
    val toGround = goToPosition(GROUND)
}
```

## Telemetry Best Practices

**IMPORTANT:** Always call `ActiveOpMode.telemetry.update()` after adding telemetry data.

```kotlin
override fun periodic() {
    ActiveOpMode.telemetry.addData("Position", motor.currentPosition)
    ActiveOpMode.telemetry.addData("Velocity", motor.velocity)
    ActiveOpMode.telemetry.update()  // REQUIRED - telemetry won't display without this
}
```

Without calling `.update()`, telemetry data won't be sent to the Driver Station display.

# NextFTC Bindings

NextBindings provides gamepad integration with button callbacks, edge detection, and joystick curves.

## Setup

Add to OpMode:

```kotlin
init {
    addComponents(
        BindingsComponent,
        // ... other components
    )
}
```

## Accessing Gamepads

```kotlin
import dev.nextftc.bindings.gamepad.Gamepads

// Gamepad references
Gamepads.gamepad1
Gamepads.gamepad2
```

## Button Bindings

### Rising Edge (Button Press)

```kotlin
// When button is pressed, schedule command
Gamepads.gamepad1.a whenBecomesTrue MyCommand()
```

### Falling Edge (Button Release)

```kotlin
// When button is released, schedule command
Gamepads.gamepad1.b whenBecomesFalse MyCommand()
```

### Available Buttons

```kotlin
// Face buttons
gamepad.a, gamepad.b, gamepad.x, gamepad.y

// Bumpers
gamepad.leftBumper, gamepad.rightBumper

// D-pad
gamepad.dpadUp, gamepad.dpadDown, gamepad.dpadLeft, gamepad.dpadRight

// Sticks (as buttons when pressed)
gamepad.leftStickButton, gamepad.rightStickButton

// Other
gamepad.start, gamepad.back, gamepad.guide
```

## Trigger/Joystick Thresholds

### Using greaterThan

```kotlin
// When trigger exceeds threshold
Gamepads.gamepad1.rightTrigger greaterThan 0.5 whenBecomesTrue IntakeOn()

// When joystick exceeds threshold
Gamepads.gamepad1.leftStickY greaterThan 0.8 whenBecomesTrue FastMode()
```

### Available Analog Inputs

```kotlin
// Triggers (0.0 to 1.0)
gamepad.leftTrigger, gamepad.rightTrigger

// Joysticks (-1.0 to 1.0)
gamepad.leftStickX, gamepad.leftStickY
gamepad.rightStickX, gamepad.rightStickY
```

## Command Composition

### Sequential Actions (then)

```kotlin
// Run commands in order when button pressed
Gamepads.gamepad1.a whenBecomesTrue (
    LiftToHigh() then OpenClaw() then Delay(0.5.seconds)
)
```

### Parallel Actions (and)

```kotlin
// Run commands simultaneously when button pressed
Gamepads.gamepad1.b whenBecomesTrue (
    LiftToMedium() and RotateArm()
)
```

### Combined

```kotlin
Gamepads.gamepad1.x whenBecomesTrue (
    ParallelGroup(LiftUp(), ArmOut()) then
    Delay(0.3.seconds) then
    OpenClaw()
)
```

## Toggle Pattern

```kotlin
object ClawSubsystem : Subsystem {
    private var isOpen = false

    val toggle = LambdaCommand()
        .setStart {
            isOpen = !isOpen
            servo.position = if (isOpen) 1.0 else 0.0
        }
        .setIsDone { true }  // Instant command
        .requires(this)
}

// In TeleOp
Gamepads.gamepad2.a whenBecomesTrue ClawSubsystem.toggle
```

## Driver Control Best Practices

```kotlin
override fun onStartButtonPressed() {
    // Primary driver (gamepad1) - drivetrain
    PedroDriverControlled(
        Gamepads.gamepad1.leftStickY,
        Gamepads.gamepad1.leftStickX,
        Gamepads.gamepad1.rightStickX,
        false
    )()

    // Secondary driver (gamepad2) - mechanisms
    Gamepads.gamepad2.a whenBecomesTrue LiftSubsystem.toHigh
    Gamepads.gamepad2.b whenBecomesTrue LiftSubsystem.toLow
    Gamepads.gamepad2.x whenBecomesTrue ClawSubsystem.open
    Gamepads.gamepad2.y whenBecomesTrue ClawSubsystem.close

    // Use bumpers/triggers for frequent actions (less thumb movement)
    Gamepads.gamepad2.rightBumper whenBecomesTrue IntakeSubsystem.intake
    Gamepads.gamepad2.leftBumper whenBecomesTrue IntakeSubsystem.outtake
}
```

## Variables and Ranges

For advanced use cases with numeric values:

```kotlin
// Create a range from analog input
val speedMultiplier = Gamepads.gamepad1.rightTrigger.asRange(0.3, 1.0)

// Use in command
val adjustedSpeed = speedMultiplier.value * baseSpeed
```

# FTCLib GamepadEx and Bindings

GamepadEx provides enhanced gamepad functionality with button state tracking, trigger handling, and seamless integration with the command system through button bindings.

## Imports

```java
import com.arcrobotics.ftclib.gamepad.GamepadEx;
import com.arcrobotics.ftclib.gamepad.GamepadKeys;
import com.arcrobotics.ftclib.gamepad.ButtonReader;
import com.arcrobotics.ftclib.gamepad.TriggerReader;
import com.arcrobotics.ftclib.gamepad.KeyReader;
import com.arcrobotics.ftclib.command.button.GamepadButton;
import com.arcrobotics.ftclib.command.button.Button;
import com.arcrobotics.ftclib.command.button.Trigger;
```

## Creating GamepadEx

```java
// In CommandOpMode
private GamepadEx driverGamepad;
private GamepadEx operatorGamepad;

@Override
public void initialize() {
    driverGamepad = new GamepadEx(gamepad1);
    operatorGamepad = new GamepadEx(gamepad2);
}
```

## Joystick Input

GamepadEx provides corrected joystick values with Y-axis inverted for intuitive control.

```java
// Left stick
double forward = driverGamepad.getLeftY();   // Up = positive
double strafe = driverGamepad.getLeftX();    // Right = positive

// Right stick
double turn = driverGamepad.getRightX();     // Right = positive
double rightY = driverGamepad.getRightY();

// Use for driving
drive.driveRobotCentric(strafe, forward, turn);
```

## Button Keys

```java
GamepadKeys.Button.A
GamepadKeys.Button.B
GamepadKeys.Button.X
GamepadKeys.Button.Y
GamepadKeys.Button.LEFT_BUMPER
GamepadKeys.Button.RIGHT_BUMPER
GamepadKeys.Button.BACK
GamepadKeys.Button.START
GamepadKeys.Button.DPAD_UP
GamepadKeys.Button.DPAD_DOWN
GamepadKeys.Button.DPAD_LEFT
GamepadKeys.Button.DPAD_RIGHT
GamepadKeys.Button.LEFT_STICK_BUTTON
GamepadKeys.Button.RIGHT_STICK_BUTTON
```

## Trigger Keys

```java
GamepadKeys.Trigger.LEFT_TRIGGER
GamepadKeys.Trigger.RIGHT_TRIGGER
```

## Reading Button States

### Direct State Check

```java
// Simple boolean check
boolean aPressed = driverGamepad.getButton(GamepadKeys.Button.A);

if (driverGamepad.getButton(GamepadKeys.Button.RIGHT_BUMPER)) {
    intake.run();
} else {
    intake.stop();
}
```

### State Change Detection

For edge detection (rising/falling), call `readButtons()` once per loop:

```java
// In loop
driverGamepad.readButtons();  // Must call first!

// Now these work correctly
if (driverGamepad.wasJustPressed(GamepadKeys.Button.A)) {
    // Fires once when A is first pressed
    toggleIntake();
}

if (driverGamepad.wasJustReleased(GamepadKeys.Button.B)) {
    // Fires once when B is released
    stopMechanism();
}

if (driverGamepad.isDown(GamepadKeys.Button.X)) {
    // True while X is held
    runContinuousAction();
}

if (driverGamepad.stateJustChanged(GamepadKeys.Button.Y)) {
    // True on both press and release
    logStateChange();
}
```

### State Detection Methods

| Method | Returns True When |
|--------|-------------------|
| `getButton(button)` | Button is currently pressed |
| `wasJustPressed(button)` | Button was just pressed (rising edge) |
| `wasJustReleased(button)` | Button was just released (falling edge) |
| `isDown(button)` | Button is currently held down |
| `stateJustChanged(button)` | Button state changed since last read |

## Reading Triggers

```java
// Get trigger value (0.0 to 1.0)
double leftTrigger = driverGamepad.getTrigger(GamepadKeys.Trigger.LEFT_TRIGGER);
double rightTrigger = driverGamepad.getTrigger(GamepadKeys.Trigger.RIGHT_TRIGGER);

// Use for variable speed
motor.set(rightTrigger);

// Use for proportional control
double speed = rightTrigger - leftTrigger;  // -1 to 1 range
```

## TriggerReader for Edge Detection

```java
TriggerReader leftTriggerReader = new TriggerReader(
    driverGamepad,
    GamepadKeys.Trigger.LEFT_TRIGGER
);

// In loop
leftTriggerReader.readValue();

if (leftTriggerReader.wasJustPressed()) {
    // Trigger crossed 0.5 threshold
}

if (leftTriggerReader.wasJustReleased()) {
    // Trigger dropped below 0.5
}
```

## Command Bindings

The command-based system allows declarative button-to-command mapping.

### Getting a GamepadButton

```java
// In CommandOpMode.initialize()
Button aButton = driverGamepad.getGamepadButton(GamepadKeys.Button.A);

// Or create directly
Button bButton = new GamepadButton(driverGamepad, GamepadKeys.Button.B);
```

### Binding Methods

| Method | Behavior |
|--------|----------|
| `whenPressed(command)` | Schedule command when button pressed |
| `whenReleased(command)` | Schedule command when button released |
| `whileHeld(command)` | Schedule repeatedly while held; cancel on release |
| `whenHeld(command)` | Schedule on press; cancel on release (no re-schedule) |
| `toggleWhenPressed(command)` | Toggle command on/off with each press |
| `cancelWhenPressed(command)` | Cancel the command when button pressed |

### Basic Binding Examples

```java
@Override
public void initialize() {
    // ... create subsystems and gamepads ...

    // Single action on press
    driverGamepad.getGamepadButton(GamepadKeys.Button.A)
        .whenPressed(new OpenClawCommand(claw));

    // Action on press and release
    driverGamepad.getGamepadButton(GamepadKeys.Button.RIGHT_BUMPER)
        .whenPressed(new InstantCommand(intake::run, intake))
        .whenReleased(new InstantCommand(intake::stop, intake));

    // Run while held
    driverGamepad.getGamepadButton(GamepadKeys.Button.LEFT_BUMPER)
        .whileHeld(new RunCommand(intake::outtake, intake));

    // Toggle behavior
    driverGamepad.getGamepadButton(GamepadKeys.Button.B)
        .toggleWhenPressed(new IntakeCommand(intake));
}
```

### Method Chaining

```java
driverGamepad.getGamepadButton(GamepadKeys.Button.Y)
    .whenPressed(new LiftToHighCommand(lift))
    .whenReleased(new LiftToGroundCommand(lift));
```

### Composed Triggers

Combine multiple buttons:

```java
// Both buttons must be pressed
driverGamepad.getGamepadButton(GamepadKeys.Button.X)
    .and(driverGamepad.getGamepadButton(GamepadKeys.Button.Y))
    .whenActive(new SpecialCommand());

// Either button pressed
driverGamepad.getGamepadButton(GamepadKeys.Button.LEFT_BUMPER)
    .or(driverGamepad.getGamepadButton(GamepadKeys.Button.RIGHT_BUMPER))
    .whenActive(new IntakeCommand(intake));

// Negate (when NOT pressed)
driverGamepad.getGamepadButton(GamepadKeys.Button.A)
    .negate()
    .whenActive(new StopCommand());
```

### Custom Triggers

Create triggers from any boolean condition:

```java
// Trigger from sensor
Trigger sensorTrigger = new Trigger(() -> sensor.getDistance() < 10);
sensorTrigger.whenActive(new StopIntakeCommand(intake));

// Trigger from subsystem state
Trigger liftAtTop = new Trigger(lift::atTarget);
liftAtTop.whenActive(new ScoreCommand(claw));

// Trigger from joystick position
Trigger leftStickUp = new Trigger(() -> driverGamepad.getLeftY() > 0.8);
leftStickUp.whenActive(new BoostCommand(drive));
```

## Complete Example: TeleOp Bindings

```java
@TeleOp(name = "Command TeleOp")
public class CommandTeleOp extends CommandOpMode {
    private GamepadEx driver;
    private GamepadEx operator;

    private DriveSubsystem drive;
    private IntakeSubsystem intake;
    private LiftSubsystem lift;
    private ClawSubsystem claw;

    @Override
    public void initialize() {
        // Create gamepads
        driver = new GamepadEx(gamepad1);
        operator = new GamepadEx(gamepad2);

        // Create subsystems
        drive = new DriveSubsystem(hardwareMap);
        intake = new IntakeSubsystem(hardwareMap);
        lift = new LiftSubsystem(hardwareMap);
        claw = new ClawSubsystem(hardwareMap);

        // Register subsystems
        register(drive, intake, lift, claw);

        // === DRIVER CONTROLS ===

        // Default drive command
        drive.setDefaultCommand(new RunCommand(
            () -> drive.driveRobotCentric(
                driver.getLeftX(),
                driver.getLeftY(),
                driver.getRightX()
            ),
            drive
        ));

        // Slow mode while left trigger held
        driver.getGamepadButton(GamepadKeys.Button.LEFT_BUMPER)
            .whileHeld(new RunCommand(
                () -> drive.driveRobotCentric(
                    driver.getLeftX() * 0.3,
                    driver.getLeftY() * 0.3,
                    driver.getRightX() * 0.3
                ),
                drive
            ));

        // === OPERATOR CONTROLS ===

        // Intake on right bumper
        operator.getGamepadButton(GamepadKeys.Button.RIGHT_BUMPER)
            .whileHeld(new InstantCommand(intake::intake, intake))
            .whenReleased(new InstantCommand(intake::stop, intake));

        // Outtake on left bumper
        operator.getGamepadButton(GamepadKeys.Button.LEFT_BUMPER)
            .whileHeld(new InstantCommand(intake::outtake, intake))
            .whenReleased(new InstantCommand(intake::stop, intake));

        // Lift positions on d-pad
        operator.getGamepadButton(GamepadKeys.Button.DPAD_UP)
            .whenPressed(new LiftToPositionCommand(lift, LiftSubsystem.HIGH));

        operator.getGamepadButton(GamepadKeys.Button.DPAD_RIGHT)
            .whenPressed(new LiftToPositionCommand(lift, LiftSubsystem.MEDIUM));

        operator.getGamepadButton(GamepadKeys.Button.DPAD_LEFT)
            .whenPressed(new LiftToPositionCommand(lift, LiftSubsystem.LOW));

        operator.getGamepadButton(GamepadKeys.Button.DPAD_DOWN)
            .whenPressed(new LiftToPositionCommand(lift, LiftSubsystem.GROUND));

        // Claw toggle on A
        operator.getGamepadButton(GamepadKeys.Button.A)
            .toggleWhenPressed(new InstantCommand(claw::toggle, claw));

        // Emergency stop on B
        operator.getGamepadButton(GamepadKeys.Button.B)
            .whenPressed(new InstantCommand(() -> {
                lift.stop();
                intake.stop();
            }, lift, intake));
    }
}
```

## ButtonReader Class

For non-command-based usage:

```java
ButtonReader aReader = new ButtonReader(driverGamepad, GamepadKeys.Button.A);

// In loop
aReader.readValue();  // Update state

if (aReader.wasJustPressed()) {
    // Rising edge
}

if (aReader.wasJustReleased()) {
    // Falling edge
}

if (aReader.isDown()) {
    // Currently pressed
}

if (aReader.stateJustChanged()) {
    // Changed since last read
}
```

## Anti-Patterns

### Bad: Forgetting readButtons()

```java
// Missing readButtons() call!
if (gamepad.wasJustPressed(GamepadKeys.Button.A)) {  // Won't work correctly
    doSomething();
}
```

### Good: Always call readButtons()

```java
gamepad.readButtons();  // Call once per loop
if (gamepad.wasJustPressed(GamepadKeys.Button.A)) {
    doSomething();
}
```

### Bad: Multiple readButtons() calls

```java
// Inefficient and can cause issues
gamepad.readButtons();
if (gamepad.wasJustPressed(GamepadKeys.Button.A)) { }
gamepad.readButtons();  // Don't call again!
if (gamepad.wasJustPressed(GamepadKeys.Button.B)) { }
```

### Good: Single readButtons() call

```java
gamepad.readButtons();  // Once per loop
if (gamepad.wasJustPressed(GamepadKeys.Button.A)) { }
if (gamepad.wasJustPressed(GamepadKeys.Button.B)) { }
if (gamepad.wasJustPressed(GamepadKeys.Button.X)) { }
```

### Bad: Bindings in run loop

```java
// Don't do this!
while (opModeIsActive()) {
    if (gamepad1.a) {
        new LiftCommand(lift).schedule();  // Creates new command every loop!
    }
}
```

### Good: Declarative bindings in initialize()

```java
@Override
public void initialize() {
    // Set up bindings once
    driver.getGamepadButton(GamepadKeys.Button.A)
        .whenPressed(new LiftCommand(lift));
}
```

## Debugging Bindings

```java
@Override
public void initialize() {
    // ... bindings ...

    // Debug: Print when commands scheduled
    driver.getGamepadButton(GamepadKeys.Button.A)
        .whenPressed(new InstantCommand(() -> {
            telemetry.addData("Button", "A pressed");
            telemetry.update();
        }));
}
```

---
name: ftclib
description: Helps write FTC robot code using the FTCLib library. Use for command-based programming, subsystems, GamepadEx input handling, Pure Pursuit path following, or vision pipelines.
license: MIT
compatibility: Claude Code, Codex CLI, VS Code Copilot, Cursor
metadata:
  author: ncssm-robotics
  version: "1.0.0"
  category: framework
---

# FTCLib

FTCLib is a comprehensive Java library for FTC robotics providing a command-based framework, enhanced gamepad input, Pure Pursuit path following, and vision pipelines. It brings FRC-style architecture to FTC development.

## Quick Start

### Dependencies

In `build.gradle` (TeamCode module):

```gradle
dependencies {
    implementation 'org.ftclib.ftclib:core:2.1.1'
    implementation 'org.ftclib.ftclib:vision:2.1.0'  // Optional: vision pipelines
}
```

In `build.common.gradle`:

```gradle
minSdkVersion 24  // Required (changed from 23)
```

Add to repositories if not present:

```gradle
mavenCentral()
```

### Key Imports

```java
// Command-based
import com.arcrobotics.ftclib.command.CommandOpMode;
import com.arcrobotics.ftclib.command.CommandBase;
import com.arcrobotics.ftclib.command.SubsystemBase;
import com.arcrobotics.ftclib.command.InstantCommand;
import com.arcrobotics.ftclib.command.RunCommand;
import com.arcrobotics.ftclib.command.SequentialCommandGroup;
import com.arcrobotics.ftclib.command.ParallelCommandGroup;

// Gamepad
import com.arcrobotics.ftclib.gamepad.GamepadEx;
import com.arcrobotics.ftclib.gamepad.GamepadKeys;
import com.arcrobotics.ftclib.gamepad.ButtonReader;

// Hardware
import com.arcrobotics.ftclib.hardware.motors.Motor;
import com.arcrobotics.ftclib.hardware.motors.MotorEx;
import com.arcrobotics.ftclib.drivebase.MecanumDrive;

// Pure Pursuit
import com.arcrobotics.ftclib.purepursuit.Path;
import com.arcrobotics.ftclib.purepursuit.waypoints.*;
```

### Basic TeleOp

```java
@TeleOp(name = "Command TeleOp")
public class CommandTeleOp extends CommandOpMode {
    private GamepadEx driver;
    private GamepadEx operator;
    private DriveSubsystem drive;
    private IntakeSubsystem intake;

    @Override
    public void initialize() {
        driver = new GamepadEx(gamepad1);
        operator = new GamepadEx(gamepad2);

        drive = new DriveSubsystem(hardwareMap);
        intake = new IntakeSubsystem(hardwareMap);

        register(drive, intake);

        // Default drive command
        drive.setDefaultCommand(new RunCommand(
            () -> drive.drive(
                driver.getLeftY(),
                driver.getLeftX(),
                driver.getRightX()
            ),
            drive
        ));

        // Button bindings
        operator.getGamepadButton(GamepadKeys.Button.RIGHT_BUMPER)
            .whileHeld(new InstantCommand(intake::run, intake))
            .whenReleased(new InstantCommand(intake::stop, intake));
    }
}
```

### Basic Autonomous

```java
@Autonomous(name = "Command Auto")
public class CommandAuto extends CommandOpMode {
    private DriveSubsystem drive;
    private IntakeSubsystem intake;

    @Override
    public void initialize() {
        drive = new DriveSubsystem(hardwareMap);
        intake = new IntakeSubsystem(hardwareMap);

        register(drive, intake);

        // Schedule autonomous sequence
        schedule(new SequentialCommandGroup(
            new DriveForwardCommand(drive, 24),
            new ParallelCommandGroup(
                new TurnCommand(drive, 90),
                new IntakeCommand(intake)
            ),
            new DriveForwardCommand(drive, 12)
        ));
    }
}
```

## Core Concepts

| Concept | Description |
|---------|-------------|
| **Commands** | State machines with initialize(), execute(), end(), isFinished() lifecycle |
| **Subsystems** | Hardware groupings that encapsulate motors/sensors with requirements |
| **CommandOpMode** | Abstract OpMode that runs the CommandScheduler automatically |
| **GamepadEx** | Enhanced gamepad with button state tracking and triggers |
| **Pure Pursuit** | Path following algorithm using waypoints and look-ahead circles |

## Creating Subsystems

```java
public class LiftSubsystem extends SubsystemBase {
    private final Motor liftMotor;

    public LiftSubsystem(HardwareMap hardwareMap) {
        liftMotor = new Motor(hardwareMap, "lift");
        liftMotor.setZeroPowerBehavior(Motor.ZeroPowerBehavior.BRAKE);
    }

    public void raise() {
        liftMotor.set(0.8);
    }

    public void lower() {
        liftMotor.set(-0.5);
    }

    public void stop() {
        liftMotor.set(0);
    }

    @Override
    public void periodic() {
        // Called every scheduler cycle
    }
}
```

## Creating Commands

```java
public class LiftToPositionCommand extends CommandBase {
    private final LiftSubsystem lift;
    private final int targetPosition;

    public LiftToPositionCommand(LiftSubsystem lift, int position) {
        this.lift = lift;
        this.targetPosition = position;
        addRequirements(lift);  // Declare subsystem dependency
    }

    @Override
    public void initialize() {
        // Called once when scheduled
    }

    @Override
    public void execute() {
        // Called repeatedly
        lift.setTarget(targetPosition);
    }

    @Override
    public boolean isFinished() {
        return lift.atTarget();
    }

    @Override
    public void end(boolean interrupted) {
        lift.stop();
    }
}
```

## Command Groups

```java
// Sequential - runs commands one after another
new SequentialCommandGroup(
    new DriveToGoal(drive),
    new RaiseLift(lift),
    new ScoreSample(claw)
);

// Parallel - runs all commands simultaneously
new ParallelCommandGroup(
    new DriveToGoal(drive),
    new RaiseLift(lift)
);

// Nested groups
new SequentialCommandGroup(
    new DriveForwardCommand(drive, 24),
    new ParallelCommandGroup(
        new RaiseLift(lift),
        new ExtendArm(arm)
    ),
    new OpenClaw(claw)
);
```

## Convenience Commands

| Command | Description |
|---------|-------------|
| `InstantCommand` | Runs once and finishes immediately |
| `RunCommand` | Runs continuously in execute() |
| `WaitCommand` | Waits for specified time |
| `WaitUntilCommand` | Waits until condition is true |
| `ConditionalCommand` | Runs one of two commands based on condition |
| `SelectCommand` | Selects from multiple commands via supplier |

```java
// InstantCommand - one-shot action
new InstantCommand(intake::run, intake);

// RunCommand - continuous action (good for default commands)
new RunCommand(() -> drive.arcadeDrive(gamepad.getLeftY(), gamepad.getRightX()), drive);

// ConditionalCommand - branching
new ConditionalCommand(
    new InstantCommand(intake::run, intake),
    new InstantCommand(intake::stop, intake),
    intake::isActive
);
```

## Gamepad Extensions

```java
GamepadEx gamepad = new GamepadEx(gamepad1);

// Joystick values (Y is inverted for intuitive control)
double forward = gamepad.getLeftY();
double strafe = gamepad.getLeftX();
double rotate = gamepad.getRightX();

// Trigger values (0.0 to 1.0)
double rightTrigger = gamepad.getTrigger(GamepadKeys.Trigger.RIGHT_TRIGGER);

// Button state checks
gamepad.readButtons();  // Call once per loop
gamepad.wasJustPressed(GamepadKeys.Button.A);   // True only first press
gamepad.wasJustReleased(GamepadKeys.Button.A);  // True only on release
gamepad.isDown(GamepadKeys.Button.A);           // True while held

// Command binding (in CommandOpMode.initialize())
gamepad.getGamepadButton(GamepadKeys.Button.A)
    .whenPressed(new LiftCommand(lift))
    .whenReleased(new StopLiftCommand(lift));

// Binding methods
// .whenPressed()    - schedules when button pressed
// .whenReleased()   - schedules when button released
// .whileHeld()      - schedules repeatedly while held, cancels on release
// .toggleWhenPressed() - toggles command on/off
```

## Pure Pursuit Path Following

```java
// Create waypoints
Waypoint start = new StartWaypoint(0, 0);
Waypoint point1 = new GeneralWaypoint(24, 0, Math.toRadians(0), 0.8, 0.5, 12);
Waypoint point2 = new GeneralWaypoint(24, 24, Math.toRadians(90), 0.6, 0.5, 12);
Waypoint end = new EndWaypoint(0, 24, Math.toRadians(180), 0.5, 0.5, 12, 2, 2);

// GeneralWaypoint parameters:
// x, y, rotation (radians), movementSpeed, turnSpeed, followRadius

// Create and follow path
Path path = new Path(start, point1, point2, end);
path.init();
path.followPath(mecanumDrive, odometry);

// Manual loop control
while (!path.isFinished()) {
    double[] speeds = path.loop(robot.getX(), robot.getY(), robot.getHeading());
    robot.drive(speeds[0], speeds[1], speeds[2]);
    robot.updatePose();
}

// Special waypoints
// PointTurnWaypoint - stops, turns, then continues
// InterruptWaypoint - executes action at waypoint
new InterruptWaypoint(24, 24, 0.8, 0.5, 12, 2, 2, intake::grab);
```

## Vision Pipelines

```java
// Setup camera with EasyOpenCV
int cameraMonitorViewId = hardwareMap.appContext.getResources()
    .getIdentifier("cameraMonitorViewId", "id", hardwareMap.appContext.getPackageName());

OpenCvCamera camera = OpenCvCameraFactory.getInstance()
    .createInternalCamera(OpenCvInternalCamera.CameraDirection.BACK, cameraMonitorViewId);

// Create and set pipeline
MyPipeline pipeline = new MyPipeline();
camera.setPipeline(pipeline);

camera.openCameraDeviceAsync(new OpenCvCamera.AsyncCameraOpenListener() {
    @Override
    public void onOpened() {
        camera.startStreaming(320, 240, OpenCvCameraRotation.UPRIGHT);
    }

    @Override
    public void onError(int errorCode) {}
});

// Access pipeline results
if (pipeline.isObjectDetected()) {
    Point center = pipeline.getObjectCenter();
}
```

## Anti-Patterns

### Bad: Not declaring subsystem requirements

```java
public class BadCommand extends CommandBase {
    private final LiftSubsystem lift;

    public BadCommand(LiftSubsystem lift) {
        this.lift = lift;
        // Missing: addRequirements(lift)
    }
}
```

### Good: Always declare requirements

```java
public class GoodCommand extends CommandBase {
    private final LiftSubsystem lift;

    public GoodCommand(LiftSubsystem lift) {
        this.lift = lift;
        addRequirements(lift);  // Prevents concurrent access conflicts
    }
}
```

### Bad: Calling readButtons() multiple times per loop

```java
// Inefficient - multiple reads
if (gamepad.wasJustPressed(GamepadKeys.Button.A)) { }
if (gamepad.wasJustPressed(GamepadKeys.Button.B)) { }
```

### Good: Single readButtons() call

```java
gamepad.readButtons();  // Once per loop
if (gamepad.wasJustPressed(GamepadKeys.Button.A)) { }
if (gamepad.wasJustPressed(GamepadKeys.Button.B)) { }
```

### Bad: Using global variables for subsystems

```java
public class BadOpMode extends CommandOpMode {
    public static DriveSubsystem drive;  // Global state is problematic
}
```

### Good: Pass subsystems through constructors

```java
public class DriveCommand extends CommandBase {
    private final DriveSubsystem drive;

    public DriveCommand(DriveSubsystem drive) {
        this.drive = drive;  // Dependency injection
        addRequirements(drive);
    }
}
```

## Reference Documentation

- [FTCLib Documentation](https://docs.ftclib.org/ftclib)
- [FTCLib GitHub](https://github.com/FTCLib/FTCLib)
- [Command System](https://docs.ftclib.org/ftclib/command-base/command-system)
- [Pure Pursuit](https://docs.ftclib.org/ftclib/pathing/pure-pursuit)
- [Gamepad Extensions](https://docs.ftclib.org/ftclib/features/gamepad-extensions)
- [Command-Based Samples](https://github.com/FTCLib/command-based-samples)

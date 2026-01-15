# FTCLib Commands

Commands are the fundamental units of robot behavior in FTCLib's command-based framework. They define actions with a clear lifecycle: initialize, execute, check completion, and end.

## Imports

```java
import com.arcrobotics.ftclib.command.Command;
import com.arcrobotics.ftclib.command.CommandBase;
import com.arcrobotics.ftclib.command.CommandScheduler;
import com.arcrobotics.ftclib.command.InstantCommand;
import com.arcrobotics.ftclib.command.RunCommand;
import com.arcrobotics.ftclib.command.WaitCommand;
import com.arcrobotics.ftclib.command.WaitUntilCommand;
import com.arcrobotics.ftclib.command.ConditionalCommand;
import com.arcrobotics.ftclib.command.SelectCommand;
import com.arcrobotics.ftclib.command.SequentialCommandGroup;
import com.arcrobotics.ftclib.command.ParallelCommandGroup;
import com.arcrobotics.ftclib.command.ParallelRaceGroup;
import com.arcrobotics.ftclib.command.ParallelDeadlineGroup;
```

## Command Lifecycle

```
schedule() → initialize() → execute() (repeats) → isFinished()=true → end()
```

| Method | When Called | Purpose |
|--------|-------------|---------|
| `initialize()` | Once when scheduled | Set up initial state, reset sensors |
| `execute()` | Every scheduler cycle | Main logic (keep fast!) |
| `isFinished()` | Every cycle after execute | Return true to end command |
| `end(interrupted)` | Once when ending | Cleanup; `interrupted=true` if cancelled |

## Creating Commands

### Extending CommandBase (Recommended)

```java
public class LiftToPositionCommand extends CommandBase {
    private final LiftSubsystem lift;
    private final int targetPosition;

    public LiftToPositionCommand(LiftSubsystem lift, int position) {
        this.lift = lift;
        this.targetPosition = position;
        addRequirements(lift);  // CRITICAL: Declare subsystem dependency
    }

    @Override
    public void initialize() {
        lift.setTargetPosition(targetPosition);
    }

    @Override
    public void execute() {
        lift.updatePID();
    }

    @Override
    public boolean isFinished() {
        return lift.atTarget();
    }

    @Override
    public void end(boolean interrupted) {
        if (interrupted) {
            lift.stop();
        }
        // Hold position if completed normally
    }
}
```

### Implementing Command Interface (Advanced)

```java
public class MyCommand implements Command {
    private final Set<Subsystem> requirements = new HashSet<>();

    public MyCommand(Subsystem... subsystems) {
        Collections.addAll(requirements, subsystems);
    }

    @Override
    public Set<Subsystem> getRequirements() {
        return requirements;
    }

    @Override
    public void initialize() { }

    @Override
    public void execute() { }

    @Override
    public boolean isFinished() {
        return false;
    }

    @Override
    public void end(boolean interrupted) { }
}
```

## Scheduling Commands

```java
// Schedule a command
command.schedule();

// Cancel a command
command.cancel();

// Check if running
command.isScheduled();

// Run scheduler (called automatically in CommandOpMode)
CommandScheduler.getInstance().run();
```

## Convenience Commands

### InstantCommand

Runs once and finishes immediately. Perfect for one-shot actions.

```java
// Lambda syntax
new InstantCommand(() -> intake.open());

// Method reference
new InstantCommand(intake::open);

// With subsystem requirement
new InstantCommand(intake::open, intake);

// Multiple actions
new InstantCommand(() -> {
    lift.reset();
    arm.home();
}, lift, arm);
```

### RunCommand

Runs continuously in execute(). Never finishes on its own.

```java
// Continuous intake
new RunCommand(intake::spin, intake);

// Drive command (great for default commands)
new RunCommand(
    () -> drive.arcadeDrive(gamepad.getLeftY(), gamepad.getRightX()),
    drive
);
```

### WaitCommand

Waits for a specified duration in milliseconds.

```java
new WaitCommand(500);  // Wait 500ms
new WaitCommand(2000); // Wait 2 seconds
```

### WaitUntilCommand

Waits until a condition becomes true.

```java
new WaitUntilCommand(lift::atTarget);
new WaitUntilCommand(() -> sensor.getDistance() < 10);
```

### ConditionalCommand

Chooses between two commands based on a condition.

```java
new ConditionalCommand(
    new ScoreHighCommand(lift),    // If true
    new ScoreLowCommand(lift),     // If false
    () -> gamepad.getButton(GamepadKeys.Button.Y)  // Condition
);

// Toggle pattern
new ConditionalCommand(
    new InstantCommand(intake::run, intake),
    new InstantCommand(intake::stop, intake),
    intake::isRunning
);
```

### SelectCommand

Selects from multiple commands based on a supplier.

```java
new SelectCommand(
    new HashMap<Object, Command>() {{
        put(Height.HIGH, new LiftToHigh(lift));
        put(Height.MEDIUM, new LiftToMedium(lift));
        put(Height.LOW, new LiftToLow(lift));
        put(Height.GROUND, new LiftToGround(lift));
    }},
    this::getSelectedHeight
);
```

### FunctionalCommand

Inline definition of a complete command.

```java
new FunctionalCommand(
    () -> motor.resetEncoder(),           // initialize
    () -> motor.set(0.5),                 // execute
    (interrupted) -> motor.stop(),        // end
    () -> motor.getCurrentPosition() > 1000,  // isFinished
    subsystem                             // requirements
);
```

### StartEndCommand

InstantCommand with a custom end action.

```java
new StartEndCommand(
    intake::run,   // On start
    intake::stop,  // On end
    intake
);
```

### PerpetualCommand

Wraps a command to run forever, ignoring its isFinished().

```java
new PerpetualCommand(new DriveCommand(drive));
```

## Command Groups

### SequentialCommandGroup

Runs commands one after another.

```java
new SequentialCommandGroup(
    new DriveForwardCommand(drive, 24),
    new TurnCommand(drive, 90),
    new DriveForwardCommand(drive, 12)
);
```

### ParallelCommandGroup

Runs all commands simultaneously. Finishes when ALL complete.

```java
new ParallelCommandGroup(
    new LiftToHighCommand(lift),
    new ExtendArmCommand(arm),
    new OpenClawCommand(claw)
);
```

### ParallelRaceGroup

Runs all commands simultaneously. Finishes when ANY completes, cancelling others.

```java
new ParallelRaceGroup(
    new DriveToTargetCommand(drive),
    new WaitCommand(5000)  // 5 second timeout
);
```

### ParallelDeadlineGroup

Runs commands in parallel. Finishes when the FIRST command (deadline) completes.

```java
new ParallelDeadlineGroup(
    new DriveForwardCommand(drive, 24),  // Deadline
    new SpinIntakeCommand(intake),       // Runs until drive finishes
    new UpdateTelemetryCommand()
);
```

### Nested Groups

```java
new SequentialCommandGroup(
    // Drive to scoring position
    new DriveToPositionCommand(drive, scoringPose),

    // Raise and extend simultaneously
    new ParallelCommandGroup(
        new LiftToHighCommand(lift),
        new ExtendArmCommand(arm)
    ),

    // Score with timeout
    new ParallelRaceGroup(
        new ScoreCommand(claw),
        new WaitCommand(2000)
    ),

    // Retract
    new ParallelCommandGroup(
        new RetractArmCommand(arm),
        new LiftToGroundCommand(lift)
    )
);
```

## Command Decorators

Chain methods to modify command behavior.

```java
// Add timeout
command.withTimeout(3000);  // 3 second timeout

// Run something after
command.andThen(new NextCommand());

// Run something before
command.beforeStarting(new SetupCommand());

// Run in parallel
command.alongWith(new OtherCommand());

// Race with another command
command.raceWith(new TimeoutCommand());

// Add interrupt condition
command.withInterrupt(() -> sensor.isTriggered());

// Run perpetually
command.perpetually();
```

### Decorator Examples

```java
// Drive with 5 second timeout
new DriveToTargetCommand(drive)
    .withTimeout(5000)
    .andThen(new InstantCommand(drive::stop, drive));

// Intake until sensor triggered or 3 seconds
new RunCommand(intake::run, intake)
    .withInterrupt(sensor::isTriggered)
    .withTimeout(3000)
    .andThen(new InstantCommand(intake::stop, intake));
```

## Requirements and Scheduling

### Declaring Requirements

```java
public class ArmCommand extends CommandBase {
    public ArmCommand(ArmSubsystem arm) {
        addRequirements(arm);  // Single subsystem
    }
}

public class ScoringCommand extends CommandBase {
    public ScoringCommand(LiftSubsystem lift, ArmSubsystem arm, ClawSubsystem claw) {
        addRequirements(lift, arm, claw);  // Multiple subsystems
    }
}
```

### How Requirements Work

- Only ONE command can use a subsystem at a time
- New commands interrupt old commands using the same subsystem
- Command groups inherit requirements from all contained commands

```java
// LiftUp requires LiftSubsystem
// If LiftDown is scheduled while LiftUp is running,
// LiftUp is interrupted and LiftDown starts
```

## Default Commands

Commands that run when no other command requires a subsystem.

```java
// In CommandOpMode.initialize()
drive.setDefaultCommand(new RunCommand(
    () -> drive.arcadeDrive(
        gamepad.getLeftY(),
        gamepad.getRightX()
    ),
    drive
));

// Alternative syntax
CommandScheduler.getInstance().setDefaultCommand(
    drive,
    new DriveCommand(drive, gamepad)
);
```

## Anti-Patterns

### Bad: Not declaring requirements

```java
public class BadCommand extends CommandBase {
    private final LiftSubsystem lift;

    public BadCommand(LiftSubsystem lift) {
        this.lift = lift;
        // MISSING: addRequirements(lift)
    }
}
```

### Good: Always declare requirements

```java
public class GoodCommand extends CommandBase {
    private final LiftSubsystem lift;

    public GoodCommand(LiftSubsystem lift) {
        this.lift = lift;
        addRequirements(lift);  // Prevents conflicts
    }
}
```

### Bad: Blocking in execute()

```java
@Override
public void execute() {
    Thread.sleep(100);  // NEVER block!
    motor.set(1.0);
}
```

### Good: Non-blocking execute()

```java
@Override
public void execute() {
    motor.set(1.0);  // Return immediately
}

@Override
public boolean isFinished() {
    return timer.milliseconds() > 100;  // Use state for timing
}
```

### Bad: Complex logic in isFinished()

```java
@Override
public boolean isFinished() {
    updatePID();      // Don't do work here!
    readSensors();    // This belongs in execute()
    return atTarget;
}
```

### Good: Simple boolean check

```java
@Override
public boolean isFinished() {
    return Math.abs(current - target) < tolerance;
}
```

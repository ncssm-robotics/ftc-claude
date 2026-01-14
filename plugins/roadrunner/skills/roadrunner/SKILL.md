---
name: roadrunner
description: >-
  Helps build autonomous routines using the RoadRunner 1.0 path planning library.
  Use when creating trajectories, configuring motion profiles, setting up
  localization, tuning drive constants, building spline paths, or combining
  actions for complex autonomous sequences.
license: MIT
compatibility: Claude Code, Codex CLI, VS Code Copilot, Cursor
metadata:
  author: ncssm-robotics
  version: "1.0.0"
  category: library
---

# RoadRunner Path Planning

RoadRunner is a motion planning library for FTC that provides trajectory following, feedforward control, and advanced path building. Version 1.0 introduced a new Actions-based API for composing autonomous routines.

## Quick Start

### Option 1: Quickstart Project (Recommended)

Clone the pre-configured project:
```bash
git clone https://github.com/acmerobotics/road-runner-quickstart.git
```

### Option 2: Add to Existing Project

Add to `TeamCode/build.gradle`:

```gradle
repositories {
    maven {
        url = 'https://maven.brott.dev/'
    }
}

dependencies {
    implementation "com.acmerobotics.roadrunner:ftc:0.1.25"
    implementation "com.acmerobotics.roadrunner:core:1.0.1"
    implementation "com.acmerobotics.roadrunner:actions:1.0.1"
    implementation "com.acmerobotics.dashboard:dashboard:0.5.1"
}
```

Then copy the tuning OpModes from the quickstart's `TeamCode/src/main/java/org/firstinspires/ftc/teamcode` folder (including `messages` and `tuning` subdirectories).

### Basic Autonomous

```java
@Autonomous(name = "Basic Auto")
public class BasicAuto extends LinearOpMode {
    @Override
    public void runOpMode() {
        MecanumDrive drive = new MecanumDrive(hardwareMap, new Pose2d(0, 0, 0));

        Action trajectory = drive.actionBuilder(new Pose2d(0, 0, 0))
            .lineToX(48)
            .turn(Math.PI / 2)
            .lineToY(48)
            .build();

        waitForStart();

        Actions.runBlocking(trajectory);
    }
}
```

## Key Concepts

| Term | Description |
|------|-------------|
| **Action** | Smallest unit of robot behavior. Returns `true` while running, `false` when complete |
| **Trajectory** | A planned path with motion profile (velocity/acceleration constraints) |
| **Pose2d** | Robot position and heading: `new Pose2d(x, y, heading)` |
| **Vector2d** | 2D position without heading: `new Vector2d(x, y)` |
| **Feedforward** | Open-loop motor control using kS, kV, kA constants |
| **inPerTick** | Encoder conversion factor: inches traveled per encoder tick |
| **trackWidthTicks** | Distance between drive wheels in encoder ticks |

## Trajectory Builder Methods

### Line Movements

```java
// Move to specific X coordinate (maintains current Y)
.lineToX(48)

// Move to specific Y coordinate (maintains current X)
.lineToY(36)

// Move to specific position
.lineToXY(new Vector2d(48, 36))
```

### Spline Paths

```java
// Curved path to position with exit tangent
.splineTo(new Vector2d(48, 48), Math.PI / 2)

// Spline with constant heading (robot faces same direction)
.splineToConstantHeading(new Vector2d(48, 48), Math.PI / 2)

// Spline with linear heading interpolation
.splineToLinearHeading(new Pose2d(48, 48, Math.PI), Math.PI / 2)

// Spline with spline heading interpolation (smoothest)
.splineToSplineHeading(new Pose2d(48, 48, Math.PI), Math.PI / 2)
```

### Turns

```java
// Turn by angle (relative)
.turn(Math.PI / 2)        // 90 degrees counterclockwise
.turn(-Math.PI / 2)       // 90 degrees clockwise

// Turn to absolute heading
.turnTo(Math.PI)          // Face 180 degrees
```

### Tangent Control

```java
// Set the tangent direction for the next segment
.setTangent(Math.toRadians(45))
.splineTo(new Vector2d(48, 48), Math.PI / 2)
```

## Common Patterns

### Pattern 1: Sequential Actions

```java
Action auto = new SequentialAction(
    drive.actionBuilder(startPose)
        .lineToX(24)
        .build(),
    arm.raise(),
    claw.open(),
    drive.actionBuilder(new Pose2d(24, 0, 0))
        .lineToX(0)
        .build()
);

Actions.runBlocking(auto);
```

### Pattern 2: Parallel Actions

```java
// Drive while raising arm simultaneously
Action auto = new ParallelAction(
    drive.actionBuilder(startPose)
        .splineTo(new Vector2d(48, 24), Math.PI / 4)
        .build(),
    arm.raise()  // Happens during drive
);

Actions.runBlocking(auto);
```

### Pattern 3: Custom Action

```java
public class GrabAction implements Action {
    private Claw claw;
    private boolean finished = false;

    public GrabAction(Claw claw) {
        this.claw = claw;
    }

    @Override
    public boolean run(@NonNull TelemetryPacket packet) {
        if (!finished) {
            claw.close();
            finished = true;
            return true;  // Still running (let servo move)
        }
        return false;  // Complete
    }
}
```

### Pattern 4: Wait/Delay

```java
Action auto = new SequentialAction(
    claw.close(),
    new SleepAction(0.5),  // Wait 500ms
    arm.raise()
);
```

## Tuning Process

**Important:** Follow this order exactly. Each step depends on previous results.

| Step | OpMode | What It Tunes |
|------|--------|---------------|
| 1 | Configure drive class | Motor names, IMU orientation |
| 2 | Motor direction test | Verify motor spin directions |
| 3 | ForwardPushTest | `inPerTick` |
| 4 | LateralPushTest | `lateralInPerTick` (mecanum only) |
| 5 | ForwardRampLogger | Collect feedforward data |
| 6 | ManualFeedforwardTuner | `kS`, `kV`, `kA` |
| 7 | ManualFeedbackTuner | Position/velocity gains |
| 8 | SplineTest | Validate all tuning |

### Hardware Naming Convention

```java
// Mecanum drive motors
"leftFront", "leftBack", "rightBack", "rightFront"

// IMU
"imu"

// Dead wheel encoders (if using)
"par"   // Parallel to drive direction
"perp"  // Perpendicular to drive direction
```

## Anti-Patterns

- ❌ **Skipping tuning steps** - Each step builds on previous results; skipping causes poor tracking
- ❌ **Long-running Action.run()** - Keep under 100ms; use state machines for complex actions
- ❌ **Blocking in run()** - Never use `Thread.sleep()` or while loops inside actions
- ❌ **Ignoring units** - RoadRunner uses inches and radians; don't mix with cm or degrees
- ❌ **Reusing trajectories** - Build fresh for each run; pose state changes
- ❌ **Hardcoding poses** - Use constants or enums for reusability

## Examples

### Good: Complete Autonomous with Actions

```java
@Autonomous(name = "Sample Auto")
public class SampleAuto extends LinearOpMode {
    @Override
    public void runOpMode() {
        MecanumDrive drive = new MecanumDrive(hardwareMap, new Pose2d(12, -62, Math.PI / 2));
        Arm arm = new Arm(hardwareMap);
        Claw claw = new Claw(hardwareMap);

        // Build the trajectory during init
        Action driveToBasket = drive.actionBuilder(new Pose2d(12, -62, Math.PI / 2))
            .splineTo(new Vector2d(48, -48), Math.PI / 4)
            .build();

        Action scoreSequence = new SequentialAction(
            new ParallelAction(
                driveToBasket,
                arm.raise()
            ),
            claw.open(),
            new SleepAction(0.3),
            arm.lower()
        );

        waitForStart();

        if (opModeIsActive()) {
            Actions.runBlocking(scoreSequence);
        }
    }
}
```

### Bad: Blocking Code in Actions

```java
// ❌ Don't do this - blocks the action loop
public class BadAction implements Action {
    @Override
    public boolean run(TelemetryPacket packet) {
        motor.setPower(1.0);
        Thread.sleep(1000);  // ❌ NEVER block!
        motor.setPower(0);
        return false;
    }
}

// ✓ Use state machine instead
public class GoodAction implements Action {
    private ElapsedTime timer = new ElapsedTime();
    private boolean started = false;

    @Override
    public boolean run(TelemetryPacket packet) {
        if (!started) {
            motor.setPower(1.0);
            timer.reset();
            started = true;
        }

        if (timer.seconds() >= 1.0) {
            motor.setPower(0);
            return false;  // Complete
        }
        return true;  // Still running
    }
}
```

### Bad: Wrong Heading Control

```java
// ❌ Robot spins wildly - tangent heading on sharp corners
.lineToX(48)
.lineToY(48)  // 90-degree corner causes heading discontinuity

// ✓ Use constant heading for sharp turns
.lineToXConstantHeading(48)
.lineToYConstantHeading(48)

// ✓ Or use splines for smooth curves
.splineTo(new Vector2d(48, 48), Math.PI / 2)
```

## Migration from 0.5.x

RoadRunner 1.0 is **not backwards compatible**. Key changes:

| 0.5.x | 1.0 |
|-------|-----|
| `drive.followTrajectoryAsync()` | `Actions.runBlocking(trajectory)` |
| `TrajectoryBuilder` | `drive.actionBuilder()` |
| `drive.update()` loop | Actions handle internally |
| Separate trajectory/turn | Unified action system |

Remove all 0.5.x references before upgrading.

## External Resources

- [RoadRunner 1.0 Documentation](https://rr.brott.dev/docs/v1-0/)
- [Learn Road Runner (0.5.x legacy)](https://learnroadrunner.com/)
- [GitHub Repository](https://github.com/acmerobotics/road-runner)
- [FTC Dashboard](https://acmerobotics.github.io/ftc-dashboard/)

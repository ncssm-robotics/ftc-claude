---
name: pedro-pathing
description: Helps write autonomous and teleop code using Pedro Pathing library. Use when creating paths, building autonomous routines, setting up path following, working with Follower, PathChain, BezierLine, or heading interpolation.
license: MIT
compatibility: Claude Code, Codex CLI, VS Code Copilot, Cursor
metadata:
  author: ncssm-robotics
  version: "1.0.0"
  category: library
---

# Pedro Pathing

Pedro Pathing is a path follower using Bezier curves for smooth autonomous navigation.

## Quick Start

### Autonomous OpMode Structure

```java
@Autonomous(name = "My Auto")
public class MyAuto extends OpMode {
    private Follower follower;
    private Timer pathTimer;
    private int pathState;

    // Define poses (x, y, heading in radians)
    private final Pose startPose = new Pose(7, 6.75, Math.toRadians(0));
    private final Pose targetPose = new Pose(24, 48, Math.toRadians(90));

    @Override
    public void init() {
        pathTimer = new Timer();
        follower = Constants.createFollower(hardwareMap);
        buildPaths();
        follower.setStartingPose(startPose);
    }

    @Override
    public void loop() {
        follower.update();  // MUST call every loop
        autonomousPathUpdate();
        telemetry.update();
    }
}
```

### Building Paths

```java
// Straight line path
Path straightPath = new Path(new BezierLine(startPose, endPose));
straightPath.setLinearHeadingInterpolation(startPose.getHeading(), endPose.getHeading());

// PathChain (multiple segments or single path via builder)
PathChain myChain = follower.pathBuilder()
    .addPath(new BezierLine(startPose, endPose))
    .setLinearHeadingInterpolation(startPose.getHeading(), endPose.getHeading())
    .build();
```

### Following Paths

```java
follower.followPath(myPath);           // Follow without holding endpoint
follower.followPath(myChain, true);    // Hold endpoint position when done
```

### State Machine Pattern

```java
public void autonomousPathUpdate() {
    switch (pathState) {
        case 0:
            follower.followPath(firstPath);
            setPathState(1);
            break;
        case 1:
            if (!follower.isBusy()) {
                // Path complete, do action then next path
                follower.followPath(nextPath, true);
                setPathState(2);
            }
            break;
    }
}

public void setPathState(int state) {
    pathState = state;
    pathTimer.resetTimer();
}
```

### TeleOp with Pedro

```java
@Override
public void loop() {
    follower.update();
    follower.setTeleOpMovementVectors(
        -gamepad1.left_stick_y,   // forward
        -gamepad1.left_stick_x,   // strafe
        -gamepad1.right_stick_x,  // turn
        true                      // robot-centric (false for field-centric)
    );
}
```

## Key Concepts

- **Pose**: Position (x, y) + heading in radians. Field is 144x144 inches, origin bottom-left
- **BezierLine**: Straight path between two points
- **BezierCurve**: Curved path with control points (minimum 3 points)
- **PathChain**: Multiple path segments as one unit
- **Follower**: Main controller - call `update()` every loop cycle

## Transition Conditions

Check when path is complete:
- `!follower.isBusy()` - Path finished
- `pathTimer.getElapsedTimeSeconds() > 1.5` - Time elapsed
- `follower.getPose().getX() > 36` - Position threshold

## Reference Documentation

- [HEADING_INTERPOLATION.md](HEADING_INTERPOLATION.md) - All heading options
- [CONSTRAINTS.md](CONSTRAINTS.md) - Path completion constraints
- [CONSTANTS_SETUP.md](CONSTANTS_SETUP.md) - Robot configuration
- [TUNING.md](TUNING.md) - Tuning process overview

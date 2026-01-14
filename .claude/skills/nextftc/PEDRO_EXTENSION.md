# NextFTC Pedro Pathing Extension

Integration between NextFTC commands and Pedro Pathing for autonomous navigation.

## Setup

### Dependencies

```gradle
implementation 'dev.nextftc.extensions:pedro:1.0.0'
implementation 'com.pedropathing:ftc:2.0.4'
```

### Add PedroComponent

```kotlin
init {
    addComponents(
        PedroComponent(Constants::createFollower),
        // ... other components
    )
}
```

The PedroComponent:
1. Creates the follower during init
2. Calls `follower.update()` every loop automatically

## Accessing the Follower

```kotlin
import dev.nextftc.extensions.pedro.PedroComponent.follower

// Direct access
follower.setStartingPose(startPose)
val currentPose = follower.getPose()
```

## FollowPath Command

Use `FollowPath` instead of `follower.followPath()`:

```kotlin
import dev.nextftc.extensions.pedro.FollowPath

// Basic usage
FollowPath(myPath)
FollowPath(myPathChain)

// With options
FollowPath(path, holdEnd = true)
FollowPath(path, holdEnd = true, maxPower = 0.5)
```

**Important**: Cannot pass `maxPower` without also passing `holdEnd`.

### FollowPath Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `path` | required | Path or PathChain to follow |
| `holdEnd` | from FollowerConstants | Hold position at path end |
| `maxPower` | from FollowerConstants | Maximum motor power (0-1) |

## TeleOp Driving

### PedroDriverControlled

```kotlin
import dev.nextftc.extensions.pedro.PedroDriverControlled

// Robot-centric (default)
PedroDriverControlled(
    Gamepads.gamepad1.leftStickY,   // forward/back
    Gamepads.gamepad1.leftStickX,   // strafe
    Gamepads.gamepad1.rightStickX   // rotation
)()

// Field-centric
PedroDriverControlled(
    Gamepads.gamepad1.leftStickY,
    Gamepads.gamepad1.leftStickX,
    Gamepads.gamepad1.rightStickX,
    false  // false = field-centric
)()
```

### Control Modes

- **Robot-centric** (`true`): Joystick forward = robot forward (relative to robot)
- **Field-centric** (`false`): Joystick forward = away from driver (relative to field)

## Autonomous Example

```kotlin
@Autonomous(name = "My Auto")
class MyAuto : NextFTCOpMode() {
    private val startPose = Pose(7.0, 6.75, Math.toRadians(0.0))
    private val scorePose = Pose(24.0, 48.0, Math.toRadians(90.0))

    private lateinit var scorePath: Path

    init {
        addComponents(
            BulkReadComponent,
            PedroComponent(Constants::createFollower)
        )
    }

    override fun onInit() {
        super.onInit()
        buildPaths()
        PedroComponent.follower.setStartingPose(startPose)
    }

    private fun buildPaths() {
        scorePath = Path(BezierLine(startPose, scorePose)).apply {
            setLinearHeadingInterpolation(startPose.heading, scorePose.heading)
        }
    }

    override fun onStartButtonPressed() {
        SequentialGroup(
            FollowPath(scorePath, holdEnd = true),
            Delay(0.5.seconds),
            // Add mechanism commands here
        )()
    }
}
```

## Building Paths

Paths are built using Pedro Pathing's API:

```kotlin
// Straight line path
val straightPath = Path(BezierLine(startPose, endPose)).apply {
    setLinearHeadingInterpolation(startPose.heading, endPose.heading)
}

// PathChain via builder
val chain = follower.pathBuilder()
    .addPath(BezierLine(startPose, midPose))
    .setLinearHeadingInterpolation(startPose.heading, midPose.heading)
    .addPath(BezierLine(midPose, endPose))
    .setLinearHeadingInterpolation(midPose.heading, endPose.heading)
    .build()
```

## Combining Paths with Mechanisms

```kotlin
SequentialGroup(
    // Drive to scoring position
    FollowPath(scoreApproach, holdEnd = true),

    // Score while holding position
    ParallelGroup(
        LiftSubsystem.toHigh,
        ArmSubsystem.extend
    ),
    Delay(0.3.seconds),
    ClawSubsystem.open,

    // Retract and drive to next position
    ParallelGroup(
        LiftSubsystem.toLow,
        FollowPath(toPickup, holdEnd = true)
    ),

    // Pick up
    ClawSubsystem.close
)()
```

## Breaking Path Following

To stop path following mid-execution:

```kotlin
// In a command
PedroComponent.follower.breakFollowing()
```

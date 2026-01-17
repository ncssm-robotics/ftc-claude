# FTCLib Pure Pursuit

Pure Pursuit is a path tracking algorithm that calculates robot velocity to reach a look-ahead point on a path. FTCLib provides a complete Pure Pursuit implementation with waypoints, retrace recovery, and command integration.

## Imports

```java
import com.arcrobotics.ftclib.purepursuit.Path;
import com.arcrobotics.ftclib.purepursuit.Waypoint;
import com.arcrobotics.ftclib.purepursuit.waypoints.StartWaypoint;
import com.arcrobotics.ftclib.purepursuit.waypoints.GeneralWaypoint;
import com.arcrobotics.ftclib.purepursuit.waypoints.EndWaypoint;
import com.arcrobotics.ftclib.purepursuit.waypoints.PointTurnWaypoint;
import com.arcrobotics.ftclib.purepursuit.waypoints.InterruptWaypoint;
import com.arcrobotics.ftclib.command.PurePursuitCommand;
import com.arcrobotics.ftclib.kinematics.HolonomicOdometry;
```

## How Pure Pursuit Works

1. **Look-Ahead Circle**: Creates a circle of radius `followRadius` around the robot
2. **Path Intersection**: Finds where the circle intersects the path
3. **Target Point**: Drives toward the intersection point
4. **Continuous Update**: Repeats each loop cycle

The robot loosely follows the path, cutting corners based on the follow radius.

## Waypoint Types

### StartWaypoint

The first point in every path. Defines the starting position.

```java
// Basic - just position
Waypoint start = new StartWaypoint(0, 0);

// From Pose2d
Waypoint start = new StartWaypoint(new Pose2d(0, 0, new Rotation2d(0)));
```

### GeneralWaypoint

Standard waypoints along the path. Inherits settings from previous waypoint if not specified.

```java
// Full constructor
Waypoint point = new GeneralWaypoint(
    x,              // X position (inches)
    y,              // Y position (inches)
    rotation,       // Heading (radians)
    movementSpeed,  // Movement speed (0-1)
    turnSpeed,      // Turn speed (0-1)
    followRadius    // Look-ahead radius (inches)
);

// Example
Waypoint point = new GeneralWaypoint(24, 0, Math.toRadians(0), 0.8, 0.5, 12);

// Minimal - inherits previous settings
Waypoint point = new GeneralWaypoint(24, 24);
```

### EndWaypoint

The final point in every path. Requires position buffer and rotation buffer.

```java
Waypoint end = new EndWaypoint(
    x,               // X position
    y,               // Y position
    rotation,        // Final heading (radians)
    movementSpeed,   // Approach speed
    turnSpeed,       // Turn speed
    followRadius,    // Look-ahead radius
    positionBuffer,  // Position tolerance (inches)
    rotationBuffer   // Rotation tolerance (radians)
);

// Example - end at (48, 24) facing 90 degrees
Waypoint end = new EndWaypoint(
    48, 24,
    Math.toRadians(90),
    0.5, 0.5,
    12,
    2.0,  // Within 2 inches
    Math.toRadians(5)  // Within 5 degrees
);
```

### PointTurnWaypoint

Stops at the waypoint, turns to face the target heading, then continues.

```java
Waypoint turn = new PointTurnWaypoint(
    x, y,
    rotation,        // Target heading
    movementSpeed,
    turnSpeed,
    followRadius,
    positionBuffer,  // How close before turning
    rotationBuffer   // Turn tolerance
);

// Example - stop at (24, 0), turn to face 90 degrees
Waypoint turn = new PointTurnWaypoint(
    24, 0,
    Math.toRadians(90),
    0.6, 0.4,
    10,
    2.0, Math.toRadians(3)
);
```

### InterruptWaypoint

Executes a custom action when reached, then continues.

```java
Waypoint interrupt = new InterruptWaypoint(
    x, y,
    movementSpeed,
    turnSpeed,
    followRadius,
    positionBuffer,
    rotationBuffer,
    action  // Runnable to execute
);

// Example - grab sample at waypoint
Waypoint grabPoint = new InterruptWaypoint(
    30, 12,
    0.6, 0.4,
    10,
    2.0, Math.toRadians(5),
    () -> claw.close()  // Action to run
);

// Using method reference
Waypoint intakePoint = new InterruptWaypoint(
    24, 24, 0.5, 0.4, 8, 2.0, Math.toRadians(5),
    intake::run
);
```

## Creating and Following Paths

### Basic Path

```java
// Create waypoints
Waypoint start = new StartWaypoint(0, 0);
Waypoint point1 = new GeneralWaypoint(24, 0, Math.toRadians(0), 0.8, 0.5, 12);
Waypoint point2 = new GeneralWaypoint(24, 24, Math.toRadians(90), 0.6, 0.5, 12);
Waypoint end = new EndWaypoint(0, 24, Math.toRadians(180), 0.5, 0.5, 12, 2, Math.toRadians(5));

// Create path
Path path = new Path(start, point1, point2, end);

// Initialize (required before following)
path.init();

// Follow path
path.followPath(mecanumDrive, odometry);
```

### Manual Loop Control

For more control over path execution:

```java
path.init();

while (!path.isFinished()) {
    // Check for timeout
    if (path.timedOut()) {
        throw new InterruptedException("Path timed out");
    }

    // Get motor powers
    double[] speeds = path.loop(
        robot.getX(),
        robot.getY(),
        robot.getHeading()
    );

    // Apply to drivetrain
    // speeds[0] = strafe, speeds[1] = forward, speeds[2] = turn
    robot.drive(speeds[0], speeds[1], speeds[2]);

    // Update odometry
    robot.updatePose();
}

robot.stop();
```

### Using followPath()

Automatic mode that handles odometry updates:

```java
// followPath() uses suppliers internally
path.followPath(mecanumDrive, holonomicOdometry);
```

## Path Configuration

### Retrace (Recovery)

When the robot loses the path, retrace plots a temporary path back.

```java
// Enabled by default - keep it enabled!
path.enableRetrace();

// Only disable if you have a specific reason
path.disableRetrace();  // Not recommended
```

### Timeouts

Set maximum time for waypoints:

```java
path.setWaypointTimeouts(5000);  // 5 seconds per waypoint
```

### Resetting Paths

For reusing paths:

```java
path.reset();  // Reset before following again
```

## PurePursuitCommand (Command-Based)

For integration with the command system:

```java
// Create odometry subsystem for shared odometry
HolonomicOdometry odometry = new HolonomicOdometry(
    leftEncoder::getDistance,
    rightEncoder::getDistance,
    strafeEncoder::getDistance,
    TRACKWIDTH,
    CENTER_WHEEL_OFFSET
);
OdometrySubsystem odometrySubsystem = new OdometrySubsystem(odometry);

// Create command
PurePursuitCommand followPath = new PurePursuitCommand(
    driveSubsystem,
    odometrySubsystem,
    start, point1, point2, end
);

// Schedule it
followPath.schedule();

// Or use in autonomous sequence
new SequentialCommandGroup(
    new PurePursuitCommand(drive, odom, pathToScoring),
    new ScoreCommand(claw),
    new PurePursuitCommand(drive, odom, pathToParking)
);
```

### Dynamic Waypoint Modification

```java
PurePursuitCommand command = new PurePursuitCommand(drive, odom, start, end);

// Add waypoints
command.addWaypoint(newWaypoint);

// Remove waypoints
command.removeWaypointAtIndex(2);
```

## Odometry Setup

Pure Pursuit requires accurate odometry. See [ODOMETRY.md](ODOMETRY.md) for details.

```java
// Create encoder suppliers
DoubleSupplier leftSupplier = () -> leftEncoder.getDistance();
DoubleSupplier rightSupplier = () -> rightEncoder.getDistance();
DoubleSupplier strafeSupplier = () -> strafeEncoder.getDistance();

// Create odometry
HolonomicOdometry odometry = new HolonomicOdometry(
    leftSupplier,
    rightSupplier,
    strafeSupplier,
    TRACKWIDTH,        // Distance between left and right encoders
    CENTER_WHEEL_OFFSET // Distance from center to strafe encoder
);
```

## Complete Autonomous Example

```java
@Autonomous(name = "Pure Pursuit Auto")
public class PurePursuitAuto extends CommandOpMode {
    private MecanumDrive drive;
    private HolonomicOdometry odometry;
    private OdometrySubsystem odomSubsystem;
    private ClawSubsystem claw;

    // Encoders
    private MotorEx leftEncoder, rightEncoder, strafeEncoder;

    // Constants
    private static final double TRACKWIDTH = 14.0;
    private static final double CENTER_WHEEL_OFFSET = 3.5;
    private static final double TICKS_PER_INCH = 307.699557;

    @Override
    public void initialize() {
        // Setup encoders
        leftEncoder = new MotorEx(hardwareMap, "leftEncoder");
        rightEncoder = new MotorEx(hardwareMap, "rightEncoder");
        strafeEncoder = new MotorEx(hardwareMap, "strafeEncoder");

        leftEncoder.setDistancePerPulse(1.0 / TICKS_PER_INCH);
        rightEncoder.setDistancePerPulse(1.0 / TICKS_PER_INCH);
        strafeEncoder.setDistancePerPulse(1.0 / TICKS_PER_INCH);

        // Create odometry
        odometry = new HolonomicOdometry(
            () -> leftEncoder.getDistance(),
            () -> rightEncoder.getDistance(),
            () -> strafeEncoder.getDistance(),
            TRACKWIDTH,
            CENTER_WHEEL_OFFSET
        );
        odomSubsystem = new OdometrySubsystem(odometry);

        // Create drive
        drive = new MecanumDrive(
            new Motor(hardwareMap, "fl"),
            new Motor(hardwareMap, "fr"),
            new Motor(hardwareMap, "bl"),
            new Motor(hardwareMap, "br")
        );

        // Create claw
        claw = new ClawSubsystem(hardwareMap);

        // Define paths
        Waypoint start = new StartWaypoint(0, 0);
        Waypoint scoringPosition = new GeneralWaypoint(36, 12, Math.toRadians(45), 0.7, 0.5, 10);
        Waypoint scoreEnd = new EndWaypoint(42, 18, Math.toRadians(45), 0.4, 0.4, 8, 2, Math.toRadians(3));

        Waypoint parkStart = new StartWaypoint(42, 18);
        Waypoint parkEnd = new EndWaypoint(48, 48, Math.toRadians(90), 0.6, 0.5, 10, 3, Math.toRadians(5));

        // Schedule autonomous
        schedule(new SequentialCommandGroup(
            // Drive to scoring
            new PurePursuitCommand(drive, odomSubsystem, start, scoringPosition, scoreEnd),

            // Score
            new InstantCommand(claw::open, claw),
            new WaitCommand(500),

            // Park
            new PurePursuitCommand(drive, odomSubsystem, parkStart, parkEnd)
        ));
    }
}
```

## Tuning Tips

### Follow Radius

- **Larger radius**: Smoother curves, cuts corners more
- **Smaller radius**: Tighter tracking, more oscillation

Start with 10-15 inches and adjust.

### Movement Speed

- Start at 0.5-0.6 for testing
- Increase once path is reliable
- Reduce for precise movements

### Position/Rotation Buffers

- Position: 1-3 inches typically
- Rotation: 3-10 degrees typically
- Tighter tolerances = longer completion time

### Trackwidth Tuning

1. Measure physical distance between parallel encoders
2. Have robot spin in place for several rotations
3. Compare expected vs actual rotation
4. Adjust trackwidth: `actual_trackwidth = measured * (expected_turns / actual_turns)`

## Anti-Patterns

### Bad: Forgetting path.init()

```java
Path path = new Path(start, end);
path.followPath(drive, odom);  // Will fail!
```

### Good: Always initialize

```java
Path path = new Path(start, end);
path.init();  // Required!
path.followPath(drive, odom);
```

### Bad: Wrong units

```java
// Mixing degrees and radians
Waypoint end = new EndWaypoint(24, 24, 90, ...);  // Wrong! Should be radians
```

### Good: Use radians consistently

```java
Waypoint end = new EndWaypoint(24, 24, Math.toRadians(90), ...);
```

### Bad: No odometry updates

```java
while (!path.isFinished()) {
    double[] speeds = path.loop(x, y, heading);
    drive.drive(speeds);
    // Missing: odometry.updatePose()!
}
```

### Good: Update odometry every loop

```java
while (!path.isFinished()) {
    double[] speeds = path.loop(
        odometry.getPose().getX(),
        odometry.getPose().getY(),
        odometry.getPose().getHeading()
    );
    drive.drive(speeds);
    odometry.updatePose();  // Critical!
}
```

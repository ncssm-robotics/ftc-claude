# FTCLib Odometry

Odometry tracks your robot's position on the field using encoders. FTCLib provides `HolonomicOdometry` for mecanum and H-drive robots using three dead wheel encoders.

## Imports

```java
import com.arcrobotics.ftclib.kinematics.HolonomicOdometry;
import com.arcrobotics.ftclib.kinematics.Odometry;
import com.arcrobotics.ftclib.command.OdometrySubsystem;
import com.arcrobotics.ftclib.geometry.Pose2d;
import com.arcrobotics.ftclib.geometry.Rotation2d;
import com.arcrobotics.ftclib.hardware.motors.MotorEx;

import java.util.function.DoubleSupplier;
```

## Dead Wheel Configuration

Standard three-wheel odometry uses:
- **Left encoder**: Parallel to robot forward direction, on left side
- **Right encoder**: Parallel to robot forward direction, on right side
- **Strafe encoder**: Perpendicular to robot forward direction (horizontal)

```
        Left        Right
          |   [R]   |
          |    |    |
          |====+====|  <- Strafe (horizontal)
          |         |
          |_________|
            Front
```

## Key Constants

### Trackwidth

Distance between the left and right parallel encoders.

```java
// Measure center-to-center distance in inches
private static final double TRACKWIDTH = 14.5;
```

### Center Wheel Offset

Distance from the robot's center of rotation to the strafe encoder. Positive if strafe encoder is in front of center.

```java
// Measure from center to strafe wheel in inches
private static final double CENTER_WHEEL_OFFSET = 3.5;
```

### Ticks Per Inch

Encoder ticks per inch of wheel travel.

```java
// Calculate: ticks_per_revolution / (wheel_diameter * PI)
// Example: 8192 ticks/rev, 35mm wheel = 1.378" diameter
private static final double TICKS_PER_INCH = 8192 / (1.378 * Math.PI);
// = ~1892 ticks per inch
```

## Setting Up Odometry

### Step 1: Create Encoders

```java
MotorEx leftEncoder = new MotorEx(hardwareMap, "leftEncoder");
MotorEx rightEncoder = new MotorEx(hardwareMap, "rightEncoder");
MotorEx strafeEncoder = new MotorEx(hardwareMap, "strafeEncoder");

// Set distance per pulse for direct distance reading
leftEncoder.setDistancePerPulse(1.0 / TICKS_PER_INCH);
rightEncoder.setDistancePerPulse(1.0 / TICKS_PER_INCH);
strafeEncoder.setDistancePerPulse(1.0 / TICKS_PER_INCH);

// Reset encoders
leftEncoder.resetEncoder();
rightEncoder.resetEncoder();
strafeEncoder.resetEncoder();
```

### Step 2: Create Suppliers

```java
DoubleSupplier leftSupplier = () -> leftEncoder.getDistance();
DoubleSupplier rightSupplier = () -> rightEncoder.getDistance();
DoubleSupplier strafeSupplier = () -> strafeEncoder.getDistance();
```

### Step 3: Create HolonomicOdometry

```java
HolonomicOdometry odometry = new HolonomicOdometry(
    leftSupplier,
    rightSupplier,
    strafeSupplier,
    TRACKWIDTH,
    CENTER_WHEEL_OFFSET
);
```

## Using Odometry

### Update Position

Call `updatePose()` every loop to update the robot's position.

```java
// In your loop
odometry.updatePose();

// Or with manual values
odometry.update(leftDistance, rightDistance, strafeDistance);
```

### Get Current Position

```java
Pose2d pose = odometry.getPose();

double x = pose.getX();           // Forward distance from start
double y = pose.getY();           // Lateral distance from start
double heading = pose.getHeading(); // Heading in radians
double headingDegrees = Math.toDegrees(pose.getHeading());

// Get Rotation2d for field-centric driving
Rotation2d rotation = pose.getRotation();
```

### Reset Position

```java
// Reset to origin
odometry.updatePose(new Pose2d(0, 0, new Rotation2d(0)));

// Reset to specific pose (e.g., starting position)
Pose2d startPose = new Pose2d(24, 12, new Rotation2d(Math.toRadians(90)));
odometry.updatePose(startPose);
```

## OdometrySubsystem (Command-Based)

Wraps odometry for automatic updates through the command scheduler.

```java
// Create odometry subsystem
HolonomicOdometry odometry = new HolonomicOdometry(...);
OdometrySubsystem odometrySubsystem = new OdometrySubsystem(odometry);

// Register with scheduler
register(odometrySubsystem);

// Odometry updates automatically via periodic()
// Access pose from commands
Pose2d pose = odometrySubsystem.getPose();
```

## Complete Setup Example

```java
public class OdometrySubsystemImpl extends SubsystemBase {
    private final MotorEx leftEncoder, rightEncoder, strafeEncoder;
    private final HolonomicOdometry odometry;

    // Tuned constants
    private static final double TRACKWIDTH = 14.5;
    private static final double CENTER_WHEEL_OFFSET = 3.5;
    private static final double TICKS_PER_INCH = 1892.37;

    public OdometrySubsystemImpl(HardwareMap hardwareMap) {
        // Initialize encoders
        leftEncoder = new MotorEx(hardwareMap, "leftOdom");
        rightEncoder = new MotorEx(hardwareMap, "rightOdom");
        strafeEncoder = new MotorEx(hardwareMap, "strafeOdom");

        // Configure distance per pulse
        leftEncoder.setDistancePerPulse(1.0 / TICKS_PER_INCH);
        rightEncoder.setDistancePerPulse(1.0 / TICKS_PER_INCH);
        strafeEncoder.setDistancePerPulse(1.0 / TICKS_PER_INCH);

        // Reverse encoders if needed (depends on mounting)
        rightEncoder.setInverted(true);

        // Create odometry
        odometry = new HolonomicOdometry(
            leftEncoder::getDistance,
            rightEncoder::getDistance,
            strafeEncoder::getDistance,
            TRACKWIDTH,
            CENTER_WHEEL_OFFSET
        );
    }

    @Override
    public void periodic() {
        odometry.updatePose();
    }

    public Pose2d getPose() {
        return odometry.getPose();
    }

    public double getX() {
        return odometry.getPose().getX();
    }

    public double getY() {
        return odometry.getPose().getY();
    }

    public double getHeading() {
        return odometry.getPose().getHeading();
    }

    public double getHeadingDegrees() {
        return Math.toDegrees(getHeading());
    }

    public void resetPose() {
        resetPose(new Pose2d());
    }

    public void resetPose(Pose2d pose) {
        leftEncoder.resetEncoder();
        rightEncoder.resetEncoder();
        strafeEncoder.resetEncoder();
        odometry.updatePose(pose);
    }

    public void resetHeading() {
        resetPose(new Pose2d(getX(), getY(), new Rotation2d(0)));
    }
}
```

## Tuning Odometry

### Step 1: Measure Physical Constants

1. **Trackwidth**: Measure center-to-center distance between parallel encoders
2. **Center offset**: Measure from robot center to strafe encoder
3. **Wheel diameter**: Measure odometry wheel diameter precisely

### Step 2: Calculate Ticks Per Inch

```java
// For REV Through Bore Encoder with 35mm wheel:
// 8192 ticks/rev, 35mm = 1.378" diameter
double TICKS_PER_INCH = 8192 / (1.378 * Math.PI);
```

### Step 3: Tune Trackwidth

1. Push robot forward exactly 48 inches
2. Check reported Y distance
3. Adjust ticks per inch if needed

### Step 4: Tune Heading

1. Spin robot exactly 10 full rotations (3600 degrees)
2. Check reported heading
3. Adjust trackwidth:

```java
// If robot reports more rotation than actual:
TRACKWIDTH = measured_trackwidth * (actual_rotations / reported_rotations);

// If robot reports less rotation than actual:
TRACKWIDTH = measured_trackwidth * (actual_rotations / reported_rotations);
```

### Step 5: Tune Strafe

1. Push robot sideways exactly 48 inches
2. Check reported X distance
3. Adjust center wheel offset or strafe encoder ticks if needed

## Using with Pure Pursuit

```java
// Create odometry
OdometrySubsystemImpl odometry = new OdometrySubsystemImpl(hardwareMap);

// Create Pure Pursuit command
PurePursuitCommand followPath = new PurePursuitCommand(
    driveSubsystem,
    odometry,  // Pass odometry subsystem
    startWaypoint,
    midWaypoint,
    endWaypoint
);
```

## Telemetry for Debugging

```java
@Override
public void periodic() {
    odometry.updatePose();

    // Debug telemetry
    Pose2d pose = odometry.getPose();
    telemetry.addData("X", "%.2f", pose.getX());
    telemetry.addData("Y", "%.2f", pose.getY());
    telemetry.addData("Heading", "%.2f°", Math.toDegrees(pose.getHeading()));
    telemetry.addData("Left Encoder", leftEncoder.getCurrentPosition());
    telemetry.addData("Right Encoder", rightEncoder.getCurrentPosition());
    telemetry.addData("Strafe Encoder", strafeEncoder.getCurrentPosition());
    telemetry.update();
}
```

## Two-Wheel Odometry

For simpler setups with only two parallel encoders and an IMU:

```java
public class TwoWheelOdometry {
    private final MotorEx leftEncoder, rightEncoder;
    private final RevIMU imu;
    private double x, y, heading;
    private double lastLeft, lastRight;

    private static final double TRACKWIDTH = 14.5;
    private static final double TICKS_PER_INCH = 1892.37;

    public void update() {
        double left = leftEncoder.getCurrentPosition() / TICKS_PER_INCH;
        double right = rightEncoder.getCurrentPosition() / TICKS_PER_INCH;

        double deltaLeft = left - lastLeft;
        double deltaRight = right - lastRight;

        double deltaForward = (deltaLeft + deltaRight) / 2.0;
        heading = Math.toRadians(imu.getHeading());

        x += deltaForward * Math.cos(heading);
        y += deltaForward * Math.sin(heading);

        lastLeft = left;
        lastRight = right;
    }
}
```

## Anti-Patterns

### Bad: Not updating every loop

```java
// Only updating sometimes
if (needsUpdate) {
    odometry.updatePose();
}
```

### Good: Update every loop

```java
@Override
public void periodic() {
    odometry.updatePose();  // Always update
}
```

### Bad: Wrong units

```java
// Mixing inches and centimeters
private static final double TRACKWIDTH = 37;  // Oops, centimeters!
```

### Good: Consistent units (inches)

```java
private static final double TRACKWIDTH = 14.5;  // inches
```

### Bad: Not resetting encoders

```java
// Encoders accumulate from previous runs
HolonomicOdometry odometry = new HolonomicOdometry(...);
// Missing encoder reset!
```

### Good: Reset at start

```java
leftEncoder.resetEncoder();
rightEncoder.resetEncoder();
strafeEncoder.resetEncoder();
HolonomicOdometry odometry = new HolonomicOdometry(...);
```

## Common Issues

### Robot drifts during pure forward motion
- Check that parallel encoders are truly parallel
- Verify both encoders have same ticks per inch
- Check for mechanical binding

### Heading accumulates error
- Tune trackwidth more precisely
- Check encoders are centered on wheels
- Verify wheels don't slip

### Strafe distance is wrong
- Tune center wheel offset
- Check strafe encoder is perpendicular
- Verify strafe wheel doesn't slip

### Position jumps
- Check for loose encoder connections
- Verify bulk read mode is enabled
- Check for encoder overflow (use MotorEx for correction)

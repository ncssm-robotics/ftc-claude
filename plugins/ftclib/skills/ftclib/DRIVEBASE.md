# FTCLib Drivebases

FTCLib provides ready-to-use drivetrain classes for common FTC robot configurations, handling the math for arcade, tank, and omnidirectional control.

## Imports

```java
import com.arcrobotics.ftclib.drivebase.RobotDrive;
import com.arcrobotics.ftclib.drivebase.DifferentialDrive;
import com.arcrobotics.ftclib.drivebase.MecanumDrive;
import com.arcrobotics.ftclib.drivebase.HDrive;
import com.arcrobotics.ftclib.hardware.motors.Motor;
```

## RobotDrive Base Class

All drivebases extend `RobotDrive` which provides:

```java
// Set maximum speed (0-1)
drive.setMaxSpeed(0.8);

// Stop all motors
drive.stop();

// Square inputs for finer low-speed control
drive.setSquareInputs(true);

// Clip values to valid range
double clipped = RobotDrive.clipRange(value, -1, 1);

// Normalize wheel speeds
double[] normalized = RobotDrive.normalize(speeds, maxMagnitude);
```

## DifferentialDrive (Tank/West Coast)

Two-motor drivetrain with one motor (or motor group) per side.

### Setup

```java
Motor leftMotor = new Motor(hardwareMap, "left");
Motor rightMotor = new Motor(hardwareMap, "right");

// Right side typically needs to be inverted
rightMotor.setInverted(true);

DifferentialDrive drive = new DifferentialDrive(leftMotor, rightMotor);
```

### Drive Methods

```java
// Arcade drive - single stick
// forward: positive = forward, turn: positive = right
drive.arcadeDrive(forward, turn);

// Tank drive - dual stick
// leftSpeed and rightSpeed: positive = forward
drive.tankDrive(leftSpeed, rightSpeed);
```

### Arcade Drive Example

```java
@TeleOp(name = "Differential TeleOp")
public class DiffTeleOp extends LinearOpMode {
    @Override
    public void runOpMode() {
        Motor left = new Motor(hardwareMap, "left");
        Motor right = new Motor(hardwareMap, "right");
        right.setInverted(true);

        DifferentialDrive drive = new DifferentialDrive(left, right);

        waitForStart();

        while (opModeIsActive()) {
            double forward = -gamepad1.left_stick_y;  // Negate for intuitive control
            double turn = gamepad1.right_stick_x;

            drive.arcadeDrive(forward, turn);
        }
    }
}
```

## MecanumDrive

Four omniwheels for omnidirectional movement.

### Setup

```java
Motor frontLeft = new Motor(hardwareMap, "frontLeft");
Motor frontRight = new Motor(hardwareMap, "frontRight");
Motor backLeft = new Motor(hardwareMap, "backLeft");
Motor backRight = new Motor(hardwareMap, "backRight");

// Right side motors typically inverted
frontRight.setInverted(true);
backRight.setInverted(true);

MecanumDrive drive = new MecanumDrive(frontLeft, frontRight, backLeft, backRight);
```

### Drive Methods

```java
// Robot-centric (relative to robot's perspective)
// strafeSpeed: positive = right
// forwardSpeed: positive = forward
// turnSpeed: positive = clockwise
drive.driveRobotCentric(strafeSpeed, forwardSpeed, turnSpeed);

// Field-centric (relative to field)
// heading: robot's current heading in degrees
drive.driveFieldCentric(strafeSpeed, forwardSpeed, turnSpeed, heading);
```

### Robot-Centric TeleOp

```java
@TeleOp(name = "Mecanum TeleOp")
public class MecanumTeleOp extends LinearOpMode {
    @Override
    public void runOpMode() {
        Motor fl = new Motor(hardwareMap, "fl");
        Motor fr = new Motor(hardwareMap, "fr");
        Motor bl = new Motor(hardwareMap, "bl");
        Motor br = new Motor(hardwareMap, "br");

        fr.setInverted(true);
        br.setInverted(true);

        MecanumDrive drive = new MecanumDrive(fl, fr, bl, br);

        waitForStart();

        while (opModeIsActive()) {
            double strafe = gamepad1.left_stick_x;
            double forward = -gamepad1.left_stick_y;
            double turn = gamepad1.right_stick_x;

            drive.driveRobotCentric(strafe, forward, turn);
        }
    }
}
```

### Field-Centric TeleOp

```java
@TeleOp(name = "Field Centric TeleOp")
public class FieldCentricTeleOp extends LinearOpMode {
    @Override
    public void runOpMode() {
        Motor fl = new Motor(hardwareMap, "fl");
        Motor fr = new Motor(hardwareMap, "fr");
        Motor bl = new Motor(hardwareMap, "bl");
        Motor br = new Motor(hardwareMap, "br");

        fr.setInverted(true);
        br.setInverted(true);

        MecanumDrive drive = new MecanumDrive(fl, fr, bl, br);

        RevIMU imu = new RevIMU(hardwareMap);
        imu.init();

        waitForStart();

        while (opModeIsActive()) {
            double strafe = gamepad1.left_stick_x;
            double forward = -gamepad1.left_stick_y;
            double turn = gamepad1.right_stick_x;
            double heading = imu.getHeading();

            drive.driveFieldCentric(strafe, forward, turn, heading);

            // Reset heading with button
            if (gamepad1.a) {
                imu.reset();
            }
        }
    }
}
```

## HDrive (Holonomic/Kiwi)

Three-wheel holonomic with a perpendicular strafe wheel, or kiwi drive.

### Standard H-Drive (3 wheels)

```java
Motor left = new Motor(hardwareMap, "left");
Motor right = new Motor(hardwareMap, "right");
Motor slide = new Motor(hardwareMap, "slide");  // Perpendicular wheel

HDrive drive = new HDrive(left, right, slide);

// Drive
drive.driveRobotCentric(strafe, forward, turn);
```

### Kiwi Drive (3 omni wheels at angles)

```java
// Default 120-degree spacing
HDrive kiwi = new HDrive(motor1, motor2, motor3);

// Custom angles (in radians)
HDrive kiwi = new HDrive(
    motor1, motor2, motor3,
    Math.toRadians(0),    // Motor 1 angle
    Math.toRadians(120),  // Motor 2 angle
    Math.toRadians(240)   // Motor 3 angle
);
```

## Command-Based Drive Subsystem

### Mecanum Drive Subsystem

```java
public class DriveSubsystem extends SubsystemBase {
    private final MecanumDrive drive;
    private final RevIMU imu;

    private static final double MAX_SPEED = 1.0;

    public DriveSubsystem(HardwareMap hardwareMap) {
        Motor fl = new Motor(hardwareMap, "fl");
        Motor fr = new Motor(hardwareMap, "fr");
        Motor bl = new Motor(hardwareMap, "bl");
        Motor br = new Motor(hardwareMap, "br");

        fr.setInverted(true);
        br.setInverted(true);

        fl.setZeroPowerBehavior(Motor.ZeroPowerBehavior.BRAKE);
        fr.setZeroPowerBehavior(Motor.ZeroPowerBehavior.BRAKE);
        bl.setZeroPowerBehavior(Motor.ZeroPowerBehavior.BRAKE);
        br.setZeroPowerBehavior(Motor.ZeroPowerBehavior.BRAKE);

        drive = new MecanumDrive(fl, fr, bl, br);
        drive.setMaxSpeed(MAX_SPEED);

        imu = new RevIMU(hardwareMap);
        imu.init();
    }

    public void driveRobotCentric(double strafe, double forward, double turn) {
        drive.driveRobotCentric(strafe, forward, turn);
    }

    public void driveFieldCentric(double strafe, double forward, double turn) {
        drive.driveFieldCentric(strafe, forward, turn, imu.getHeading());
    }

    public void stop() {
        drive.stop();
    }

    public void resetHeading() {
        imu.reset();
    }

    public double getHeading() {
        return imu.getHeading();
    }

    public void setMaxSpeed(double speed) {
        drive.setMaxSpeed(speed);
    }
}
```

### Default Drive Command

```java
// In CommandOpMode.initialize()
DriveSubsystem drive = new DriveSubsystem(hardwareMap);
GamepadEx gamepad = new GamepadEx(gamepad1);

// Robot-centric default
drive.setDefaultCommand(new RunCommand(
    () -> drive.driveRobotCentric(
        gamepad.getLeftX(),
        gamepad.getLeftY(),
        gamepad.getRightX()
    ),
    drive
));

// Or field-centric
drive.setDefaultCommand(new RunCommand(
    () -> drive.driveFieldCentric(
        gamepad.getLeftX(),
        gamepad.getLeftY(),
        gamepad.getRightX()
    ),
    drive
));
```

### Slow Mode

```java
// Slow mode while button held
gamepad.getGamepadButton(GamepadKeys.Button.LEFT_BUMPER)
    .whileHeld(new RunCommand(
        () -> drive.driveRobotCentric(
            gamepad.getLeftX() * 0.3,
            gamepad.getLeftY() * 0.3,
            gamepad.getRightX() * 0.3
        ),
        drive
    ));
```

## Motor Direction Guide

### Mecanum Configuration

Looking down at robot from above:

```
    Front
  FL     FR
   \\   //
    \\ //
     []
    // \\
   //   \\
  BL     BR
    Back
```

- **FL (Front Left)**: Forward = counter-clockwise
- **FR (Front Right)**: Forward = clockwise (inverted)
- **BL (Back Left)**: Forward = counter-clockwise
- **BR (Back Right)**: Forward = clockwise (inverted)

### Testing Motor Directions

```java
// Test each motor individually
fl.set(0.3);  // Should move robot forward-right
// Then test fr, bl, br

// If robot spins or strafes wrong, adjust inversions
```

## Wheel Speed Calculations

For autonomous with specific velocities:

```java
// Calculate wheel speeds for desired motion
// vx = strafe velocity, vy = forward velocity, omega = turn rate
double fl = vy + vx + omega;
double fr = vy - vx - omega;
double bl = vy - vx + omega;
double br = vy + vx - omega;

// Normalize if any wheel > 1.0
double max = Math.max(Math.abs(fl), Math.max(Math.abs(fr),
             Math.max(Math.abs(bl), Math.abs(br))));
if (max > 1.0) {
    fl /= max;
    fr /= max;
    bl /= max;
    br /= max;
}
```

## Anti-Patterns

### Bad: Inconsistent motor directions

```java
// Random inversion without understanding
fl.setInverted(true);
fr.setInverted(false);
bl.setInverted(true);
br.setInverted(false);
```

### Good: Understand your drivetrain

```java
// Standard mecanum: right side inverted
fr.setInverted(true);
br.setInverted(true);
// Test and verify with actual robot
```

### Bad: Not using brake mode

```java
// Motors coast when stopped - robot drifts
Motor fl = new Motor(hardwareMap, "fl");
// Missing zero power behavior
```

### Good: Set brake mode for control

```java
Motor fl = new Motor(hardwareMap, "fl");
fl.setZeroPowerBehavior(Motor.ZeroPowerBehavior.BRAKE);
```

### Bad: Hard-coded values

```java
drive.driveRobotCentric(0.5, 0.5, 0.3);  // What do these mean?
```

### Good: Use named variables

```java
double strafe = gamepad.getLeftX();
double forward = gamepad.getLeftY();
double turn = gamepad.getRightX();
drive.driveRobotCentric(strafe, forward, turn);
```

## Tips

1. **Test motors individually** before assembling drivetrain
2. **Use brake mode** for better control
3. **Start slow** when testing new configurations
4. **Field-centric** is preferred for driver comfort
5. **Reset IMU heading** at start of each match pointing same direction

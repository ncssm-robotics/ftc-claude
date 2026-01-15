# FTCLib Hardware

FTCLib provides enhanced hardware wrappers that extend the standard FTC SDK with better control, velocity correction, and easier configuration.

## Imports

```java
// Motors
import com.arcrobotics.ftclib.hardware.motors.Motor;
import com.arcrobotics.ftclib.hardware.motors.MotorEx;
import com.arcrobotics.ftclib.hardware.motors.MotorGroup;
import com.arcrobotics.ftclib.hardware.motors.CRServo;

// Servos
import com.arcrobotics.ftclib.hardware.ServoEx;
import com.arcrobotics.ftclib.hardware.SimpleServo;

// Sensors
import com.arcrobotics.ftclib.hardware.RevIMU;
import com.arcrobotics.ftclib.hardware.SensorColor;
import com.arcrobotics.ftclib.hardware.SensorRevTOFDistance;

// Controllers
import com.arcrobotics.ftclib.controller.PIDController;
import com.arcrobotics.ftclib.controller.PIDFController;
```

## Motor Class

Basic motor wrapper with run modes and encoder support.

### Constructors

```java
// Basic - uses default CPR/RPM
Motor motor = new Motor(hardwareMap, "motorName");

// With GoBILDA preset
Motor motor = new Motor(hardwareMap, "motorName", Motor.GoBILDA.RPM_312);

// Custom CPR and RPM
Motor motor = new Motor(hardwareMap, "motorName", CPR, RPM);
```

### GoBILDA Motor Types

```java
Motor.GoBILDA.RPM_30    // 30 RPM, high torque
Motor.GoBILDA.RPM_43
Motor.GoBILDA.RPM_60
Motor.GoBILDA.RPM_84
Motor.GoBILDA.RPM_117
Motor.GoBILDA.RPM_223
Motor.GoBILDA.RPM_312   // Most common
Motor.GoBILDA.RPM_435
Motor.GoBILDA.RPM_1150
Motor.GoBILDA.RPM_1620  // High speed
Motor.GoBILDA.BARE      // No gearbox
```

### Run Modes

```java
// RawPower - Direct power control, no feedback (default)
motor.setRunMode(Motor.RunMode.RawPower);
motor.set(0.5);  // Set power directly

// PositionControl - PID to target position
motor.setRunMode(Motor.RunMode.PositionControl);
motor.setPositionCoefficient(0.05);  // P gain
motor.setTargetPosition(1000);
motor.set(0.75);  // Max power for PID

// VelocityControl - PID to target velocity
motor.setRunMode(Motor.RunMode.VelocityControl);
motor.setVeloCoefficients(0.05, 0.01, 0.31);  // kP, kI, kD
motor.setFeedforwardCoefficients(0.92, 0.47); // kS, kV
motor.set(0.8);  // Target as fraction of max velocity
```

### Zero Power Behavior

```java
motor.setZeroPowerBehavior(Motor.ZeroPowerBehavior.BRAKE);  // Hold position
motor.setZeroPowerBehavior(Motor.ZeroPowerBehavior.FLOAT);  // Coast
```

### Direction

```java
motor.setInverted(true);
boolean inverted = motor.getInverted();
```

### Encoder Methods

```java
// Reset encoder
motor.resetEncoder();
motor.stopAndResetEncoder();  // Stops motor too

// Read position
int position = motor.getCurrentPosition();
double revolutions = motor.encoder.getRevolutions();

// Distance (if configured)
motor.encoder.setDistancePerPulse(distancePerTick);
double distance = motor.encoder.getDistance();
```

### Position Control Example

```java
Motor liftMotor = new Motor(hardwareMap, "lift", Motor.GoBILDA.RPM_312);
liftMotor.setRunMode(Motor.RunMode.PositionControl);
liftMotor.setPositionCoefficient(0.05);
liftMotor.setZeroPowerBehavior(Motor.ZeroPowerBehavior.BRAKE);
liftMotor.setPositionTolerance(15);  // Encoder ticks

// Go to position
liftMotor.setTargetPosition(1200);
while (!liftMotor.atTargetPosition()) {
    liftMotor.set(0.75);  // Max power
}
liftMotor.stopMotor();
```

## MotorEx Class

Extended motor with corrected velocity and direct velocity control.

```java
MotorEx motor = new MotorEx(hardwareMap, "motor", Motor.GoBILDA.RPM_312);

// Corrected velocity (fixes SDK overflow bug)
double velocity = motor.getVelocity();
double correctedVelocity = motor.getCorrectedVelocity();

// Set velocity directly
motor.setVelocity(500);  // Ticks per second
motor.setVelocity(100, AngleUnit.DEGREES);  // Degrees per second
motor.setVelocity(2, AngleUnit.RADIANS);    // Radians per second
```

## MotorGroup

Control multiple motors as one unit.

```java
// Create group - first motor is the leader
Motor frontLeft = new Motor(hardwareMap, "fl");
Motor backLeft = new Motor(hardwareMap, "bl");

MotorGroup leftSide = new MotorGroup(frontLeft, backLeft);

// All motors receive same commands
leftSide.set(0.5);
leftSide.setZeroPowerBehavior(Motor.ZeroPowerBehavior.BRAKE);
leftSide.setRunMode(Motor.RunMode.RawPower);

// Encoder reads from leader
int position = leftSide.getCurrentPosition();
```

## CRServo (Continuous Rotation Servo)

Motor-like wrapper for continuous rotation servos.

```java
CRServo crServo = new CRServo(hardwareMap, "crServo");

// Use like a motor
crServo.set(1.0);   // Full forward
crServo.set(-1.0);  // Full reverse
crServo.set(0);     // Stop
```

## SimpleServo

Enhanced servo with angle-based control.

```java
// Constructor with angle range
SimpleServo servo = new SimpleServo(
    hardwareMap,
    "servoName",
    0,     // Min angle (degrees)
    270    // Max angle (degrees)
);

// Position control (0.0 to 1.0)
servo.setPosition(0.5);
double position = servo.getPosition();

// Angle control
servo.turnToAngle(135);  // Turn to 135 degrees
servo.rotateByAngle(45); // Rotate 45 degrees from current

// Relative movement
servo.rotateBy(0.1);  // Move 10% of range

// Direction
servo.setInverted(true);

// Custom range
servo.setRange(45, 225);  // New min/max angles
double range = servo.getAngleRange();
```

### Servo Example

```java
public class ClawSubsystem extends SubsystemBase {
    private final SimpleServo clawServo;

    private static final double OPEN_ANGLE = 180;
    private static final double CLOSED_ANGLE = 60;

    public ClawSubsystem(HardwareMap hardwareMap) {
        clawServo = new SimpleServo(hardwareMap, "claw", 0, 270);
    }

    public void open() {
        clawServo.turnToAngle(OPEN_ANGLE);
    }

    public void close() {
        clawServo.turnToAngle(CLOSED_ANGLE);
    }

    public void setAngle(double angle) {
        clawServo.turnToAngle(angle);
    }
}
```

## RevIMU

REV Hub built-in IMU wrapper.

```java
RevIMU imu = new RevIMU(hardwareMap);
imu.init();

// Get heading (degrees)
double heading = imu.getHeading();
double absoluteHeading = imu.getAbsoluteHeading();

// Get as Rotation2d (for odometry)
Rotation2d rotation = imu.getRotation2d();

// Get all angles
double[] angles = imu.getAngles();  // [heading, pitch, roll]

// Reset
imu.reset();
```

## PID Controllers

### PIDController

```java
PIDController pid = new PIDController(kP, kI, kD);

// Set gains individually
pid.setP(0.05);
pid.setI(0.001);
pid.setD(0.01);

// Or all at once
pid.setPID(0.05, 0.001, 0.01);

// Calculate output
double output = pid.calculate(currentPosition, targetPosition);

// With tolerance
pid.setTolerance(10);  // Position tolerance
pid.setTolerance(10, 5);  // Position and velocity tolerance
boolean atTarget = pid.atSetPoint();

// Reset (clears integral)
pid.reset();
```

### PIDFController

Adds feedforward term.

```java
PIDFController pidf = new PIDFController(kP, kI, kD, kF);

// Feedforward helps overcome static friction and gravity
pidf.setF(0.1);

// Calculate with feedforward
double output = pidf.calculate(currentPosition, targetPosition);

// Get coefficients
double[] coeffs = pidf.getCoefficients();  // [kP, kI, kD, kF]
```

### PID Example: Arm Control

```java
public class ArmSubsystem extends SubsystemBase {
    private final MotorEx armMotor;
    private final PIDController pidController;

    private static final double kP = 0.003;
    private static final double kI = 0.0;
    private static final double kD = 0.0001;
    private static final double kF = 0.1;  // Gravity compensation

    private int targetPosition = 0;

    public ArmSubsystem(HardwareMap hardwareMap) {
        armMotor = new MotorEx(hardwareMap, "arm", Motor.GoBILDA.RPM_60);
        armMotor.setZeroPowerBehavior(Motor.ZeroPowerBehavior.BRAKE);
        armMotor.resetEncoder();

        pidController = new PIDController(kP, kI, kD);
        pidController.setTolerance(15);
    }

    public void setTarget(int position) {
        targetPosition = position;
    }

    public boolean atTarget() {
        return pidController.atSetPoint();
    }

    @Override
    public void periodic() {
        // Calculate PID output
        double pid = pidController.calculate(armMotor.getCurrentPosition(), targetPosition);

        // Add feedforward for gravity (arm-specific)
        double ff = kF * Math.cos(Math.toRadians(getArmAngle()));

        armMotor.set(pid + ff);
    }

    private double getArmAngle() {
        // Convert encoder position to angle
        return armMotor.getCurrentPosition() / TICKS_PER_DEGREE;
    }
}
```

## Bulk Reading

Improves cycle time by reading all sensors once per loop.

```java
// In OpMode init
List<LynxModule> hubs = hardwareMap.getAll(LynxModule.class);
for (LynxModule hub : hubs) {
    hub.setBulkCachingMode(LynxModule.BulkCachingMode.AUTO);
}
```

### Bulk Caching Modes

| Mode | Behavior |
|------|----------|
| `OFF` | No caching (default SDK behavior) |
| `AUTO` | Automatic cache clearing each loop |
| `MANUAL` | You control when cache clears |

```java
// Manual mode - clear cache yourself
hub.setBulkCachingMode(LynxModule.BulkCachingMode.MANUAL);

// In loop
for (LynxModule hub : hubs) {
    hub.clearBulkCache();  // Clear at start of each loop
}
// ... read sensors ...
```

## Anti-Patterns

### Bad: Not setting zero power behavior

```java
Motor lift = new Motor(hardwareMap, "lift");
// Lift will coast when stopped - dangerous!
```

### Good: Set brake mode for mechanisms

```java
Motor lift = new Motor(hardwareMap, "lift");
lift.setZeroPowerBehavior(Motor.ZeroPowerBehavior.BRAKE);
```

### Bad: Raw SDK velocity

```java
// SDK velocity has overflow bugs at high speeds
double velocity = motor.motor.getVelocity();
```

### Good: Use MotorEx corrected velocity

```java
MotorEx motor = new MotorEx(hardwareMap, "motor");
double velocity = motor.getCorrectedVelocity();
```

### Bad: Creating motors in commands

```java
public class BadCommand extends CommandBase {
    @Override
    public void initialize() {
        Motor motor = new Motor(hardwareMap, "motor");  // Wrong!
    }
}
```

### Good: Pass hardware through subsystems

```java
public class GoodSubsystem extends SubsystemBase {
    private final Motor motor;

    public GoodSubsystem(HardwareMap hardwareMap) {
        motor = new Motor(hardwareMap, "motor");
    }
}
```

## Hardware Configuration Reference

### Standard Names

```java
// Drive motors
"frontLeft", "frontRight", "backLeft", "backRight"
// or
"fl", "fr", "bl", "br"

// Mechanisms
"lift", "arm", "intake", "slide"

// Servos
"claw", "wrist", "bucket"

// Sensors
"imu", "colorSensor", "distanceSensor"

// Encoders (dead wheels)
"leftEncoder", "rightEncoder", "strafeEncoder"
```

### REV Hub Port Mapping

```
Motors: 0-3 per hub
Servos: 0-5 per hub
I2C: 0-3 per hub
Digital: 0-7 per hub
Analog: 0-3 per hub
```

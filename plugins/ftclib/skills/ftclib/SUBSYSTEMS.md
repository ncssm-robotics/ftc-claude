# FTCLib Subsystems

Subsystems are the organizational unit of robot hardware in FTCLib. They encapsulate motors, sensors, and servos for a specific mechanism and define the interface for controlling them.

## Imports

```java
import com.arcrobotics.ftclib.command.SubsystemBase;
import com.arcrobotics.ftclib.command.Subsystem;
import com.arcrobotics.ftclib.command.CommandScheduler;
import com.arcrobotics.ftclib.hardware.motors.Motor;
import com.arcrobotics.ftclib.hardware.motors.MotorEx;
import com.arcrobotics.ftclib.hardware.SimpleServo;
```

## Why Use Subsystems?

1. **Organization**: Group related hardware and logic together
2. **Conflict Prevention**: Only one command can use a subsystem at a time
3. **Reusability**: Same subsystem works in TeleOp and Autonomous
4. **Testability**: Isolate and test individual mechanisms
5. **Periodic Updates**: Automatic calls for telemetry and state updates

## Creating a Subsystem

### Basic Structure

```java
public class LiftSubsystem extends SubsystemBase {
    // Hardware
    private final Motor liftMotor;

    // State
    private int targetPosition = 0;

    // Constants
    private static final int HIGH_POSITION = 2000;
    private static final int MEDIUM_POSITION = 1200;
    private static final int LOW_POSITION = 400;
    private static final int GROUND_POSITION = 0;
    private static final int POSITION_TOLERANCE = 20;

    public LiftSubsystem(HardwareMap hardwareMap) {
        liftMotor = new Motor(hardwareMap, "lift", Motor.GoBILDA.RPM_312);
        liftMotor.setRunMode(Motor.RunMode.PositionControl);
        liftMotor.setZeroPowerBehavior(Motor.ZeroPowerBehavior.BRAKE);
        liftMotor.setPositionCoefficient(0.05);
    }

    // Public methods for commands to call
    public void setTargetPosition(int position) {
        targetPosition = position;
        liftMotor.setTargetPosition(position);
    }

    public void toHigh() {
        setTargetPosition(HIGH_POSITION);
    }

    public void toMedium() {
        setTargetPosition(MEDIUM_POSITION);
    }

    public void toLow() {
        setTargetPosition(LOW_POSITION);
    }

    public void toGround() {
        setTargetPosition(GROUND_POSITION);
    }

    public boolean atTarget() {
        return Math.abs(liftMotor.getCurrentPosition() - targetPosition) < POSITION_TOLERANCE;
    }

    public int getCurrentPosition() {
        return liftMotor.getCurrentPosition();
    }

    public void setPower(double power) {
        liftMotor.set(power);
    }

    public void stop() {
        liftMotor.set(0);
    }

    @Override
    public void periodic() {
        // Called every scheduler cycle
        // Use for telemetry, state machines, PID updates
    }
}
```

## Subsystem Lifecycle

| Method | When Called | Purpose |
|--------|-------------|---------|
| Constructor | OpMode init | Initialize hardware |
| `periodic()` | Every scheduler run | Telemetry, state updates |

## Registration

Subsystems must be registered with the scheduler.

```java
// In CommandOpMode
@Override
public void initialize() {
    LiftSubsystem lift = new LiftSubsystem(hardwareMap);
    ClawSubsystem claw = new ClawSubsystem(hardwareMap);

    register(lift, claw);  // Register with scheduler
}

// Alternative
CommandScheduler.getInstance().registerSubsystem(lift, claw);
```

## Default Commands

Commands that run when no other command requires the subsystem.

```java
// Drive subsystem with joystick control as default
drive.setDefaultCommand(new RunCommand(
    () -> drive.arcadeDrive(gamepad.getLeftY(), gamepad.getRightX()),
    drive
));

// Intake that stops by default
intake.setDefaultCommand(new RunCommand(intake::stop, intake));
```

## Example Subsystems

### Claw Subsystem

```java
public class ClawSubsystem extends SubsystemBase {
    private final SimpleServo clawServo;

    private static final double OPEN_POSITION = 0.7;
    private static final double CLOSED_POSITION = 0.0;

    public ClawSubsystem(HardwareMap hardwareMap) {
        clawServo = new SimpleServo(hardwareMap, "claw", 0, 270);
    }

    public void open() {
        clawServo.setPosition(OPEN_POSITION);
    }

    public void close() {
        clawServo.setPosition(CLOSED_POSITION);
    }

    public void setPosition(double position) {
        clawServo.setPosition(position);
    }

    public double getPosition() {
        return clawServo.getPosition();
    }
}
```

### Intake Subsystem

```java
public class IntakeSubsystem extends SubsystemBase {
    private final Motor intakeMotor;
    private boolean isRunning = false;

    private static final double INTAKE_POWER = 1.0;
    private static final double OUTTAKE_POWER = -0.7;

    public IntakeSubsystem(HardwareMap hardwareMap) {
        intakeMotor = new Motor(hardwareMap, "intake");
    }

    public void intake() {
        intakeMotor.set(INTAKE_POWER);
        isRunning = true;
    }

    public void outtake() {
        intakeMotor.set(OUTTAKE_POWER);
        isRunning = true;
    }

    public void stop() {
        intakeMotor.set(0);
        isRunning = false;
    }

    public boolean isRunning() {
        return isRunning;
    }

    public void toggle() {
        if (isRunning) {
            stop();
        } else {
            intake();
        }
    }
}
```

### Arm Subsystem with PID

```java
public class ArmSubsystem extends SubsystemBase {
    private final MotorEx armMotor;
    private final PIDController pidController;

    private int targetPosition = 0;

    private static final double kP = 0.005;
    private static final double kI = 0.0;
    private static final double kD = 0.0001;
    private static final int TOLERANCE = 15;

    public ArmSubsystem(HardwareMap hardwareMap) {
        armMotor = new MotorEx(hardwareMap, "arm", Motor.GoBILDA.RPM_60);
        armMotor.setZeroPowerBehavior(Motor.ZeroPowerBehavior.BRAKE);
        armMotor.resetEncoder();

        pidController = new PIDController(kP, kI, kD);
        pidController.setTolerance(TOLERANCE);
    }

    public void setTarget(int position) {
        targetPosition = position;
        pidController.setSetPoint(position);
    }

    public boolean atTarget() {
        return pidController.atSetPoint();
    }

    public void stop() {
        armMotor.set(0);
    }

    @Override
    public void periodic() {
        // Run PID control loop
        double output = pidController.calculate(armMotor.getCurrentPosition());
        armMotor.set(output);
    }
}
```

### Drive Subsystem (Mecanum)

```java
public class DriveSubsystem extends SubsystemBase {
    private final MecanumDrive drive;
    private final Motor frontLeft, frontRight, backLeft, backRight;

    public DriveSubsystem(HardwareMap hardwareMap) {
        frontLeft = new Motor(hardwareMap, "frontLeft");
        frontRight = new Motor(hardwareMap, "frontRight");
        backLeft = new Motor(hardwareMap, "backLeft");
        backRight = new Motor(hardwareMap, "backRight");

        // Reverse right side motors
        frontRight.setInverted(true);
        backRight.setInverted(true);

        drive = new MecanumDrive(frontLeft, frontRight, backLeft, backRight);
    }

    public void driveRobotCentric(double strafe, double forward, double turn) {
        drive.driveRobotCentric(strafe, forward, turn);
    }

    public void driveFieldCentric(double strafe, double forward, double turn, double heading) {
        drive.driveFieldCentric(strafe, forward, turn, heading);
    }

    public void stop() {
        drive.stop();
    }
}
```

## Using periodic()

The `periodic()` method is called every scheduler cycle. Use it for:

### Telemetry Updates

```java
@Override
public void periodic() {
    telemetry.addData("Lift Position", liftMotor.getCurrentPosition());
    telemetry.addData("Lift Target", targetPosition);
    telemetry.addData("At Target", atTarget());
    telemetry.update();
}
```

### State Machine Updates

```java
private enum State { IDLE, INTAKING, TRANSFERRING, SCORING }
private State currentState = State.IDLE;

@Override
public void periodic() {
    switch (currentState) {
        case INTAKING:
            if (sensorDetected()) {
                currentState = State.TRANSFERRING;
                beginTransfer();
            }
            break;
        case TRANSFERRING:
            if (transferComplete()) {
                currentState = State.IDLE;
            }
            break;
        // ... other states
    }
}
```

### Continuous Control Loops

```java
@Override
public void periodic() {
    // Update PID control
    double output = pid.calculate(motor.getCurrentPosition(), targetPosition);
    motor.set(output);
}
```

## Subsystem Patterns

### Factory Methods for Commands

```java
public class LiftSubsystem extends SubsystemBase {
    // ... hardware and methods ...

    // Command factory methods
    public Command toHighCommand() {
        return new InstantCommand(this::toHigh, this);
    }

    public Command toGroundCommand() {
        return new InstantCommand(this::toGround, this);
    }

    public Command waitUntilAtTarget() {
        return new WaitUntilCommand(this::atTarget);
    }

    public Command toHighAndWait() {
        return new SequentialCommandGroup(
            toHighCommand(),
            waitUntilAtTarget()
        );
    }
}
```

### Singleton Pattern (Use Sparingly)

```java
public class LiftSubsystem extends SubsystemBase {
    private static LiftSubsystem instance;

    public static LiftSubsystem getInstance() {
        return instance;
    }

    public LiftSubsystem(HardwareMap hardwareMap) {
        instance = this;
        // ... initialization
    }
}
```

### Multiple Independent Mechanisms

For subsystems with independent degrees of freedom:

```java
public class ArmSubsystem extends SubsystemBase {
    private final SimpleServo clawServo;
    private final SimpleServo wristServo;
    private final Motor extensionMotor;

    // Each mechanism can have its own commands that only require that component
    // This allows parallel operation of independent parts
}
```

## Anti-Patterns

### Bad: Hardware in Commands

```java
// Don't initialize hardware in commands
public class BadCommand extends CommandBase {
    private Motor motor;  // Bad!

    @Override
    public void initialize() {
        motor = new Motor(hardwareMap, "motor");  // Wrong place!
    }
}
```

### Good: Hardware in Subsystems

```java
public class GoodSubsystem extends SubsystemBase {
    private final Motor motor;  // Hardware owned by subsystem

    public GoodSubsystem(HardwareMap hardwareMap) {
        motor = new Motor(hardwareMap, "motor");
    }
}
```

### Bad: Public Hardware Access

```java
public class BadSubsystem extends SubsystemBase {
    public Motor motor;  // Don't expose hardware!
}
```

### Good: Encapsulated Hardware

```java
public class GoodSubsystem extends SubsystemBase {
    private final Motor motor;  // Private

    public void setPower(double power) {  // Public interface
        motor.set(power);
    }
}
```

### Bad: Direct Subsystem Method Calls

```java
// In OpMode loop
while (opModeIsActive()) {
    lift.setTargetPosition(1000);  // Bypasses command system!
    lift.setPower(0.5);
}
```

### Good: Use Commands

```java
// In initialize()
gamepad.getGamepadButton(GamepadKeys.Button.A)
    .whenPressed(new LiftToPositionCommand(lift, 1000));
```

## Telemetry Reference

Always pass telemetry to subsystems that need it:

```java
public class LiftSubsystem extends SubsystemBase {
    private final Telemetry telemetry;

    public LiftSubsystem(HardwareMap hardwareMap, Telemetry telemetry) {
        this.telemetry = telemetry;
        // ... initialization
    }

    @Override
    public void periodic() {
        telemetry.addData("Position", motor.getCurrentPosition());
        telemetry.update();
    }
}

// In CommandOpMode
LiftSubsystem lift = new LiftSubsystem(hardwareMap, telemetry);
```

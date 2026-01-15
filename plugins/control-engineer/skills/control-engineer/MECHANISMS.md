# Mechanism-Specific Control Implementations

Complete implementation examples for each common FTC mechanism type.

## Elevator/Lift

### Physical Characteristics

- Linear vertical motion against gravity
- Gravity force is **constant** at all positions
- Common drives: string/pulley, lead screw, cascade
- Encoder typically measures total extension

### Implementation Checklist

- [ ] Set motor to BRAKE mode
- [ ] Define encoder zero at bottom position
- [ ] Measure kG (power to hold at mid-height)
- [ ] Set position limits (min/max)
- [ ] Add limit switch for homing (optional)
- [ ] Test full range of motion

### Complete Example: Plain FTC SDK

```java
public class ElevatorSubsystem {
    private DcMotorEx motor;
    private ElapsedTime timer = new ElapsedTime();

    // Control constants - TUNE THESE
    private double kP = 0.005;
    private double kI = 0.0;
    private double kD = 0.001;
    private double kG = 0.15;  // Power to hold against gravity

    // State
    private double integral = 0;
    private double lastError = 0;
    private int targetPosition = 0;

    // Limits
    private static final int MIN_POS = 0;
    private static final int MAX_POS = 3000;
    private static final int TOLERANCE = 20;

    public ElevatorSubsystem(HardwareMap hardwareMap) {
        motor = hardwareMap.get(DcMotorEx.class, "elevator");
        motor.setMode(DcMotor.RunMode.STOP_AND_RESET_ENCODER);
        motor.setMode(DcMotor.RunMode.RUN_WITHOUT_ENCODER);
        motor.setZeroPowerBehavior(DcMotor.ZeroPowerBehavior.BRAKE);
        motor.setDirection(DcMotorSimple.Direction.REVERSE); // Adjust as needed
    }

    public void setTarget(int position) {
        targetPosition = Math.max(MIN_POS, Math.min(MAX_POS, position));
        integral = 0; // Reset integral on new target
    }

    public void update() {
        int currentPos = motor.getCurrentPosition();
        double error = targetPosition - currentPos;

        // PID calculations
        integral += error;
        integral = Math.max(-1000, Math.min(1000, integral)); // Anti-windup
        double derivative = error - lastError;
        lastError = error;

        double pidOutput = kP * error + kI * integral + kD * derivative;

        // Feedforward: constant gravity compensation
        double feedforward = kG;

        // Combine and limit
        double output = pidOutput + feedforward;
        output = Math.max(-1.0, Math.min(1.0, output));

        motor.setPower(output);
    }

    public boolean atTarget() {
        return Math.abs(motor.getCurrentPosition() - targetPosition) < TOLERANCE;
    }

    public int getCurrentPosition() {
        return motor.getCurrentPosition();
    }
}
```

### Complete Example: NextFTC (Kotlin)

```kotlin
object ElevatorSubsystem : Subsystem {
    private val motor by lazy {
        ActiveOpMode.hardwareMap.get(DcMotorEx::class.java, "elevator").apply {
            mode = DcMotor.RunMode.STOP_AND_RESET_ENCODER
            mode = DcMotor.RunMode.RUN_WITHOUT_ENCODER
            zeroPowerBehavior = DcMotor.ZeroPowerBehavior.BRAKE
            direction = DcMotorSimple.Direction.REVERSE
        }
    }

    private fun buildController() = ControlSystem.builder()
        .posPid(kP = 0.005, kI = 0.0, kD = 0.001)
        .elevatorFF(kG = 0.15)
        .build()

    private var controller = buildController()
    private var targetPosition = 0

    object Positions {
        const val GROUND = 0
        const val LOW = 1000
        const val MID = 2000
        const val HIGH = 3000
    }

    override fun periodic() {
        controller = buildController() // Rebuild for live tuning
        controller.goal = KineticState(position = targetPosition.toDouble())
        val output = controller.calculate(
            KineticState(position = motor.currentPosition.toDouble())
        )
        motor.power = output.coerceIn(-1.0, 1.0)
    }

    fun goTo(position: Int) = LambdaCommand()
        .setStart { targetPosition = position.coerceIn(0, 3000) }
        .setIsDone { controller.isWithinTolerance(KineticState(position = 20.0)) }
        .requires(this)

    val toGround = goTo(Positions.GROUND)
    val toLow = goTo(Positions.LOW)
    val toMid = goTo(Positions.MID)
    val toHigh = goTo(Positions.HIGH)
}
```

---

## Arm/Pivot

### Physical Characteristics

- Rotates around a fixed pivot point
- Gravity torque = weight × distance × cos(angle)
- Maximum torque at horizontal, zero at vertical
- Zero position definition matters!

### Implementation Checklist

- [ ] Define zero angle (horizontal or vertical?)
- [ ] Calculate ticks per radian conversion
- [ ] Measure kG at horizontal position
- [ ] Set motor to BRAKE mode
- [ ] Define angle limits
- [ ] Account for gear ratio in conversions

### Angle Convention

Choose ONE convention and stick with it:

| Convention | Zero Position | Horizontal | Vertical Up |
|------------|---------------|------------|-------------|
| **Option A** | Horizontal | 0 rad | π/2 rad |
| **Option B** | Vertical down | π/2 rad | 0 rad |

### Complete Example: Plain FTC SDK

```java
public class ArmSubsystem {
    private DcMotorEx motor;

    // Control constants - TUNE THESE
    private double kP = 0.01;
    private double kD = 0.002;
    private double kG = 0.3;  // Power to hold at horizontal

    // Conversion: encoder ticks to radians
    // Example: 28 ticks/rev motor * 50:1 gearbox * (1 rev / 2π rad)
    private double ticksPerRadian = (28 * 50) / (2 * Math.PI);

    // Zero position: arm horizontal = 0 radians
    private double zeroOffsetTicks = 0;

    private double lastError = 0;
    private double targetAngleRad = 0;

    public ArmSubsystem(HardwareMap hardwareMap) {
        motor = hardwareMap.get(DcMotorEx.class, "arm");
        motor.setMode(DcMotor.RunMode.STOP_AND_RESET_ENCODER);
        motor.setMode(DcMotor.RunMode.RUN_WITHOUT_ENCODER);
        motor.setZeroPowerBehavior(DcMotor.ZeroPowerBehavior.BRAKE);
    }

    public void setZeroOffset() {
        // Call this when arm is at horizontal position
        zeroOffsetTicks = motor.getCurrentPosition();
    }

    public void setTargetAngle(double angleRadians) {
        // Limit to safe range (-π/4 to 3π/4 for example)
        targetAngleRad = Math.max(-Math.PI/4, Math.min(3*Math.PI/4, angleRadians));
    }

    public void setTargetDegrees(double degrees) {
        setTargetAngle(Math.toRadians(degrees));
    }

    private double getCurrentAngleRad() {
        double ticks = motor.getCurrentPosition() - zeroOffsetTicks;
        return ticks / ticksPerRadian;
    }

    public void update() {
        double currentAngle = getCurrentAngleRad();
        double error = targetAngleRad - currentAngle;

        // PD control
        double derivative = error - lastError;
        lastError = error;
        double pidOutput = kP * error + kD * derivative;

        // Feedforward: gravity compensation varies with cosine of angle
        // cos(0) = 1 at horizontal, cos(π/2) = 0 at vertical
        double gravityFF = kG * Math.cos(currentAngle);

        double output = pidOutput + gravityFF;
        output = Math.max(-1.0, Math.min(1.0, output));

        motor.setPower(output);
    }

    public boolean atTarget() {
        return Math.abs(getCurrentAngleRad() - targetAngleRad) < Math.toRadians(2);
    }
}
```

### Complete Example: NextFTC (Kotlin)

```kotlin
object ArmSubsystem : Subsystem {
    private val motor by lazy {
        ActiveOpMode.hardwareMap.get(DcMotorEx::class.java, "arm").apply {
            mode = DcMotor.RunMode.STOP_AND_RESET_ENCODER
            mode = DcMotor.RunMode.RUN_WITHOUT_ENCODER
            zeroPowerBehavior = DcMotor.ZeroPowerBehavior.BRAKE
        }
    }

    // Ticks per radian (adjust for your gearing)
    private const val TICKS_PER_RADIAN = 223.4  // Example value

    private fun buildController() = ControlSystem.builder()
        .posPid(kP = 0.01, kI = 0.0, kD = 0.002)
        .armFF(kG = 0.3)  // NextFTC handles cos(angle) internally
        .build()

    private var controller = buildController()
    private var targetAngleRad = 0.0
    private var zeroOffset = 0

    override fun periodic() {
        controller = buildController()
        controller.goal = KineticState(position = targetAngleRad)
        val currentAngle = (motor.currentPosition - zeroOffset) / TICKS_PER_RADIAN
        val output = controller.calculate(KineticState(position = currentAngle))
        motor.power = output.coerceIn(-1.0, 1.0)
    }

    fun setZero() { zeroOffset = motor.currentPosition }

    fun goToAngle(radians: Double) = LambdaCommand()
        .setStart { targetAngleRad = radians.coerceIn(-PI/4, 3*PI/4) }
        .setIsDone { controller.isWithinTolerance(KineticState(position = 0.05)) }
        .requires(this)
}
```

---

## Flywheel/Shooter

### Physical Characteristics

- Continuous rotation at target velocity
- High moment of inertia (slow to speed up/down)
- No position control needed
- Velocity accuracy is critical for consistent shots

### Implementation Checklist

- [ ] Use motor encoder for velocity feedback
- [ ] Measure kV (power per velocity unit)
- [ ] Determine acceptable velocity tolerance (±5%?)
- [ ] Consider spin-up time in autonomous planning
- [ ] May need two motors (counter-rotating)

### Complete Example: Plain FTC SDK

```java
public class FlywheelSubsystem {
    private DcMotorEx motor;

    // Control constants - TUNE THESE
    private double kP = 0.0001;
    private double kV = 0.00015;  // Power per tick/second
    private double kS = 0.05;    // Static friction compensation

    private double targetVelocity = 0;
    private double velocityTolerance = 50;  // ticks/sec

    public FlywheelSubsystem(HardwareMap hardwareMap) {
        motor = hardwareMap.get(DcMotorEx.class, "flywheel");
        motor.setMode(DcMotor.RunMode.RUN_WITHOUT_ENCODER);
        motor.setZeroPowerBehavior(DcMotor.ZeroPowerBehavior.FLOAT);
    }

    public void setTargetVelocity(double velocity) {
        targetVelocity = velocity;
    }

    public void update() {
        if (targetVelocity == 0) {
            motor.setPower(0);
            return;
        }

        double currentVel = motor.getVelocity();
        double error = targetVelocity - currentVel;

        // Feedforward: base power for target velocity
        double velocityFF = kV * targetVelocity;

        // Static friction compensation
        double staticFF = kS * Math.signum(targetVelocity);

        // PID correction
        double pidOutput = kP * error;

        double output = velocityFF + staticFF + pidOutput;
        output = Math.max(-1.0, Math.min(1.0, output));

        motor.setPower(output);
    }

    public boolean atTargetVelocity() {
        return Math.abs(motor.getVelocity() - targetVelocity) < velocityTolerance;
    }

    public double getCurrentVelocity() {
        return motor.getVelocity();
    }

    public void stop() {
        targetVelocity = 0;
        motor.setPower(0);
    }
}
```

### Complete Example: NextFTC (Kotlin)

```kotlin
object FlywheelSubsystem : Subsystem {
    private val motor by lazy {
        ActiveOpMode.hardwareMap.get(DcMotorEx::class.java, "flywheel").apply {
            mode = DcMotor.RunMode.RUN_WITHOUT_ENCODER
            zeroPowerBehavior = DcMotor.ZeroPowerBehavior.FLOAT
        }
    }

    private fun buildController() = ControlSystem.builder()
        .velPid(kP = 0.0001, kI = 0.0, kD = 0.0)
        .basicFF(kV = 0.00015, kS = 0.05)
        .build()

    private var controller = buildController()
    private var targetVelocity = 0.0

    override fun periodic() {
        if (targetVelocity == 0.0) {
            motor.power = 0.0
            return
        }

        controller = buildController()
        controller.goal = KineticState(velocity = targetVelocity)
        val output = controller.calculate(KineticState(velocity = motor.velocity))
        motor.power = output.coerceIn(-1.0, 1.0)
    }

    fun spinUp(velocity: Double) = LambdaCommand()
        .setStart { targetVelocity = velocity }
        .setIsDone { controller.isWithinTolerance(KineticState(velocity = 50.0)) }
        .requires(this)

    fun stop() = LambdaCommand()
        .setStart { targetVelocity = 0.0 }
        .setInstant(true)
}
```

---

## Drivetrain Control

### Recommendation: Use RoadRunner or Pedro Pathing

For drivetrain path following, **do not implement from scratch**. Use:
- **RoadRunner 1.0** - Industry standard, extensive documentation
- **Pedro Pathing** - Simpler API, good for beginners

These libraries handle:
- Odometry/localization
- Motion profiling
- Feedforward (kS, kV, kA)
- Trajectory following PID
- Heading control

### When You Might Need Custom Drivetrain Control

| Scenario | Solution |
|----------|----------|
| Simple teleop drive | Use gamepad inputs directly |
| Field-centric drive | Use IMU for heading, no PID needed |
| Hold heading while driving | Simple heading PID |
| Point turn to angle | Simple heading PID |
| Follow path | Use RoadRunner/Pedro |

### Simple Heading Hold (Teleop)

```java
public class DriveSubsystem {
    private IMU imu;
    private double kP_heading = 0.02;
    private double targetHeading;
    private boolean holdingHeading = false;

    public void enableHeadingHold() {
        targetHeading = imu.getRobotYawPitchRollAngles().getYaw(AngleUnit.RADIANS);
        holdingHeading = true;
    }

    public void disableHeadingHold() {
        holdingHeading = false;
    }

    public double getHeadingCorrection() {
        if (!holdingHeading) return 0;

        double currentHeading = imu.getRobotYawPitchRollAngles().getYaw(AngleUnit.RADIANS);
        double error = normalizeAngle(targetHeading - currentHeading);
        return kP_heading * error;
    }

    private double normalizeAngle(double angle) {
        while (angle > Math.PI) angle -= 2 * Math.PI;
        while (angle < -Math.PI) angle += 2 * Math.PI;
        return angle;
    }
}
```

---

## Multi-Stage Mechanisms

### Cascading Elevator (Two-Stage)

For elevators with multiple stages:

**Option A: Control Total Extension**
- Simpler to program
- Single encoder measures total height
- Both stages move together

**Option B: Control Each Stage**
- More complex
- Allows independent positioning
- Useful if stages have different limits

### Example: Two-Stage Total Extension

```java
public class CascadeElevator {
    private DcMotorEx motor;  // Drives both stages via continuous belt

    // Total extension control (same as single elevator)
    private double kP = 0.003;  // May need lower gains for longer travel
    private double kG = 0.12;   // Gravity compensation

    // The physics are the same - gravity is constant
    // Just adjust gains for the different mechanism response
}
```

### Extending Arm

For arms with extending reach (telescoping):

```java
public class ExtendingArm {
    private DcMotorEx pivotMotor;
    private DcMotorEx extensionMotor;

    private double pivotKG = 0.3;  // Base gravity at horizontal

    // Gravity compensation must account for extension!
    // Longer extension = more torque needed
    private double getGravityFF() {
        double angle = getPivotAngle();
        double extension = getExtension();  // 0.0 to 1.0 normalized

        // Torque scales with extension (moment arm increases)
        double extensionFactor = 0.5 + 0.5 * extension;  // Example scaling

        return pivotKG * extensionFactor * Math.cos(angle);
    }
}
```

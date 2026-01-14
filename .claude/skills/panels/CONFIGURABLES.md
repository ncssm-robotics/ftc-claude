# Panels Configurables

Live-tunable variables accessible from the dashboard.

## Basic Setup

1. Add `@Configurable` annotation to your OpMode
2. Declare `public static` fields for tunable values
3. Access dashboard to modify values in real-time

```java
@Configurable
@TeleOp(name = "Tuning Mode")
public class TuningOpMode extends OpMode {
    // Numeric values
    public static double kP = 0.1;
    public static double kI = 0.0;
    public static double kD = 0.01;
    public static int targetTicks = 1000;

    // Boolean toggles
    public static boolean enablePID = true;
    public static boolean debugMode = false;
}
```

## Supported Types

- `double` - Decimal numbers
- `int` - Integers
- `boolean` - Toggle switches
- `String` - Text values

## PID Tuning Pattern

```java
@Configurable
@TeleOp(name = "PID Tuner")
public class PIDTuner extends OpMode {
    public static double kP = 0.05;
    public static double kI = 0.0;
    public static double kD = 0.0;
    public static double kF = 0.0;
    public static int target = 500;

    private DcMotorEx motor;

    @Override
    public void init() {
        motor = hardwareMap.get(DcMotorEx.class, "motor");
        motor.setMode(DcMotor.RunMode.STOP_AND_RESET_ENCODER);
        motor.setMode(DcMotor.RunMode.RUN_WITHOUT_ENCODER);
    }

    @Override
    public void loop() {
        int current = motor.getCurrentPosition();
        int error = target - current;

        // Simple P control for demo
        double power = error * kP;
        motor.setPower(power);

        // Graph these in dashboard
        telemetry.addData("Target", target);
        telemetry.addData("Current", current);
        telemetry.addData("Error", error);
        telemetry.addData("Power", power);
        telemetry.update();
    }
}
```

## Position Tuning Pattern

```java
@Configurable
@TeleOp(name = "Position Tuner")
public class PositionTuner extends OpMode {
    // Arm positions
    public static int ARM_INTAKE = 0;
    public static int ARM_SCORE = 500;
    public static int ARM_HIGH = 1000;

    // Servo positions
    public static double CLAW_OPEN = 0.7;
    public static double CLAW_CLOSED = 0.3;
}
```

## Tips

- Changes take effect immediately - no restart needed
- Use telemetry to see current values and behavior
- Graph plugin helps visualize response curves
- Save good values to code after tuning session

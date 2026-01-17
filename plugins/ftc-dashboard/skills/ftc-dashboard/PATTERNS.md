# FTC Dashboard Common Patterns

Advanced usage patterns for FTC Dashboard. These examples build on the basics covered in the main skill documentation.

## PID Tuning Setup

A complete PID tuning OpMode with live graph visualization:

```java
@Config
public class PIDConstants {
    public static double kP = 0.0;
    public static double kI = 0.0;
    public static double kD = 0.0;
    public static double TARGET = 0.0;
}

@TeleOp(name = "PID Tuner")
public class PIDTuner extends LinearOpMode {
    @Override
    public void runOpMode() {
        DcMotorEx motor = hardwareMap.get(DcMotorEx.class, "motor");
        motor.setMode(DcMotor.RunMode.RUN_WITHOUT_ENCODER);

        FtcDashboard dashboard = FtcDashboard.getInstance();
        telemetry = new MultipleTelemetry(telemetry, dashboard.getTelemetry());

        double integral = 0;
        double lastError = 0;
        ElapsedTime timer = new ElapsedTime();

        waitForStart();
        timer.reset();

        while (opModeIsActive()) {
            double position = motor.getCurrentPosition();
            double error = PIDConstants.TARGET - position;

            double dt = timer.seconds();
            timer.reset();

            integral += error * dt;
            double derivative = (error - lastError) / dt;
            lastError = error;

            double power = PIDConstants.kP * error
                         + PIDConstants.kI * integral
                         + PIDConstants.kD * derivative;

            motor.setPower(Math.max(-1, Math.min(1, power)));

            // Graph these values
            TelemetryPacket packet = new TelemetryPacket();
            packet.put("target", PIDConstants.TARGET);
            packet.put("position", position);
            packet.put("error", error);
            packet.put("power", power);
            dashboard.sendTelemetryPacket(packet);
        }
    }
}
```

## Robot Position Tracking

Visualize robot position on the field overlay in real-time:

```java
@TeleOp(name = "Position Tracker")
public class PositionTracker extends LinearOpMode {
    @Override
    public void runOpMode() {
        FtcDashboard dashboard = FtcDashboard.getInstance();

        // Your localization system
        Localizer localizer = new ThreeWheelLocalizer(hardwareMap);

        waitForStart();

        while (opModeIsActive()) {
            localizer.update();
            Pose2d pose = localizer.getPoseEstimate();

            TelemetryPacket packet = new TelemetryPacket();

            // Draw robot on field
            Canvas canvas = packet.fieldOverlay();
            canvas.setStroke("blue");
            canvas.strokeCircle(pose.getX(), pose.getY(), 9);

            // Draw heading line
            double headX = pose.getX() + 12 * Math.cos(pose.getHeading());
            double headY = pose.getY() + 12 * Math.sin(pose.getHeading());
            canvas.strokeLine(pose.getX(), pose.getY(), headX, headY);

            // Telemetry data
            packet.put("x", pose.getX());
            packet.put("y", pose.getY());
            packet.put("heading (deg)", Math.toDegrees(pose.getHeading()));

            dashboard.sendTelemetryPacket(packet);
        }
    }
}
```

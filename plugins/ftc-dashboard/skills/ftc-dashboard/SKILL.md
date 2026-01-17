---
name: ftc-dashboard
description: |
  FTC Dashboard by ACME Robotics - web-based dashboard for real-time telemetry visualization,
  live configuration variables, field overlay drawing, and camera streaming. Use when teams
  ask about dashboard setup, telemetry graphing, @Config variables, canvas drawing on field,
  or streaming camera to browser.
license: MIT
metadata:
  category: visualization
  version: 1.0.0
  library-version: 0.5.1
  source: https://acmerobotics.github.io/ftc-dashboard/
---

# FTC Dashboard

React-based web dashboard for monitoring FTC robots during operation.

**Access the dashboard at:** `http://192.168.43.1:8080` (Control Hub) or `http://192.168.49.1:8080` (phone)

## Quick Start

### Installation

1. Add the Maven repository to `build.dependencies.gradle`:

```gradle
repositories {
    maven { url = 'https://maven.brott.dev/' }
}
```

2. Add the dependency:

```gradle
// Standard FTC SDK
implementation 'com.acmerobotics.dashboard:dashboard:0.5.1'

// For OpenRC or non-standard SDK
implementation('com.acmerobotics.dashboard:dashboard:0.5.1') {
    exclude group: 'org.firstinspires.ftc'
}
```

3. Sync Gradle and deploy to robot.

### Basic Telemetry

```java
import com.acmerobotics.dashboard.FtcDashboard;
import com.acmerobotics.dashboard.telemetry.TelemetryPacket;

@TeleOp(name = "Dashboard Demo")
public class DashboardDemo extends LinearOpMode {
    @Override
    public void runOpMode() {
        FtcDashboard dashboard = FtcDashboard.getInstance();

        waitForStart();

        while (opModeIsActive()) {
            TelemetryPacket packet = new TelemetryPacket();
            packet.put("loopTime", getRuntime());
            packet.put("heading", imu.getAngularOrientation().firstAngle);

            dashboard.sendTelemetryPacket(packet);
        }
    }
}
```

## Features

### 1. Telemetry Visualization

Send key-value pairs that appear as live-updating graphs:

```java
TelemetryPacket packet = new TelemetryPacket();

// Numeric values get plotted automatically
packet.put("voltage", batteryVoltage);
packet.put("motorPower", leftMotor.getPower());
packet.put("encoderPosition", encoder.getCurrentPosition());

// String values appear in the telemetry panel
packet.put("status", "Running");
packet.put("targetColor", "RED");

dashboard.sendTelemetryPacket(packet);
```

### 2. MultipleTelemetry (DS + Dashboard)

Send telemetry to both Driver Station and Dashboard simultaneously:

```java
import com.acmerobotics.dashboard.telemetry.MultipleTelemetry;

@TeleOp(name = "Dual Telemetry")
public class DualTelemetryOp extends LinearOpMode {
    @Override
    public void runOpMode() {
        // Wrap both telemetry objects
        telemetry = new MultipleTelemetry(telemetry, FtcDashboard.getInstance().getTelemetry());

        waitForStart();

        while (opModeIsActive()) {
            // This now goes to BOTH DS and Dashboard
            telemetry.addData("Heading", "%.2f", imu.getAngularOrientation().firstAngle);
            telemetry.addData("Power", leftMotor.getPower());
            telemetry.update();  // Sends to both
        }
    }
}
```

### 3. Configuration Variables (@Config)

Live-tunable variables that can be changed from the dashboard without redeploying:

```java
import com.acmerobotics.dashboard.config.Config;

@Config  // Mark class as containing config variables
public class DriveConstants {
    // Must be static and NOT final
    public static double DRIVE_SPEED = 0.8;
    public static double TURN_SPEED = 0.5;
    public static int ENCODER_TICKS_PER_REV = 537;

    // PID tuning values - adjust live!
    public static double kP = 0.05;
    public static double kI = 0.0;
    public static double kD = 0.01;
}
```

Use in your OpMode:

```java
@TeleOp(name = "Tunable Drive")
public class TunableDrive extends LinearOpMode {
    @Override
    public void runOpMode() {
        waitForStart();

        while (opModeIsActive()) {
            // Values update in real-time from dashboard
            double drive = -gamepad1.left_stick_y * DriveConstants.DRIVE_SPEED;
            double turn = gamepad1.right_stick_x * DriveConstants.TURN_SPEED;

            leftMotor.setPower(drive + turn);
            rightMotor.setPower(drive - turn);
        }
    }
}
```

**Dashboard UI:** Variables appear in the "Configuration" tab where you can edit them live.

### 4. Field Overlay (Canvas Drawing)

Draw shapes on the field view to visualize robot position, paths, and targets:

```java
TelemetryPacket packet = new TelemetryPacket();

// Get the canvas for drawing
Canvas canvas = packet.fieldOverlay();

// Set colors (CSS color names or hex)
canvas.setStroke("blue");
canvas.setFill("rgba(0, 0, 255, 0.3)");

// Draw robot position (x, y in inches from field center)
double robotX = 24;  // inches
double robotY = -36;
double robotHeading = Math.toRadians(45);

// Draw robot as a filled circle
canvas.setFill("green");
canvas.fillCircle(robotX, robotY, 9);  // 9-inch radius

// Draw heading indicator
double headingX = robotX + 12 * Math.cos(robotHeading);
double headingY = robotY + 12 * Math.sin(robotHeading);
canvas.setStroke("white");
canvas.setStrokeWidth(3);
canvas.strokeLine(robotX, robotY, headingX, headingY);

// Draw target position
canvas.setStroke("red");
canvas.strokeCircle(48, 0, 6);

dashboard.sendTelemetryPacket(packet);
```

#### Canvas Methods

**Shapes:**
```java
canvas.strokeCircle(x, y, radius);      // Circle outline
canvas.fillCircle(x, y, radius);        // Filled circle
canvas.strokeRect(x, y, width, height); // Rectangle outline
canvas.fillRect(x, y, width, height);   // Filled rectangle
canvas.strokeLine(x1, y1, x2, y2);      // Line segment
canvas.strokePolygon(xPoints, yPoints); // Polygon outline
canvas.fillPolygon(xPoints, yPoints);   // Filled polygon
```

**Styling:**
```java
canvas.setStroke("blue");           // Outline color
canvas.setFill("red");              // Fill color
canvas.setStrokeWidth(2);           // Line thickness
canvas.setAlpha(0.5);               // Transparency (0-1)
```

**Transformations:**
```java
canvas.setTranslation(x, y);        // Move origin
canvas.setRotation(radians);        // Rotate canvas
canvas.setScale(scaleX, scaleY);    // Scale drawing
```

**Text:**
```java
canvas.strokeText(text, x, y, font, rotation);
canvas.fillText(text, x, y, font, rotation);
```

#### Drawing a Path

```java
// Draw a planned path
List<Pose2d> pathPoints = trajectory.getPath();

double[] xPoints = new double[pathPoints.size()];
double[] yPoints = new double[pathPoints.size()];

for (int i = 0; i < pathPoints.size(); i++) {
    xPoints[i] = pathPoints.get(i).getX();
    yPoints[i] = pathPoints.get(i).getY();
}

canvas.setStroke("yellow");
canvas.setStrokeWidth(2);
canvas.strokePolygon(xPoints, yPoints);
```

### 5. Camera Streaming

Stream camera feed to the dashboard for remote viewing:

#### EasyOpenCV

```java
import com.acmerobotics.dashboard.FtcDashboard;
import org.openftc.easyopencv.*;

@TeleOp(name = "Camera Stream")
public class CameraStreamOp extends LinearOpMode {
    @Override
    public void runOpMode() {
        int cameraMonitorViewId = hardwareMap.appContext.getResources()
            .getIdentifier("cameraMonitorViewId", "id", hardwareMap.appContext.getPackageName());

        OpenCvCamera camera = OpenCvCameraFactory.getInstance()
            .createWebcam(hardwareMap.get(WebcamName.class, "Webcam 1"), cameraMonitorViewId);

        camera.openCameraDeviceAsync(new OpenCvCamera.AsyncCameraOpenListener() {
            @Override
            public void onOpened() {
                camera.startStreaming(320, 240, OpenCvCameraRotation.UPRIGHT);

                // Start dashboard stream
                FtcDashboard.getInstance().startCameraStream(camera, 30);
            }

            @Override
            public void onError(int errorCode) {
                telemetry.addData("Camera Error", errorCode);
            }
        });

        waitForStart();

        while (opModeIsActive()) {
            sleep(20);
        }

        // Stop streaming when done
        FtcDashboard.getInstance().stopCameraStream();
    }
}
```

#### Vision Portal (SDK 9.0+)

```java
// Camera streaming with Vision Portal
VisionPortal portal = VisionPortal.easyCreateWithDefaults(
    hardwareMap.get(WebcamName.class, "Webcam 1")
);

// The dashboard can connect to Vision Portal's stream automatically
```

### 6. OpMode Controls

The dashboard provides limited driver station functionality:
- Init/Start/Stop OpModes
- Virtual gamepad input (higher latency than physical)

**Note:** Dashboard gamepads have higher latency. Use for testing only, not competition.

## Common Patterns

See [PATTERNS.md](PATTERNS.md) for complete examples including:
- **PID Tuning Setup** - Live-tunable PID with graphed response
- **Robot Position Tracking** - Field overlay visualization with localizer

## Anti-Patterns

### Don't: Call sendTelemetryPacket Multiple Times Per Loop

```java
// BAD - Multiple packets per loop creates choppy graphs
while (opModeIsActive()) {
    TelemetryPacket packet1 = new TelemetryPacket();
    packet1.put("x", x);
    dashboard.sendTelemetryPacket(packet1);  // First send

    TelemetryPacket packet2 = new TelemetryPacket();
    packet2.put("y", y);
    dashboard.sendTelemetryPacket(packet2);  // Second send - BAD
}

// GOOD - One packet with all data
while (opModeIsActive()) {
    TelemetryPacket packet = new TelemetryPacket();
    packet.put("x", x);
    packet.put("y", y);
    dashboard.sendTelemetryPacket(packet);  // Single send
}
```

### Don't: Make Config Variables Final

```java
// BAD - final prevents dashboard from modifying
@Config
public class Constants {
    public static final double SPEED = 0.5;  // Can't be changed!
}

// GOOD - non-final allows live editing
@Config
public class Constants {
    public static double SPEED = 0.5;  // Editable from dashboard
}
```

### Don't: Forget @Config Annotation

```java
// BAD - Variables won't appear in dashboard
public class TuningConstants {
    public static double kP = 0.1;
}

// GOOD - Class annotated, variables visible
@Config
public class TuningConstants {
    public static double kP = 0.1;
}
```

### Don't: Use Dashboard Gamepad for Competition

```java
// BAD - Dashboard gamepad has high latency
// Don't rely on it during matches

// GOOD - Use dashboard gamepad only for testing
// Always use physical gamepads for competition
```

## Troubleshooting

### Dashboard Not Loading

1. **Check WiFi connection** - Must be connected to robot's WiFi network
2. **Verify URL** - Control Hub: `192.168.43.1:8080`, Phone: `192.168.49.1:8080`
3. **Check if app is running** - Robot Controller app must be active
4. **Clear browser cache** - Hard refresh with Ctrl+Shift+R

### Variables Not Appearing in Config Tab

1. **Check @Config annotation** on the class
2. **Ensure variables are `static`** and NOT `final`
3. **Verify class is in TeamCode** - Must be in your code, not a library
4. **Redeploy after adding @Config**

### Telemetry Not Updating

1. **Check packet is being sent** - `sendTelemetryPacket()` must be called
2. **Verify loop is running** - Add a counter to confirm
3. **Check for exceptions** - Look in logcat for errors

### Field Overlay Not Showing

1. **Enable field view** in dashboard UI
2. **Check coordinate system** - Center is (0,0), units are inches
3. **Verify colors are visible** - Try high-contrast colors

## Coordinate System

The field overlay uses a coordinate system where:
- **Origin (0, 0)** is the center of the field
- **X-axis** runs along the length of the field
- **Y-axis** runs along the width
- **Units** are in inches
- **Rotation** is counter-clockwise from the positive X-axis

```
        +Y
         |
         |
  -X ----+---- +X
         |
         |
        -Y
```

## Resources

- [Official Documentation](https://acmerobotics.github.io/ftc-dashboard/)
- [GitHub Repository](https://github.com/acmerobotics/ftc-dashboard)
- [Javadoc](https://acmerobotics.github.io/ftc-dashboard/javadoc/)
- [Sample Code](https://github.com/acmerobotics/ftc-dashboard/tree/master/TeamCode)

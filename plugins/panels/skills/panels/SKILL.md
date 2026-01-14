---
name: panels
description: Helps use the Panels dashboard for FTC robot debugging, configuration, and telemetry. Use when adding telemetry, creating graphs, making configurable variables, or setting up the Panels dashboard.
license: MIT
compatibility: Claude Code, Codex CLI, VS Code Copilot, Cursor
metadata:
  author: ncssm-robotics
  version: "1.0.0"
  category: tools
---

# Panels Dashboard

Panels (by Lazar/ByteForce) is a web-based dashboard for FTC robots providing telemetry, graphs, and live configuration.

## Setup

Add dependency in `TeamCode/build.gradle`:
```gradle
implementation "com.bylazar:fullpanels:1.0.6"
```

Access dashboard at `192.168.43.1:8001` when connected to robot WiFi.

## Core Plugins

### Telemetry Plugin
Text-based telemetry mirroring Driver Hub output.

```java
// Standard FTC telemetry works automatically
telemetry.addData("Position", follower.getPose());
telemetry.addData("State", pathState);
telemetry.update();
```

### Graph Plugin
Visualize data over time - useful for PID tuning and control system validation.

```java
// Add values to graph in loop()
telemetry.addData("Motor Power", motor.getPower());
telemetry.addData("Target Position", targetPos);
telemetry.addData("Current Position", currentPos);
telemetry.update();  // REQUIRED after adding telemetry
```

### Configurables Plugin
Tunable variables that update in real-time.

```java
@Configurable
public class MyOpMode extends OpMode {
    // These can be adjusted live from dashboard
    public static double kP = 0.1;
    public static double kI = 0.0;
    public static double kD = 0.01;
    public static double targetPosition = 100;
}
```

Use `@Configurable` annotation on your OpMode class, then declare `public static` fields.

### Capture Plugin
Records debugging data for offline replay - debug without robot connected.

## Dashboard Features

### OpMode Control
- Start/stop OpModes from dashboard
- Separate autonomous and teleop sections
- Built-in safety timers

### Gamepad Support
- Two FTC gamepad inputs
- Pre-configured button mapping
- Wireless robot control through dashboard

### Monitoring
- Battery level tracking
- Network latency/delay monitoring
- Automatic plugin update notifications

## Themes & Layout

- Customizable colors
- Resizable widget panels
- Grid-based layout
- Tabbed widget groups

## Usage Pattern

```java
@Configurable
@TeleOp(name = "Debug TeleOp")
public class DebugTeleOp extends OpMode {
    // Live-tunable from dashboard
    public static double driveSpeed = 0.8;
    public static double turnSpeed = 0.6;

    @Override
    public void loop() {
        // Telemetry shows in dashboard
        telemetry.addData("Drive Speed", driveSpeed);
        telemetry.addData("Turn Speed", turnSpeed);
        telemetry.addData("Left Stick Y", gamepad1.left_stick_y);

        // Use configurable values
        double drive = -gamepad1.left_stick_y * driveSpeed;
        double turn = gamepad1.right_stick_x * turnSpeed;

        telemetry.update();
    }
}
```

## Reference

- [CONFIGURABLES.md](CONFIGURABLES.md) - Detailed configurable patterns
- Dashboard URL: `http://192.168.43.1:8001`
- Documentation: https://panels.bylazar.com/docs

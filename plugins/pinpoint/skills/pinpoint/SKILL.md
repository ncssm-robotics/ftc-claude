---
name: pinpoint
description: Helps configure and use the GoBilda Pinpoint odometry computer for robot localization. Use when setting up Pinpoint, configuring pod offsets, troubleshooting LED status, tuning encoders, or integrating with Pedro Pathing.
license: MIT
compatibility: Claude Code, Codex CLI, VS Code Copilot, Cursor
metadata:
  author: ncssm-robotics
  version: "1.1.0"
  category: hardware
---

# GoBilda Pinpoint Odometry Computer

The Pinpoint performs sensor fusion between two dead-wheel odometry pods and an internal IMU at ~1500Hz (vs typical 100-300Hz), providing highly accurate position tracking.

## Quick Start with Pedro Pathing

### 1. Hardware Configuration

In your robot configuration (Driver Station), add the Pinpoint as an I2C device:
- Type: `goBILDA Pinpoint Odometry Computer`
- Name: `pinpoint`
- Port: Any I2C port **except port 0** (reserved for IMU)

### 2. PinpointConstants Setup

In `Constants.java`:

```java
public static PinpointConstants localizerConstants = new PinpointConstants()
    .forwardPodY(0)           // Forward pod Y offset in inches (see POD_OFFSETS.md)
    .strafePodX(-4)           // Strafe pod X offset in inches
    .hardwareMapName("pinpoint")
    .encoderResolution(GoBildaPinpointDriver.GoBildaOdometryPods.goBILDA_4_BAR_POD)
    .forwardEncoderDirection(GoBildaPinpointDriver.EncoderDirection.FORWARD)
    .strafeEncoderDirection(GoBildaPinpointDriver.EncoderDirection.FORWARD);
```

### 3. Add to FollowerBuilder

```java
public static Follower createFollower(HardwareMap hardwareMap) {
    return new FollowerBuilder(followerConstants, hardwareMap)
        .pinpointLocalizer(localizerConstants)
        .mecanumDrivetrain(driveConstants)
        .build();
}
```

## Encoder Resolution Options

| Pod Type | Constant | Ticks/mm |
|----------|----------|----------|
| goBILDA 4-Bar Pod | `goBILDA_4_BAR_POD` | 19.89 |
| goBILDA Swingarm Pod | `goBILDA_SWINGARM_POD` | 13.26 |
| Custom | `.customEncoderResolution(ticks_per_mm)` | - |

## LED Status Reference

| Color | Status | Action |
|-------|--------|--------|
| Green | READY | Normal operation |
| Red | CALIBRATING | Wait ~0.25s |
| Red | NOT_READY | Device initializing |
| Purple | NO_PODS_DETECTED | Check both pod connections |
| Blue | X_POD_NOT_DETECTED | Check forward pod (port X) |
| Orange | Y_POD_NOT_DETECTED | Check strafe pod (port Y) |

## Coordinate System

### Pinpoint Internal
- **X (forward)**: Positive when robot moves forward
- **Y (strafe)**: Positive when robot moves left
- **Heading**: Radians, counterclockwise positive
- **Units**: mm internally (divide by 25.4 for inches)

### Pedro Pathing Integration
When used with Pedro Pathing, coordinates are automatically converted:
- **X**: Positive to the right (field perspective)
- **Y**: Positive toward back wall
- **Origin**: Field corner (0, 0)
- **Units**: Inches

The Pedro Pathing Pinpoint localizer handles all conversions internally.

### Coordinate Conversion (Standalone)
```kotlin
// Pinpoint to Pedro coordinates
fun pinpointToPedro(pinpointPose: Pose2D): Pose {
    // Convert mm to inches
    val xInches = pinpointPose.x / 25.4
    val yInches = pinpointPose.y / 25.4

    // Swap axes (Pinpoint forward = Pedro +Y)
    // Note: Actual mapping depends on robot orientation
    return Pose(yInches, xInches, pinpointPose.heading)
}
```

## Essential Methods (Standalone Use)

```java
// Initialize in init()
pinpoint = hardwareMap.get(GoBildaPinpointDriver.class, "pinpoint");
pinpoint.setOffsets(xOffset_mm, yOffset_mm);
pinpoint.setEncoderResolution(GoBildaPinpointDriver.GoBildaOdometryPods.goBILDA_4_BAR_POD);
pinpoint.resetPosAndIMU();  // MUST be stationary!

// In loop()
pinpoint.update();  // Call every loop to refresh data
Pose2D pos = pinpoint.getPosition();  // x, y in mm; heading in radians
```

## Anti-Patterns

### Don't: Use I2C port 0

```java
// BAD - Port 0 is reserved for internal IMU
// Robot configuration: pinpoint on Port 0  <-- WRONG!

// GOOD - Use any port except 0
// Robot configuration: pinpoint on Port 1, 2, or 3
```

### Don't: Move robot during reset

```java
// BAD - Calibration fails if robot is moving
pinpoint.resetPosAndIMU();
follower.followPath(path);  // Started too soon!

// GOOD - Ensure robot is stationary
pinpoint.resetPosAndIMU();
sleep(300);  // Wait for calibration (LED turns green)
follower.followPath(path);
```

### Don't: Forget to call update()

```java
// BAD - Position data is stale
Pose2D pos = pinpoint.getPosition();  // Same value every loop!

// GOOD - Update before reading
pinpoint.update();
Pose2D pos = pinpoint.getPosition();
```

### Don't: Ignore LED status

```java
// BAD - Using bad data without checking
// LED is purple but code continues anyway

// GOOD - Check status before trusting data
if (pinpoint.getDeviceStatus() == DeviceStatus.READY) {
    Pose2D pos = pinpoint.getPosition();
    // Use position data
}
```

## Reference Documentation

- [HARDWARE_SETUP.md](HARDWARE_SETUP.md) - Physical installation and wiring
- [POD_OFFSETS.md](POD_OFFSETS.md) - Measuring and configuring offsets
- [TUNING.md](TUNING.md) - Encoder direction and yaw scalar tuning
- [API_REFERENCE.md](API_REFERENCE.md) - Complete driver API
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues and fixes

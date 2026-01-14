# Pinpoint Tuning

## Encoder Direction Tuning

### Test Procedure

1. Run the localization test OpMode
2. Push the robot **forward** manually
3. Observe the X coordinate - it should **increase**
4. Push the robot **left** manually
5. Observe the Y coordinate - it should **increase**

### Fixing Reversed Encoders

If X decreases when moving forward:
```java
.forwardEncoderDirection(GoBildaPinpointDriver.EncoderDirection.REVERSED)
```

If Y decreases when moving left:
```java
.strafeEncoderDirection(GoBildaPinpointDriver.EncoderDirection.REVERSED)
```

### Pedro Pathing Configuration

```java
public static PinpointConstants localizerConstants = new PinpointConstants()
    // ... other settings
    .forwardEncoderDirection(GoBildaPinpointDriver.EncoderDirection.REVERSED)
    .strafeEncoderDirection(GoBildaPinpointDriver.EncoderDirection.FORWARD);
```

### Standalone Driver Configuration

```java
pinpoint.setEncoderDirections(
    GoBildaPinpointDriver.EncoderDirection.REVERSED,  // X (forward) encoder
    GoBildaPinpointDriver.EncoderDirection.FORWARD    // Y (strafe) encoder
);
```

## Yaw Scalar Tuning

The Pinpoint comes pre-calibrated, but you can fine-tune if needed.

### When to Tune

Only tune if heading drift is significant. The factory calibration is 0.002% accurate.

### Test Procedure

1. Reset position and IMU
2. Rotate the robot exactly **10 full turns** (3600 degrees)
3. Check the reported heading
4. Calculate: `scalar = 3600 / measured_degrees`

### Applying the Scalar

Pedro Pathing:
```java
.yawScalar(1.02)  // Example: if measured 3529 degrees, scalar = 3600/3529 = 1.02
```

Standalone:
```java
pinpoint.setYawScalar(1.02);
```

### Warning

> The yaw scalar overrides GoBilda's factory calibration. Only modify if there's a clear reason. If you need a scalar outside 0.95-1.05, the device may be defective - contact tech@gobilda.com

## IMU Calibration

### When to Calibrate

- At the start of each match (Autonomous init)
- After power cycling
- If heading drifts while stationary

### Calibration Methods

**Reset Position AND Calibrate IMU** (recommended for match start):
```java
pinpoint.resetPosAndIMU();  // Sets position to (0,0,0) and calibrates
```

**Calibrate IMU Only** (keeps current position):
```java
pinpoint.recalibrateIMU();  // Just recalibrates gyro offset
```

### Critical Requirements

- **Robot MUST be completely stationary** during calibration
- Calibration takes approximately 0.25 seconds
- A bad zero offset causes constant heading drift

## Verifying Tuning

### Straight Line Test

1. Drive robot forward in a straight line
2. X should increase steadily
3. Y should remain near zero
4. Heading should remain near zero

### Square Test

1. Drive in a square pattern, returning to start
2. Final position should be close to (0, 0)
3. Final heading should be close to 0

### Rotation Test

1. Rotate robot 360 degrees in place
2. X and Y should remain stable (minimal drift)
3. Heading should return to starting value

## Current Team Configuration

```java
.forwardEncoderDirection(GoBildaPinpointDriver.EncoderDirection.REVERSED)
.strafeEncoderDirection(GoBildaPinpointDriver.EncoderDirection.FORWARD)
.yawScalar(Math.PI / 3.16744 * Math.PI / 3.10675)  // Custom tuned
```

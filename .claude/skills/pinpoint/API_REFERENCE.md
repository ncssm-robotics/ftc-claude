# Pinpoint Driver API Reference

Complete API for `GoBildaPinpointDriver` class.

## Initialization

```java
GoBildaPinpointDriver pinpoint = hardwareMap.get(GoBildaPinpointDriver.class, "pinpoint");
```

## Configuration Methods

### setOffsets(double xOffset, double yOffset)

Sets odometry pod positions relative to tracking center (in mm).

```java
// xOffset: how far left (+) or right (-) the forward pod is
// yOffset: how far forward (+) or backward (-) the strafe pod is
pinpoint.setOffsets(90.0, -60.0);
```

### setEncoderResolution(GoBildaOdometryPods pods)

Sets encoder resolution for goBILDA pods.

```java
pinpoint.setEncoderResolution(GoBildaPinpointDriver.GoBildaOdometryPods.goBILDA_4_BAR_POD);
// or
pinpoint.setEncoderResolution(GoBildaPinpointDriver.GoBildaOdometryPods.goBILDA_SWINGARM_POD);
```

### setEncoderResolution(double ticks_per_mm)

Sets custom encoder resolution.

```java
pinpoint.setEncoderResolution(15.5);  // Custom ticks per mm
```

### setEncoderDirections(EncoderDirection xEncoder, EncoderDirection yEncoder)

Reverses encoder counting direction.

```java
pinpoint.setEncoderDirections(
    GoBildaPinpointDriver.EncoderDirection.REVERSED,  // X encoder
    GoBildaPinpointDriver.EncoderDirection.FORWARD    // Y encoder
);
```

### setYawScalar(double yawOffset)

Fine-tunes heading measurement (factory calibrated, rarely needed).

```java
pinpoint.setYawScalar(1.02);  // Scalar for heading correction
```

## Calibration Methods

### resetPosAndIMU()

Resets position to (0,0,0) AND recalibrates IMU. **Robot must be stationary!**

```java
pinpoint.resetPosAndIMU();  // ~0.25 seconds
```

### recalibrateIMU()

Recalibrates IMU without resetting position. **Robot must be stationary!**

```java
pinpoint.recalibrateIMU();  // ~0.25 seconds
```

## Update Methods

### update()

**Must call every loop** to read new data from device.

```java
@Override
public void loop() {
    pinpoint.update();
    // Now position data is fresh
}
```

### update(readData data)

Partial update for faster reads (heading only).

```java
pinpoint.update(GoBildaPinpointDriver.readData.ONLY_UPDATE_HEADING);
```

## Position Methods

### getPosition()

Returns current estimated position as Pose2D.

```java
Pose2D pos = pinpoint.getPosition();
double x = pos.getX(DistanceUnit.MM);      // or DistanceUnit.INCH
double y = pos.getY(DistanceUnit.MM);
double heading = pos.getHeading(AngleUnit.RADIANS);  // or AngleUnit.DEGREES
```

### setPosition(Pose2D pos)

Overrides current position (for field coordinates or AprilTag correction).

```java
Pose2D fieldStart = new Pose2D(DistanceUnit.MM, -600, -1200, AngleUnit.DEGREES, 90);
pinpoint.setPosition(fieldStart);
```

### Individual Position Getters

```java
double x = pinpoint.getPosX();        // mm
double y = pinpoint.getPosY();        // mm
double heading = pinpoint.getHeading();  // radians
```

## Velocity Methods

### getVelocity()

Returns current velocity as Pose2D.

```java
Pose2D vel = pinpoint.getVelocity();
double vx = vel.getX(DistanceUnit.MM);     // mm/sec
double vy = vel.getY(DistanceUnit.MM);     // mm/sec
double vHeading = vel.getHeading(AngleUnit.RADIANS);  // rad/sec
```

### Individual Velocity Getters

```java
double vx = pinpoint.getVelX();           // mm/sec
double vy = pinpoint.getVelY();           // mm/sec
double vHeading = pinpoint.getHeadingVelocity();  // rad/sec
```

## Raw Encoder Methods

```java
int xTicks = pinpoint.getEncoderX();  // Raw X encoder value
int yTicks = pinpoint.getEncoderY();  // Raw Y encoder value
```

## Status Methods

### getDeviceStatus()

Returns current device state.

```java
GoBildaPinpointDriver.DeviceStatus status = pinpoint.getDeviceStatus();

switch (status) {
    case READY:
        // Normal operation
        break;
    case CALIBRATING:
        // Wait for calibration
        break;
    case FAULT_NO_PODS_DETECTED:
        // Check pod connections
        break;
    // etc.
}
```

### getLoopTime()

Returns internal loop time in microseconds (normal: 500-1100).

```java
int loopTime = pinpoint.getLoopTime();  // microseconds
```

### getFrequency()

Returns update frequency in Hz (normal: 900-2000).

```java
double freq = pinpoint.getFrequency();  // Hz
```

## Device Info Methods

```java
int id = pinpoint.getDeviceID();       // Should return 1
int version = pinpoint.getDeviceVersion();
float yawScalar = pinpoint.getYawScalar();
float xOffset = pinpoint.getXOffset();  // Separate I2C read - avoid in loop
float yOffset = pinpoint.getYOffset();  // Separate I2C read - avoid in loop
```

## Enums

### DeviceStatus

```java
NOT_READY                 // Powering up (RED LED)
READY                     // Normal operation (GREEN LED)
CALIBRATING               // Recalibrating gyro (RED LED)
FAULT_X_POD_NOT_DETECTED  // Missing X pod (BLUE LED)
FAULT_Y_POD_NOT_DETECTED  // Missing Y pod (ORANGE LED)
FAULT_NO_PODS_DETECTED    // Both pods missing (PURPLE LED)
FAULT_IMU_RUNAWAY         // IMU error
```

### EncoderDirection

```java
FORWARD   // Normal counting direction
REVERSED  // Inverted counting direction
```

### GoBildaOdometryPods

```java
goBILDA_4_BAR_POD      // 48mm wheel, 19.89 ticks/mm
goBILDA_SWINGARM_POD   // 32mm wheel, 13.26 ticks/mm
```

### readData

```java
ONLY_UPDATE_HEADING  // Fast read, heading only
```

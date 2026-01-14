# Pinpoint Troubleshooting

## LED Status Diagnostics

| LED Color | Status | Cause | Solution |
|-----------|--------|-------|----------|
| Green | READY | Normal | No action needed |
| Red (brief) | CALIBRATING | IMU calibrating | Wait ~0.25 seconds |
| Red (persistent) | NOT_READY | Device initializing | Wait for startup |
| Purple | NO_PODS_DETECTED | Both pods disconnected | Check X and Y pod cables |
| Blue | X_POD_NOT_DETECTED | Forward pod issue | Check port X connection |
| Orange | Y_POD_NOT_DETECTED | Strafe pod issue | Check port Y connection |

## Common Issues

### Position Drifts While Stationary

**Symptoms**: X, Y, or heading slowly changes when robot is not moving

**Causes & Solutions**:
1. **Bad IMU calibration**: Call `resetPosAndIMU()` with robot completely still
2. **Vibration during calibration**: Ensure no motors running during init
3. **Loose odometry pods**: Check pod mounting and wheel contact

### Encoder Values Not Changing

**Symptoms**: `getEncoderX()` or `getEncoderY()` returns 0 or constant value

**Causes & Solutions**:
1. **Pod not connected**: Check LED status for fault colors
2. **Cable damage**: Try different cable
3. **Pod wheel not touching ground**: Adjust pod mounting pressure

### Heading Drifts During Movement

**Symptoms**: Heading gradually becomes incorrect over time

**Causes & Solutions**:
1. **Yaw scalar needs tuning**: Perform 10-rotation test (see TUNING.md)
2. **Pod offsets incorrect**: Verify offset measurements
3. **Wheel slippage**: Check odometry wheel condition and contact

### Position Drifts During Pure Rotation

**Symptoms**: X or Y changes when robot spins in place

**Causes & Solutions**:
1. **Incorrect pod offsets**: Re-measure distances from center of rotation
2. **Wrong offset signs**: Check positive/negative directions

### Coordinates Move Wrong Direction

**Symptoms**: X decreases when moving forward, or Y decreases when moving left

**Solution**: Reverse the appropriate encoder direction:
```java
.forwardEncoderDirection(GoBildaPinpointDriver.EncoderDirection.REVERSED)
// or
.strafeEncoderDirection(GoBildaPinpointDriver.EncoderDirection.REVERSED)
```

### "I2C device not found" Error

**Causes & Solutions**:
1. **Wrong port**: Don't use port 0 (reserved for IMU)
2. **Wrong hardware map name**: Ensure name matches code (`"pinpoint"`)
3. **Cable not seated**: Reseat I2C cable on both ends
4. **Wrong device type**: Configure as "goBILDA Pinpoint Odometry Computer"

### SDK v11.0 Compatibility

If upgrading from older SDK, Pedro Pathing v2.0+ includes the Pinpoint driver. Remove any local `GoBildaPinpointDriver.java` if using Pedro's built-in:

```java
import com.qualcomm.hardware.gobilda.GoBildaPinpointDriver;  // SDK/Pedro version
// NOT
import edu.ncssm.aperture.base.GoBildaPinpointDriver;  // Local version
```

## Performance Verification

### Check Loop Frequency

```java
telemetry.addData("Pinpoint Hz", pinpoint.getFrequency());
telemetry.addData("Loop Time (us)", pinpoint.getLoopTime());
telemetry.update();  // REQUIRED after adding telemetry
```

**Normal values**:
- Frequency: 900-2000 Hz
- Loop Time: 500-1100 microseconds

**If outside range**: Device may be defective - contact tech@gobilda.com

### Check Device Status in Code

```java
@Override
public void loop() {
    pinpoint.update();

    if (pinpoint.getDeviceStatus() != GoBildaPinpointDriver.DeviceStatus.READY) {
        telemetry.addData("WARNING", "Pinpoint status: " + pinpoint.getDeviceStatus());
    }

    telemetry.update();  // REQUIRED after adding telemetry
}
```

## Unit Conversion Reference

The Pinpoint internally uses millimeters and radians.

```java
// Convert mm to inches
double inches = pinpoint.getPosX() / 25.4;

// Convert radians to degrees
double degrees = Math.toDegrees(pinpoint.getHeading());

// Or use Pose2D unit methods
Pose2D pos = pinpoint.getPosition();
double xInches = pos.getX(DistanceUnit.INCH);
double headingDeg = pos.getHeading(AngleUnit.DEGREES);
```

## Factory Reset

If you've applied incorrect settings:
1. Power cycle the device
2. Reconfigure offsets and encoder resolution
3. Call `resetPosAndIMU()` when stationary

## Getting Help

- **Device issues**: tech@gobilda.com
- **Pedro Pathing**: [pedropathing.com](https://pedropathing.com)
- **FTC Community**: [ftc-community.firstinspires.org](https://ftc-community.firstinspires.org)

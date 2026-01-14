# Pinpoint Hardware Setup

## Physical Specifications

- **Weight**: 40g (including wire and mounting hardware)
- **Dimensions**: 4.50" x 3.00" x 1.00"
- **Operating Voltage**: 3.3-5V
- **Current Draw**: 100mA
- **I2C Address**: 0x31 (default)

## Wiring Overview

```
REV Hub I2C Port (NOT port 0) ─────► Pinpoint
                                        │
        ┌───────────────────────────────┴───────────────────────────────┐
        │                                                               │
        ▼                                                               ▼
   Port X (Forward Pod)                                        Port Y (Strafe Pod)
   Parallel to chassis length                              Perpendicular to chassis
```

## Pod Connections

**Forward Pod (Port X)**:
- Mounted parallel to the robot's length
- Should increase when robot moves **forward**

**Strafe Pod (Port Y)**:
- Mounted perpendicular to the robot's length
- Should increase when robot moves **left**

## Connector Types

- **Encoder Connector**: 4-Position JST PH (FH-MC)
- **Included Cable**: JST PH Cable (4-Pos, MH-FC to MH-FC, 600mm)

## I2C Connection to REV Hub

**IMPORTANT**: Connect to any I2C port **except port 0** (port 0 is reserved for the built-in IMU)

### Driver Station Configuration

1. Configure Robot > Add I2C Device
2. Select port (1, 2, or 3)
3. Device Type: `goBILDA Pinpoint Odometry Computer`
4. Name: `pinpoint` (must match hardwareMapName in code)

## Mounting Considerations

- Mount rigidly to prevent vibration
- Keep away from motors and high-current wiring (EMI)
- Ensure odometry pods maintain consistent ground contact
- The Pinpoint should be mounted where it won't be impacted during matches

## Compatible Odometry Pods

| Pod Type | SKU | Wheel Size | Ticks/mm |
|----------|-----|------------|----------|
| goBILDA 4-Bar Pod | 3110-0001-0002 | 48mm | 19.89 |
| goBILDA Swingarm Pod | 3110-0001-0001 | 32mm | 13.26 |

Any quadrature encoder dead-wheel system is compatible - use `setEncoderResolution(ticks_per_mm)` for custom pods.

## Performance Specifications

- **Algorithm Update Rate**: ~1500Hz
- **Position Update Interval**: 0.00065 seconds
- **Max Encoder Speed**: 256,000 countable events/second
- **Max Gyro Speed**: 2,000 RPM
- **IMU Calibration Accuracy**: 0.002% (pre-calibrated from factory)

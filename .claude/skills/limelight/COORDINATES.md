# Limelight Coordinate Systems

## Camera Coordinate System

The Limelight camera uses a standard computer vision coordinate system:

```
        ^ +ty (up)
        |
        |
+tx <---+---> -tx
(left)  |     (right)
        |
        v -ty (down)
```

- **tx**: Horizontal offset in degrees (-27° to +27°)
  - Positive = target is LEFT of crosshair
  - Negative = target is RIGHT of crosshair
- **ty**: Vertical offset in degrees (-20.5° to +20.5°)
  - Positive = target is ABOVE crosshair
  - Negative = target is BELOW crosshair

## MegaTag2 / Botpose Coordinate System

Botpose returns robot position in FTC field coordinates (meters and degrees):

```
FTC Field (looking from driver station):

        ^ +Y (away from driver station)
        |
        |
        +---> +X (right)
       /
      v +Z (up)

Heading: 0° = facing +X, CCW positive
```

## Pedro Pathing Coordinate System

```
Pedro (origin at field corner):

        ^ +Y (up the field)
        |
        |
Origin  +---> +X (right)
(0,0)

Heading: 0° = facing +X (right), CCW positive
```

## Conversion: Botpose to Pedro

The FTC field center is at (72, 72) in Pedro coordinates (144" field).

```kotlin
object CoordinateConversion {
    const val FIELD_SIZE_INCHES = 144.0
    const val INCHES_PER_METER = 39.3701
    const val FIELD_CENTER = FIELD_SIZE_INCHES / 2  // 72 inches

    /**
     * Convert Limelight botpose (FTC coordinates) to Pedro Pathing pose.
     *
     * FTC: Origin at field center, X right, Y forward, meters
     * Pedro: Origin at corner, X right, Y up, inches
     */
    fun botposeToPedro(botpose: Pose3D): Pose {
        // Convert meters to inches
        val xInches = botpose.position.x * INCHES_PER_METER
        val yInches = botpose.position.y * INCHES_PER_METER

        // Shift origin from center to corner
        val pedroX = xInches + FIELD_CENTER
        val pedroY = yInches + FIELD_CENTER

        // Heading is already CCW positive, just convert to radians
        val headingRadians = Math.toRadians(botpose.orientation.yaw)

        return Pose(pedroX, pedroY, headingRadians)
    }

    /**
     * Convert Pedro Pathing pose to FTC coordinates (for Limelight input).
     */
    fun pedroToFTC(pedroPose: Pose): DoubleArray {
        // Shift origin from corner to center
        val ftcX = (pedroPose.x - FIELD_CENTER) / INCHES_PER_METER
        val ftcY = (pedroPose.y - FIELD_CENTER) / INCHES_PER_METER

        // Convert heading to degrees
        val headingDegrees = Math.toDegrees(pedroPose.heading)

        return doubleArrayOf(ftcX, ftcY, 0.0, 0.0, 0.0, headingDegrees)
    }
}
```

## Turret Aim Conversion

When aiming the turret based on Limelight tx:

```kotlin
// tx is degrees from camera center
// Positive tx = target is to the LEFT
// To aim at target, turret should rotate LEFT (positive direction)

fun aimTurret(tx: Double): Int {
    // Calibrate TICKS_PER_DEGREE for your turret gear ratio
    val TICKS_PER_DEGREE = 10.0

    // tx is already in the right direction for turret rotation
    return (tx * TICKS_PER_DEGREE).toInt()
}
```

## AprilTag Field Positions

DECODE 2025-2026 AprilTag positions (in Pedro coordinates):

| Tag ID | X (in) | Y (in) | Description |
|--------|--------|--------|-------------|
| 11 | 0 | 72 | Left wall center |
| 12 | 72 | 144 | Back wall center |
| 13 | 144 | 72 | Right wall center |
| 14 | 72 | 0 | Audience wall center |

*Note: Actual DECODE tag positions TBD - these are placeholders*

## Best Practices

1. **Latency Compensation**: Account for vision latency when using botpose
   ```kotlin
   val latencySeconds = (result.captureLatency + result.targetingLatency) / 1000.0
   // Adjust pose based on robot velocity and latency
   ```

2. **Filtering**: Apply low-pass filter to reduce noise
   ```kotlin
   filteredTx = filteredTx * 0.8 + result.tx * 0.2
   ```

3. **Multi-Tag**: MegaTag2 uses multiple AprilTags for more accurate localization

4. **Mount Calibration**: Configure camera offset in Limelight web UI for accurate botpose

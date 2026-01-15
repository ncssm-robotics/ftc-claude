# RoadRunner Coordinate Systems

## RoadRunner Coordinate System

RoadRunner uses a **center-origin** coordinate system with inches and radians:

```
RoadRunner (origin at field CENTER):

          ^ +Y (72")
          |
          |
-X <------+------> +X
(-72")    |        (72")
          |
          v -Y (-72")

Heading: 0 rad = facing +X (right), CCW positive
Field size: 144" x 144" (-72" to +72" on each axis)
```

**Key characteristics:**
- Origin at field center (0, 0)
- Units in **inches**
- Heading in **radians**
- 0 radians = facing right (+X direction)
- Counter-clockwise rotation is positive

## Pedro Pathing Coordinate System

```
Pedro (origin at field CORNER):

          ^ +Y (144")
          |
          |
Origin    +------> +X (144")
(0,0)

Heading: 0 rad = facing +X (right), CCW positive
Field size: 144" x 144" (0" to 144" on each axis)
```

## FTC / Limelight Coordinate System

```
FTC (origin at field CENTER):

          ^ +Y (~1.83m)
          |
          |
-X <------+------> +X
          |
          v -Y

Heading: 0° = facing +X (right), CCW positive
Field size: ~3.66m x 3.66m
```

**Key characteristics:**
- Origin at field center
- Units in **meters**
- Heading in **degrees**

## Conversion Summary

| From | To | X Transform | Y Transform | Heading |
|------|-----|-------------|-------------|---------|
| RoadRunner | Pedro | x + 72 | y + 72 | same (radians) |
| Pedro | RoadRunner | x - 72 | y - 72 | same (radians) |
| RoadRunner | FTC | x × 0.0254 | y × 0.0254 | rad → deg |
| FTC | RoadRunner | x × 39.37 | y × 39.37 | deg → rad |

## Kotlin Reference Implementation

```kotlin
object CoordinateConversion {
    const val FIELD_SIZE_INCHES = 144.0
    const val FIELD_CENTER_INCHES = 72.0
    const val INCHES_PER_METER = 39.3701
    const val METERS_PER_INCH = 0.0254

    /**
     * Convert RoadRunner pose to Pedro Pathing pose.
     * Both use inches and radians, but different origins.
     */
    fun roadRunnerToPedro(pose: Pose2d): Pose {
        return Pose(
            pose.position.x + FIELD_CENTER_INCHES,
            pose.position.y + FIELD_CENTER_INCHES,
            pose.heading.toDouble()
        )
    }

    /**
     * Convert Pedro Pathing pose to RoadRunner pose.
     */
    fun pedroToRoadRunner(pose: Pose): Pose2d {
        return Pose2d(
            pose.x - FIELD_CENTER_INCHES,
            pose.y - FIELD_CENTER_INCHES,
            pose.heading
        )
    }

    /**
     * Convert RoadRunner pose to FTC coordinates (meters, degrees).
     * Useful for Limelight botpose comparison.
     */
    fun roadRunnerToFTC(pose: Pose2d): DoubleArray {
        return doubleArrayOf(
            pose.position.x * METERS_PER_INCH,
            pose.position.y * METERS_PER_INCH,
            0.0, // z
            0.0, // roll
            0.0, // pitch
            Math.toDegrees(pose.heading.toDouble())
        )
    }

    /**
     * Convert FTC/Limelight botpose to RoadRunner pose.
     */
    fun ftcToRoadRunner(botpose: DoubleArray): Pose2d {
        return Pose2d(
            botpose[0] * INCHES_PER_METER,
            botpose[1] * INCHES_PER_METER,
            Math.toRadians(botpose[5])
        )
    }

    /**
     * Mirror a red alliance pose for blue alliance.
     * In RoadRunner coords, X is mirrored around 0.
     */
    fun mirrorForBlue(redPose: Pose2d): Pose2d {
        return Pose2d(
            -redPose.position.x,
            redPose.position.y,
            normalizeRadians(Math.PI - redPose.heading.toDouble())
        )
    }

    private fun normalizeRadians(angle: Double): Double {
        var a = angle
        while (a > Math.PI) a -= 2 * Math.PI
        while (a < -Math.PI) a += 2 * Math.PI
        return a
    }
}
```

## Common Starting Positions

### Red Alliance (RoadRunner coordinates)

| Position | X (in) | Y (in) | Heading (rad) | Description |
|----------|--------|--------|---------------|-------------|
| Far | 12 | -62 | π/2 | Right side, facing forward |
| Near | -36 | -62 | π/2 | Left side, facing forward |

### Blue Alliance (mirrored)

| Position | X (in) | Y (in) | Heading (rad) | Description |
|----------|--------|--------|---------------|-------------|
| Far | -12 | -62 | π/2 | Left side, facing forward |
| Near | 36 | -62 | π/2 | Right side, facing forward |

## Tile Coordinates

The field is 6×6 tiles, each 24" × 24".

```
Tile grid (in Pedro coordinates):

  5 |   |   |   |   |   |   |
  4 |   |   |   |   |   |   |
  3 |   |   |   |   |   |   |
  2 |   |   |   |   |   |   |
  1 |   |   |   |   |   |   |
  0 |   |   |   |   |   |   |
    +---+---+---+---+---+---+
      0   1   2   3   4   5
```

To convert tile to RoadRunner:
```kotlin
fun tileToRoadRunner(tileX: Int, tileY: Int): Vector2d {
    val pedroX = tileX * 24.0 + 12.0  // tile center
    val pedroY = tileY * 24.0 + 12.0
    return Vector2d(pedroX - 72.0, pedroY - 72.0)
}
```

## Using the Conversion Script

```bash
# Convert RoadRunner pose to all coordinate systems
uv run scripts/convert.py all 12 -62 1.57

# Convert from Pedro to RoadRunner
uv run scripts/convert.py pedro-to-roadrunner 84 10 1.57

# Mirror red pose for blue alliance
uv run scripts/convert.py mirror-blue 12 -62 1.57

# Get RoadRunner coords for tile center
uv run scripts/convert.py tile-center 2 3
```

## Best Practices

1. **Pick one coordinate system** for your codebase and stick with it
2. **Convert at boundaries** - when receiving Limelight data or sharing with other libraries
3. **Use constants** for starting positions rather than hardcoding numbers
4. **Test conversions** with known positions (field center, corners, etc.)

### Example: Combining RoadRunner with Limelight

```kotlin
class LocalizationFusion(
    private val drive: MecanumDrive,
    private val limelight: Limelight3A
) {
    fun update() {
        // Get Limelight pose (FTC coordinates)
        val result = limelight.latestResult
        if (result.isValid && result.botpose != null) {
            // Convert to RoadRunner coordinates
            val visionPose = CoordinateConversion.ftcToRoadRunner(result.botpose)

            // Fuse with odometry (example: weighted average)
            val odomPose = drive.pose
            val fusedPose = Pose2d(
                odomPose.position.x * 0.7 + visionPose.position.x * 0.3,
                odomPose.position.y * 0.7 + visionPose.position.y * 0.3,
                odomPose.heading  // Trust odometry for heading
            )

            drive.pose = fusedPose
        }
    }
}
```

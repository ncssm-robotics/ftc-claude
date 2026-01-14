# DECODE Field Positions (Pedro Coordinates)

All positions are in Pedro Pathing coordinate system:
- Origin: Field corner (audience-side, left when facing field)
- X: Increases toward right (0 to 144 inches)
- Y: Increases toward back wall (0 to 144 inches)
- Heading: 0° = facing +X (right), CCW positive

## Coordinate System

```
Pedro Pathing Coordinates:

        ^ +Y (144")
        |
        |
(0,0)   +---> +X (144")

Heading: 0° = facing right
         90° = facing back wall
         180° = facing left
         -90° / 270° = facing audience
```

## Starting Positions

| Alliance | Position | X (in) | Y (in) | Heading (rad) | Notes |
|----------|----------|--------|--------|---------------|-------|
| Red | Start Left | 7.0 | 6.75 | 0 | Facing right |
| Red | Start Right | 7.0 | 137.25 | 0 | Facing right |
| Blue | Start Left | 137.0 | 137.25 | π | Facing left |
| Blue | Start Right | 137.0 | 6.75 | π | Facing left |

## Scoring Zones

*Note: Verify these positions with official field CAD*

| Zone | X (in) | Y (in) | Heading (rad) | Description |
|------|--------|--------|---------------|-------------|
| High Goal Left | 24 | 120 | π/2 | Left side scoring |
| High Goal Right | 120 | 120 | π/2 | Right side scoring |
| Low Goal Left | 24 | 100 | π/2 | Lower scoring option |
| Low Goal Right | 120 | 100 | π/2 | Lower scoring option |

## Classifier

| Position | X (in) | Y (in) | Description |
|----------|--------|--------|-------------|
| Classifier Entry | 24 | 72 | Where artifacts enter |
| Classifier Center | 36 | 72 | Center of mechanism |

## Artifact Pickup Locations

| Location | X (in) | Y (in) | Notes |
|----------|--------|--------|-------|
| Pickup 1 | 36 | 24 | Near start |
| Pickup 2 | 36 | 48 | Mid field |
| Pickup 3 | 72 | 48 | Center field |
| Pickup 4 | 108 | 48 | Far side |

## AprilTag Positions

| Tag ID | X (in) | Y (in) | Wall | Facing |
|--------|--------|--------|------|--------|
| 11 | 0 | 72 | Left | +X (right) |
| 12 | 72 | 144 | Back | -Y (toward audience) |
| 13 | 144 | 72 | Right | -X (left) |
| 14 | 72 | 0 | Audience | +Y (toward back) |

## Common Path Waypoints

### Red Alliance Auto

```kotlin
// Starting position
val startPose = Pose(7.0, 6.75, Math.toRadians(0.0))

// Score preload
val scorePose = Pose(24.0, 48.0, Math.toRadians(90.0))

// Pickup locations
val pickup1Pose = Pose(24.0, 24.0, Math.toRadians(0.0))
val pickup2Pose = Pose(36.0, 130.0, Math.toRadians(0.0))
val pickup3Pose = Pose(36.0, 135.0, Math.toRadians(0.0))
```

### Blue Alliance Auto

```kotlin
// Mirror X coordinates: blueX = 144 - redX
// Mirror heading: blueHeading = π - redHeading

val startPose = Pose(137.0, 6.75, Math.toRadians(180.0))
val scorePose = Pose(120.0, 48.0, Math.toRadians(90.0))
```

## Coordinate Conversion

### From FTC Standard to Pedro

FTC uses origin at field center; Pedro uses corner origin.

```kotlin
fun ftcToPedro(ftcX: Double, ftcY: Double): Pair<Double, Double> {
    val pedroX = ftcX + 72.0  // Shift origin
    val pedroY = ftcY + 72.0
    return Pair(pedroX, pedroY)
}
```

### From Tile Coordinates to Pedro

Field is 6×6 tiles, each tile is 24".

```kotlin
fun tileToPedro(tileX: Double, tileY: Double): Pair<Double, Double> {
    val pedroX = tileX * 24.0
    val pedroY = tileY * 24.0
    return Pair(pedroX, pedroY)
}

// Example: Tile (1.5, 2.5) = Pedro (36", 60")
```

## Important Notes

1. **Verify Positions**: These are estimated positions. Always verify with official field CAD and measurements.

2. **Alliance Mirroring**: For blue alliance, mirror X coordinates around center (72"):
   ```kotlin
   val blueX = 144.0 - redX
   ```

3. **Heading Convention**: Pedro uses radians, CCW positive from +X axis.

4. **Tolerance**: Field measurements have ±1" tolerance per official manual.

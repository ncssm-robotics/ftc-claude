# DECODE Coordinate Systems

## Overview

This document explains how to convert between different coordinate systems used in FTC DECODE:

1. **FTC Standard** - Origin at field center, meters
2. **Pedro Pathing** - Origin at field corner, inches
3. **Tile-Based** - 6×6 grid of 24" tiles
4. **Limelight** - Vision-based degrees

## Pedro Pathing (Primary System)

All autonomous paths should use Pedro coordinates.

```
        ^ +Y (back wall, 144")
        |
        |
        |
Origin  +---> +X (right side, 144")
(0,0)
(audience-left corner)

Heading:
- 0° (0 rad) = facing +X (right)
- 90° (π/2 rad) = facing +Y (back wall)
- 180° (π rad) = facing -X (left)
- -90° (-π/2 rad) = facing audience
```

### Key Properties
- Units: **Inches**
- Heading: **Radians**, CCW positive
- Field size: 144" × 144"

## FTC Standard Coordinates

Used by WPILib-style libraries and Limelight botpose.

```
        ^ +Y (toward back wall)
        |
        |
   -----+-----> +X (toward right)
        |
        | (origin at field center)
        v
```

### Key Properties
- Units: **Meters**
- Heading: **Degrees**, CCW positive
- Origin: Field center (0, 0)

## Tile-Based Coordinates

Field is 6×6 tiles, each 24" × 24".

```
     0    1    2    3    4    5
   ┌────┬────┬────┬────┬────┬────┐
 5 │    │    │    │    │    │    │
   ├────┼────┼────┼────┼────┼────┤
 4 │    │    │    │    │    │    │
   ├────┼────┼────┼────┼────┼────┤
 3 │    │    │    │    │    │    │
   ├────┼────┼────┼────┼────┼────┤
 2 │    │    │    │    │    │    │
   ├────┼────┼────┼────┼────┼────┤
 1 │    │    │    │    │    │    │
   ├────┼────┼────┼────┼────┼────┤
 0 │    │    │    │    │    │    │
   └────┴────┴────┴────┴────┴────┘

Tile (0,0) = Pedro (0-24, 0-24)
Tile center (0.5, 0.5) = Pedro (12, 12)
```

## Conversion Functions

### FTC to Pedro

```kotlin
object CoordinateConversion {
    const val FIELD_SIZE = 144.0  // inches
    const val FIELD_CENTER = 72.0  // inches
    const val INCHES_PER_METER = 39.3701

    fun ftcToPedro(ftcX: Double, ftcY: Double, headingDeg: Double): Pose {
        // Convert meters to inches and shift origin
        val pedroX = (ftcX * INCHES_PER_METER) + FIELD_CENTER
        val pedroY = (ftcY * INCHES_PER_METER) + FIELD_CENTER
        val headingRad = Math.toRadians(headingDeg)

        return Pose(pedroX, pedroY, headingRad)
    }
}
```

### Pedro to FTC

```kotlin
fun pedroToFTC(pose: Pose): Triple<Double, Double, Double> {
    // Convert inches to meters and shift origin
    val ftcX = (pose.x - FIELD_CENTER) / INCHES_PER_METER
    val ftcY = (pose.y - FIELD_CENTER) / INCHES_PER_METER
    val headingDeg = Math.toDegrees(pose.heading)

    return Triple(ftcX, ftcY, headingDeg)
}
```

### Tile to Pedro

```kotlin
fun tileToPedro(tileX: Double, tileY: Double): Pair<Double, Double> {
    // Each tile is 24 inches
    return Pair(tileX * 24.0, tileY * 24.0)
}

fun tileCenter(tileX: Int, tileY: Int): Pair<Double, Double> {
    // Center of tile (add 0.5 tiles = 12 inches)
    return Pair((tileX * 24.0) + 12.0, (tileY * 24.0) + 12.0)
}
```

### Alliance Mirroring

```kotlin
// Mirror red alliance coordinates for blue alliance
fun mirrorForBlue(redPose: Pose): Pose {
    val blueX = FIELD_SIZE - redPose.x
    val blueY = redPose.y  // Y stays same
    val blueHeading = Math.PI - redPose.heading  // Mirror heading

    return Pose(blueX, blueY, normalizeHeading(blueHeading))
}

fun normalizeHeading(heading: Double): Double {
    var h = heading
    while (h > Math.PI) h -= 2 * Math.PI
    while (h < -Math.PI) h += 2 * Math.PI
    return h
}
```

## Common Conversions

| Location | FTC (m) | Pedro (in) | Tile |
|----------|---------|------------|------|
| Field Center | (0, 0) | (72, 72) | (3, 3) |
| Red Start | (-1.65, -1.65) | (7, 7) | (0.3, 0.3) |
| Blue Start | (1.65, -1.65) | (137, 7) | (5.7, 0.3) |

## Limelight Integration

Limelight botpose returns FTC coordinates. Convert to Pedro:

```kotlin
fun limelightToPedro(result: LLResult): Pose? {
    if (!result.isValid) return null

    val botpose = result.botpose
    return CoordinateConversion.ftcToPedro(
        botpose.position.x,
        botpose.position.y,
        botpose.orientation.yaw
    )
}
```

## Heading Quick Reference

| Direction | Degrees | Radians | Description |
|-----------|---------|---------|-------------|
| Right | 0° | 0 | Facing +X |
| Back | 90° | π/2 | Facing +Y (back wall) |
| Left | 180° | π | Facing -X |
| Audience | -90° | -π/2 | Facing -Y |

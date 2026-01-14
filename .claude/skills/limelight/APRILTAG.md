# AprilTag Detection & MegaTag2 Localization

## Overview

Limelight 3A uses AprilTags for:
1. **Target Tracking**: Get tx/ty to specific tags
2. **Field Localization**: MegaTag2 computes robot pose from multiple tags

## Basic AprilTag Detection

```kotlin
limelight.pipelineSwitch(0)  // AprilTag pipeline
limelight.start()

// In loop
val result = limelight.latestResult
if (result.isValid) {
    for (fiducial in result.fiducialResults) {
        telemetry.addData("Tag ${fiducial.fiducialId}",
            "X: %.1f°, Y: %.1f°",
            fiducial.targetXDegrees,
            fiducial.targetYDegrees)
    }
}
telemetry.update()  // REQUIRED after adding telemetry
```

## MegaTag2 Field Localization

MegaTag2 uses multiple visible AprilTags to compute accurate robot position.

### Getting Robot Pose

```kotlin
val result = limelight.latestResult
if (result.isValid) {
    val botpose = result.botpose  // Pose3D

    // Position (meters from field center)
    val x = botpose.position.x
    val y = botpose.position.y
    val z = botpose.position.z

    // Orientation (degrees)
    val yaw = botpose.orientation.yaw
    val pitch = botpose.orientation.pitch
    val roll = botpose.orientation.roll

    // Convert to Pedro Pathing
    val pedroPose = CoordinateConversion.botposeToPedro(botpose)
}
```

### Fusing with Odometry

For best results, fuse Limelight localization with odometry:

```kotlin
fun updatePose() {
    // Get odometry pose (high frequency, drifts over time)
    val odometryPose = follower.pose

    // Get vision pose (low frequency, accurate when visible)
    val result = limelight.latestResult
    if (result.isValid && result.fiducialResults.size >= 2) {
        val visionPose = CoordinateConversion.botposeToPedro(result.botpose)

        // Simple weighted average (tune weights for your robot)
        val VISION_WEIGHT = 0.3
        val fusedX = odometryPose.x * (1 - VISION_WEIGHT) + visionPose.x * VISION_WEIGHT
        val fusedY = odometryPose.y * (1 - VISION_WEIGHT) + visionPose.y * VISION_WEIGHT

        // Update follower with corrected pose
        follower.pose = Pose(fusedX, fusedY, odometryPose.heading)
    }
}
```

### Latency Compensation

Vision data has latency. Compensate by predicting pose:

```kotlin
val result = limelight.latestResult
val totalLatency = result.captureLatency + result.targetingLatency  // ms

// Get robot velocity (from odometry)
val velocity = follower.velocity  // inches/sec

// Predict current position based on velocity and latency
val latencySeconds = totalLatency / 1000.0
val predictedX = visionPose.x + (velocity.x * latencySeconds)
val predictedY = visionPose.y + (velocity.y * latencySeconds)
```

## FTC DECODE AprilTag Layout

*Note: Official DECODE 2025-2026 tag positions TBD. Update with official positions.*

### Expected Tag Positions (Pedro Coordinates)

```
Field Layout (144" x 144"):

        Y = 144" (back wall)
    ┌────────────────────────────────────┐
    │                                    │
    │                [12]                │  Tag 12: Back wall
    │                                    │
[11]│                                    │[13]  Tags 11, 13: Side walls
    │                                    │
    │                                    │
    │                [14]                │  Tag 14: Audience wall
    └────────────────────────────────────┘
        Y = 0" (audience wall)

    X = 0"                          X = 144"
```

### Tag Position Table

| Tag ID | Pedro X (in) | Pedro Y (in) | Wall | Notes |
|--------|-------------|-------------|------|-------|
| 11 | 0 | 72 | Left | Center of left wall |
| 12 | 72 | 144 | Back | Center of back wall |
| 13 | 144 | 72 | Right | Center of right wall |
| 14 | 72 | 0 | Audience | Center of audience wall |

### Check Tag Visibility

```kotlin
// Check if we can see specific tags for localization
fun canLocalize(): Boolean {
    val result = limelight.latestResult
    if (!result.isValid) return false

    // Need at least 2 tags for good localization
    return result.fiducialResults.size >= 2
}

// Get specific scoring target tag
fun getScoreTargetPosition(): Pair<Double, Double>? {
    val SCORE_TAG_ID = 12  // Hypothetical scoring target

    for (fiducial in limelight.latestResult.fiducialResults) {
        if (fiducial.fiducialId == SCORE_TAG_ID) {
            return Pair(fiducial.targetXDegrees, fiducial.targetYDegrees)
        }
    }
    return null
}
```

## Best Practices

1. **Multiple Tags**: MegaTag2 is more accurate with 2+ visible tags
2. **Good Lighting**: AprilTags need adequate, even lighting
3. **Clean Tags**: Ensure field AprilTags are clean and undamaged
4. **Camera Height**: Higher cameras see more tags over obstacles
5. **Update Rate**: Vision runs ~30 FPS; don't poll faster than data arrives

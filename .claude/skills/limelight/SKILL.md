---
name: limelight
description: Helps integrate Limelight 3A vision system for FTC robots. Use when working with AprilTag detection, MegaTag2 localization, color tracking, or shooter auto-aim.
---

# Limelight 3A for FTC

Limelight 3A is a vision processing camera for FTC robotics with on-device processing for AprilTags, color detection, and neural networks.

## Quick Start

### Hardware Configuration

In Robot Configuration, Limelight appears as a USB device:
- Name: `limelight` (default)
- Shows IP address as "serial number"

### Basic Usage

```kotlin
import com.qualcomm.hardware.limelightvision.Limelight3A
import com.qualcomm.hardware.limelightvision.LLResult

val limelight = hardwareMap.get(Limelight3A::class.java, "limelight")

// MUST call start() before getting results
limelight.pipelineSwitch(0)
limelight.start()

// In loop
val result = limelight.latestResult
if (result.isValid) {
    val tx = result.tx  // Horizontal offset in degrees
    val ty = result.ty  // Vertical offset in degrees
}

// When done
limelight.stop()
```

## Key Concepts

| Term | Description |
|------|-------------|
| **tx** | Horizontal offset to target (-27° to +27°) |
| **ty** | Vertical offset to target (-20.5° to +20.5°) |
| **ta** | Target area (0-100% of image) |
| **Pipeline** | Vision processing mode (0-9) |
| **MegaTag2** | Robot localization using AprilTags |
| **Botpose** | Robot's position on field from vision |

## Pipelines

Configure pipelines in Limelight web interface (`http://limelight.local:5801`):

| Pipeline | Typical Use |
|----------|-------------|
| 0 | AprilTag detection (default) |
| 1 | Color tracking |
| 2-9 | Custom (neural network, etc.) |

Switch pipelines: `limelight.pipelineSwitch(1)`

## Coordinate Systems

### Limelight Coordinates
- **tx**: Positive = target right of crosshair
- **ty**: Positive = target above crosshair
- Origin at camera optical center

### Converting to Pedro Pathing

See [COORDINATES.md](COORDINATES.md) for details.

```kotlin
// Limelight botpose to Pedro Pose
val botpose = result.botpose  // Pose3D in FTC coordinates
val pedroPose = Pose(
    botpose.position.x * INCHES_PER_METER,
    botpose.position.y * INCHES_PER_METER,
    Math.toRadians(botpose.orientation.yaw)
)
```

## Conversion Scripts

Use `uv run` to execute conversion scripts:

```bash
# Convert Limelight botpose to Pedro coordinates
uv run .claude/skills/limelight/scripts/convert.py botpose-to-pedro 0.5 1.2 45

# Calculate turret ticks from tx
uv run .claude/skills/limelight/scripts/convert.py tx-to-turret -5.5
uv run .claude/skills/limelight/scripts/convert.py tx-to-turret -5.5 12.0  # custom ticks/degree

# Calculate distance from ty (ty, cam_height, cam_angle, target_height)
uv run .claude/skills/limelight/scripts/convert.py distance 15 12 20 36
```

## Reference Documentation

- [API_REFERENCE.md](API_REFERENCE.md) - Full class/method reference
- [COORDINATES.md](COORDINATES.md) - Coordinate system details
- [MOUNTING.md](MOUNTING.md) - Camera mounting and calibration
- [APRILTAG.md](APRILTAG.md) - AprilTag detection and localization

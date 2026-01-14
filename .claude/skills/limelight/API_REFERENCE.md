# Limelight 3A API Reference

## Classes

### Limelight3A

Main camera interface from `com.qualcomm.hardware.limelightvision`.

```kotlin
val limelight = hardwareMap.get(Limelight3A::class.java, "limelight")
```

#### Methods

| Method | Description |
|--------|-------------|
| `start()` | Start polling for data (required before getLatestResult) |
| `stop()` | Stop polling |
| `pipelineSwitch(index: Int)` | Switch to pipeline 0-9 |
| `getLatestResult(): LLResult` | Get most recent vision result |
| `getStatus(): LLStatus` | Get camera status (temp, FPS, etc.) |

---

### LLResult

Vision processing result.

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `isValid` | Boolean | Whether result contains valid data |
| `tx` | Double | Horizontal offset to target (degrees) |
| `ty` | Double | Vertical offset to target (degrees) |
| `ta` | Double | Target area (0-100%) |
| `txNC` | Double | tx without crosshair offset |
| `tyNC` | Double | ty without crosshair offset |
| `botpose` | Pose3D | Robot pose from MegaTag2 |
| `captureLatency` | Double | Image capture latency (ms) |
| `targetingLatency` | Double | Processing latency (ms) |
| `parseLatency` | Double | Data parsing latency (ms) |

#### Result Lists

| Property | Type | Description |
|----------|------|-------------|
| `fiducialResults` | List<FiducialResult> | AprilTag detections |
| `colorResults` | List<ColorResult> | Color target detections |
| `detectorResults` | List<DetectorResult> | Neural network detections |
| `classifierResults` | List<ClassifierResult> | Classification results |
| `barcodeResults` | List<BarcodeResult> | Barcode detections |
| `pythonOutput` | DoubleArray | Custom pipeline output |

---

### LLResultTypes.FiducialResult

AprilTag detection.

| Property | Type | Description |
|----------|------|-------------|
| `fiducialId` | Int | AprilTag ID number |
| `family` | String | Tag family (e.g., "36h11") |
| `targetXDegrees` | Double | Horizontal offset (degrees) |
| `targetYDegrees` | Double | Vertical offset (degrees) |

---

### LLResultTypes.ColorResult

Color target detection.

| Property | Type | Description |
|----------|------|-------------|
| `targetXDegrees` | Double | Horizontal offset (degrees) |
| `targetYDegrees` | Double | Vertical offset (degrees) |

---

### LLResultTypes.DetectorResult

Neural network detection.

| Property | Type | Description |
|----------|------|-------------|
| `className` | String | Detected object class |
| `targetArea` | Double | Target area percentage |

---

### LLStatus

Camera status information.

| Property | Type | Description |
|----------|------|-------------|
| `name` | String | Camera name |
| `temp` | Double | Temperature (°C) |
| `cpu` | Double | CPU usage (%) |
| `fps` | Double | Frames per second |
| `pipelineIndex` | Int | Current pipeline |
| `pipelineType` | String | Pipeline type |

---

## Common Patterns

### Shooter Auto-Aim

```kotlin
fun updateTurretAim() {
    val result = limelight.latestResult
    if (result.isValid) {
        val tx = result.tx  // Degrees off-center
        // Convert to turret motor command
        val turretPower = tx * TURRET_KP
        turretMotor.power = turretPower.coerceIn(-0.5, 0.5)
    }
}
```

### Check for Specific AprilTag

```kotlin
fun isTargetTagVisible(tagId: Int): Boolean {
    val result = limelight.latestResult
    if (!result.isValid) return false

    return result.fiducialResults.any { it.fiducialId == tagId }
}
```

### Field Localization

```kotlin
fun getRobotPose(): Pose3D? {
    val result = limelight.latestResult
    return if (result.isValid) result.botpose else null
}
```

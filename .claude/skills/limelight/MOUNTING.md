# Limelight 3A Mounting & Calibration

## Physical Mounting

### Turret-Mounted (Shooter Auto-Aim)

For shooter auto-aim, mount the Limelight on the turret so it rotates with the shooter:

```
Side View:
                   ┌───────┐
                   │ LIMELIGHT
    ┌──────────────┴───────┴──────────────┐
    │           TURRET / SHOOTER           │
    └──────────────────────────────────────┘
                      │
                   ROTATION
                    AXIS
```

- Mount rigidly to turret assembly
- Camera should face same direction as shooter
- Tilt up slightly to see distant targets

### Fixed Mount (Field Localization)

For MegaTag2 localization, mount Limelight fixed to robot frame:

- Best: Elevated position with clear view of field walls
- Avoid: Low positions blocked by game elements
- Consider: Multiple Limelights for 360° coverage

## Camera Offset Configuration

Configure camera position relative to robot center in Limelight web UI for accurate botpose.

### Access Web Interface

1. Connect to robot WiFi
2. Navigate to `http://limelight.local:5801`
3. Go to "Settings" → "3D"

### Offset Measurements

Measure from robot center to camera lens:

| Parameter | Description | Sign Convention |
|-----------|-------------|-----------------|
| Forward | Distance toward front of robot | + forward |
| Right | Distance toward right side | + right |
| Up | Height from ground to lens | + up |

### Example Configuration

For turret-mounted Limelight:
```
Forward: 8.5 inches (camera ahead of robot center)
Right: 0 inches (camera centered)
Up: 12 inches (camera height from ground)
Pitch: 15 degrees (tilted up to see targets)
Yaw: 0 degrees (aligned with turret)
Roll: 0 degrees
```

## Pipeline Configuration

### AprilTag Pipeline (Pipeline 0)

1. Pipeline Type: "AprilTag"
2. Tag Family: "36h11" (FTC standard)
3. Tag Size: Configure based on actual tag dimensions
4. Enable MegaTag2 for field localization

### Color Pipeline (Pipeline 1)

1. Pipeline Type: "Color"
2. HSV Thresholds: Tune for artifact colors
   - DECODE Purple: H 260-290, S 50-100, V 30-100
   - DECODE Green: H 80-140, S 50-100, V 30-100
3. Contour filtering for size/shape

## Calibration Checklist

- [ ] Camera physically secured (no vibration)
- [ ] USB cable routed away from motors
- [ ] Camera offset measured and configured
- [ ] Pipeline 0 configured for AprilTags
- [ ] Pipeline 1 configured for color tracking
- [ ] Field AprilTag positions entered
- [ ] Test botpose accuracy with known positions
- [ ] Test tx/ty accuracy for auto-aim

## Troubleshooting

### No Data from Limelight

1. Check USB connection
2. Verify `limelight.start()` was called
3. Check pipeline is appropriate for current target

### Inaccurate Botpose

1. Verify camera offset configuration
2. Check AprilTag dimensions in settings
3. Ensure sufficient lighting
4. Verify field AprilTag positions

### tx/ty Jitter

1. Enable crosshair offset calibration
2. Apply software filtering
3. Check camera mount rigidity

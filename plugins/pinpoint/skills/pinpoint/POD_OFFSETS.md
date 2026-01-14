# Pod Offset Configuration

Pod offsets tell the Pinpoint where your odometry pods are located relative to the robot's center of rotation.

## Understanding Offsets

The Pinpoint tracks position relative to a reference point (typically robot center). Since the pods aren't at the center, you must specify their positions.

```
                    Forward (+Y)
                        ▲
                        │
          ┌─────────────┼─────────────┐
          │             │             │
          │      ┌──────┴──────┐      │
          │      │   CENTER    │      │
  Left ◄──┼──────│             │──────┼──► Right
  (+X)    │      │             │      │    (-X)
          │      └─────────────┘      │
          │                           │
          │    ◯ Forward Pod          │
          │    (measures Y travel)    │
          │                           │
          │         ═══════           │
          │        Strafe Pod         │
          │    (measures X travel)    │
          └───────────────────────────┘
                        │
                        ▼
                    Backward (-Y)
```

## Measuring Offsets

### Forward Pod Offset (forwardPodY / Y_POD_OFFSET)

Measures how far **forward or backward** from center the forward pod is:
- **Positive**: Pod is in front of center
- **Negative**: Pod is behind center

### Strafe Pod Offset (strafePodX / X_POD_OFFSET)

Measures how far **left or right** from center the strafe pod is:
- **Positive**: Pod is left of center
- **Negative**: Pod is right of center

## Pedro Pathing Configuration

```java
public static PinpointConstants localizerConstants = new PinpointConstants()
    .forwardPodY(-2.25)    // Forward pod is 2.25 inches behind center
    .strafePodX(3.5)       // Strafe pod is 3.5 inches left of center
    // ... other settings
```

## Standalone Driver Configuration

```java
// Offsets in millimeters for direct driver use
pinpoint.setOffsets(xOffset_mm, yOffset_mm);

// Example: strafe pod 90mm left, forward pod 60mm behind center
pinpoint.setOffsets(90.0, -60.0);
```

**Note**: The driver's `setOffsets(x, y)` uses:
- `x` = how far **left** (sideways) the forward pod is
- `y` = how far **forward** the strafe pod is

This is different from Pedro's PinpointConstants naming!

## Tips for Accurate Measurement

1. Measure from the **center of rotation** (usually geometric center for mecanum)
2. Measure to the **center of the odometry wheel**
3. Use consistent units (Pedro uses inches, driver uses mm)
4. Double-check positive/negative directions

## Verifying Offsets

After configuration, test by:
1. Rotating the robot in place
2. The reported position should remain stable (not drift in X or Y)
3. If position drifts during pure rotation, offsets are incorrect

## Current Team Configuration

From `Constants.java`:
```java
.forwardPodY(0)     // Forward pod at center Y
.strafePodX(-4)     // Strafe pod 4 inches right of center
```

# Path Constraints

All five constraints must be satisfied for `follower.isBusy()` to return false.

## Available Constraints

### Timeout
Duration in milliseconds for position correction after stopping.
```java
path.setTimeoutConstraint(500);  // 500ms correction time
```
Longer = more accurate endpoint, Shorter = faster transitions

### TValue
Parametric completion threshold (0.0 to 1.0).
```java
path.setTValueConstraint(0.95);  // 95% of path must complete
```

### Velocity
Speed threshold in inches/second.
```java
path.setVelocityConstraint(2.0);  // Must be below 2 in/s
```

### Translational
Maximum allowable position error in inches.
```java
path.setTranslationalConstraint(1.0);  // Within 1 inch of target
```

### Heading
Maximum allowable rotation error in radians.
```java
path.setHeadingConstraint(Math.toRadians(5));  // Within 5 degrees
```

## PathConstraints Object

Set default constraints in Constants.java:
```java
public static PathConstraints pathConstraints = new PathConstraints(
    0.99,   // tvalue
    100,    // timeout (ms)
    1,      // translational (inches)
    1       // heading (radians - check units)
);
```

## Troubleshooting

**Robot stuck at path end?**
- Decrease TValue constraint
- Decrease Timeout constraint
- Check if robot can physically reach target position

# Heading Interpolation Options

All heading values must be in radians. Use `Math.toRadians(degrees)` for conversion.

## Single Path Methods

### Linear Heading Interpolation
Robot turns from start to end heading during path execution.
```java
path.setLinearHeadingInterpolation(startHeading, endHeading);
// With end time (0.0-1.0, when rotation completes, ~0.8 recommended)
path.setLinearHeadingInterpolation(startHeading, endHeading, 0.8);
```

### Constant Heading Interpolation
Robot maintains fixed heading throughout path.
```java
path.setConstantHeadingInterpolation(Math.toRadians(90));
```

### Tangent Heading Interpolation
Robot faces direction of travel (along path slope).
```java
path.setTangentHeadingInterpolation();
```

### Facing Point Interpolation
Robot faces a specific point while following path.
```java
path.setHeadingInterpolation(HeadingInterpolator.facingPoint(targetPoint));
```

### Piecewise Interpolation
Different interpolation for different path segments.
```java
// tvalue: 0 = start, 1 = end of path
HeadingInterpolator piecewise = HeadingInterpolator.piecewise(
    new HeadingInterpolator.PiecewiseNode(0.0, constantInterpolator),
    new HeadingInterpolator.PiecewiseNode(0.5, linearInterpolator)
);
```

## Reversing Interpolation
Call `.reversed()` on any interpolator:
- Linear: takes longer rotation route
- Tangent: robot drives backward
- Constant: no effect

```java
path.setTangentHeadingInterpolation().reversed();
```

## PathChain Global Interpolation
Apply interpolation across entire chain as one continuous path.
```java
pathChain.setGlobalHeadingInterpolation(myInterpolator);
```

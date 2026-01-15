# Control Method Decision Trees

Visual flowcharts and detailed decision logic for selecting the right control approach.

## Master Decision Tree

```
                    START: What mechanism?
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   Drivetrain          Mechanism           Intake/Simple
        │                   │                   │
        v                   v                   v
   Use RoadRunner      Does it fight       Bang-bang or
   or Pedro Pathing    gravity?            simple PID
   (STOP)                   │
                    ┌───────┴───────┐
                    │               │
                   YES              NO
                    │               │
            ┌───────┴───────┐       │
            │               │       │
        Linear          Rotational  │
        (Elevator)      (Arm)       │
            │               │       │
            v               v       v
        Pos PID +       Pos PID +   Is it velocity
        kG constant     kG*cos(θ)   control?
                                        │
                                ┌───────┴───────┐
                                │               │
                               YES              NO
                                │               │
                                v               v
                            Vel PID +       Pos PID
                            kV*velocity     only
```

## Mechanism Classification

### How to Identify Your Mechanism Type

| Question | Elevator | Arm | Flywheel | Turret | Intake |
|----------|----------|-----|----------|--------|--------|
| Motion type? | Linear | Rotational | Rotational | Rotational | Rotational |
| Fights gravity? | Yes (constant) | Yes (varies) | No | No | No |
| Control goal? | Position | Position | Velocity | Position | Binary |
| Encoder type? | String pot / linear | Through-bore | Motor encoder | Through-bore | None/limit |

### Physical Characteristics by Mechanism

**Elevator/Lift**
- Moves vertically against gravity
- Gravity force is constant at all positions
- Uses pulleys, lead screws, or linear slides
- Feedforward: constant `kG`

**Arm/Pivot**
- Rotates around a pivot point
- Gravity torque = weight × arm_length × cos(angle)
- Maximum torque when horizontal, zero when vertical
- Feedforward: `kG * cos(angle)`

**Flywheel/Shooter**
- Spins continuously at target velocity
- No position control needed
- High inertia means slow response
- Feedforward: `kV * target_velocity`

**Turret/Rotating Platform**
- Rotates to specific positions
- Usually horizontal (no gravity effect)
- May have cable management constraints
- Feedforward: usually none needed

## When to Add Complexity

### Decision: Do I Need Motion Profiling?

```
Does the mechanism need smooth acceleration?
        │
    ┌───┴───┐
   YES      NO
    │        │
    v        └──> Skip motion profiling
Are there power/current limits?
        │
    ┌───┴─────────────────────┐
   YES                        NO
    │                         │
    v                         v
Use trapezoidal    Is overshoot dangerous?
or S-curve profile            │
                        ┌─────┴─────┐
                       YES          NO
                        │            │
                        v            v
                Use profiling    Skip motion profiling
```

**Use motion profiling when:**
- Mechanism could hit hard stops
- Motor current limits are a concern
- You need predictable, smooth motion
- Coordinating multiple mechanisms

### Decision: Do I Need Cascaded Control?

```
Is single-loop PID too slow or oscillatory?
        │
    ┌───┴───┐
   YES      NO
    │        │
    v        └──> Stick with single loop
Do you have both position AND velocity feedback?
        │
    ┌───┴───┐
   YES      NO
    │        │
    v        └──> Can't cascade without both
Consider cascaded control:
- Outer loop: Position → velocity setpoint
- Inner loop: Velocity → motor power
```

**Cascaded control helps when:**
- Single loop is sluggish
- You have encoder velocity feedback
- Mechanism has high inertia

### Decision: Do I Need Sensor Filtering?

```
Is your sensor data noisy (jumpy readings)?
        │
    ┌───┴───┐
   YES      NO
    │        │
    v        └──> No filter needed
Is noise causing oscillation or jitter?
        │
    ┌───┴───┐
   YES      NO
    │        │
    v        └──> Might be okay without
Add low-pass filter:
- Simple: Exponential moving average
- Better: Butterworth or Kalman
```

**Filter types:**
| Filter | Complexity | Lag | Use When |
|--------|------------|-----|----------|
| Moving average | Low | High | Very noisy, slow system |
| Exponential (EMA) | Low | Medium | General purpose |
| Low-pass (IIR) | Medium | Tunable | Need specific cutoff |
| Kalman | High | Low | Multiple sensors, need velocity |

## Library Selection Decision Tree

```
Check build.gradle for existing libraries
        │
        v
Found "dev.nextftc:control"?
        │
    ┌───┴───────────────────────────────┐
   YES                                  NO
    │                                   │
    v                                   v
Use ControlSystem.builder()    Found "com.arcrobotics.ftclib"?
(see NextFTC docs)                      │
                                ┌───────┴───────┐
                               YES              NO
                                │               │
                                v               v
                        Use PIDController    Implement manually
                        (see FTCLib docs)    (this skill guides you)
```

### Library Comparison

| Feature | NextFTC | FTCLib | Plain SDK |
|---------|---------|--------|-----------|
| PID Controller | `posPid()`, `velPid()` | `PIDController` | Manual |
| Feedforward | `elevatorFF()`, `armFF()`, `basicFF()` | Manual | Manual |
| Tolerance check | `isWithinTolerance()` | `atSetPoint()` | Manual |
| Filter support | Built-in | Separate | Manual |
| Motion profile | Separate | `MotionProfile` | Manual |
| Learning curve | Low | Low | Medium |

## Advanced Control Decision Tree

```
Is simple PID+FF working acceptably?
        │
    ┌───┴───────────────┐
   YES                  NO
    │                   │
    └──> STOP    Have you tuned FF properly first?
                        │
                ┌───────┴───────┐
               YES              NO
                │               │
                v               └──> Go tune FF first!
        Do you have a controls mentor, previous experience with control methods other than PID, or are willing to spend time learning more advanced control methods?
                │
        ┌───────┴───────┐
       YES              NO
        │               │
        v               v
Consider advanced:   Stick with PID+FF
- State-space        (get mentor before
- LQR                 going advanced)
- Kalman filter

See ADVANCED_CONTROL.md
```

## Quick Reference: Mechanism → Controller

| If you're building... | Use this controller | With this feedforward |
|----------------------|--------------------|-----------------------|
| Elevator | Position PID | `kG` (constant) |
| Single-jointed arm | Position PID | `kG * cos(angle)` |
| Double-jointed arm | Position PID per joint | `kG * cos(angle)` each |
| Flywheel shooter | Velocity PID | `kV * velocity` |
| Turret | Position PID | None |
| Horizontal slide | Position PID | `kS * sign(velocity)` |
| Intake | Bang-bang or none | None |
| Drivetrain | **Use RoadRunner/Pedro** | (handled internally) |

## Troubleshooting Decision Trees

### Oscillation

```
System is oscillating
        │
        v
Is it fast oscillation (high frequency)?
        │
    ┌───┴───┐
   YES      NO
    │        │
    v        v
Reduce kD    Is it slow oscillation?
(D fighting        │
noise)         ┌───┴───┐
              YES      NO
               │        │
               v        v
          Reduce kP   Check mechanical
          Add kD      (loose belts, backlash)
```

### Won't Hold Position

```
Mechanism drifts or falls
        │
        v
Does it fight gravity?
        │
    ┌───┴───┐
   YES      NO
    │        │
    v        v
Add/increase    Check brake mode
kG feedforward  on motor
        │
        v
Still drifting?
        │
    ┌───┴───┐
   YES      NO
    │        │
    v        └──> Fixed!
Add small kI
or check for
mechanical slip
```

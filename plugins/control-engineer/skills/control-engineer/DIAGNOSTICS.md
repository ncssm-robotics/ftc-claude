# Control System Diagnostics & Code Review

Troubleshooting guide for diagnosing control system problems and reviewing existing code for improvements.

## Quick Diagnosis

### What's Your Symptom?

| Symptom | Jump To |
|---------|---------|
| Motor doesn't move at all | [Not Moving](#not-moving) |
| Moves but doesn't reach target | [Not Reaching Target](#not-reaching-target) |
| Oscillates / vibrates around target | [Oscillation](#oscillation) |
| Overshoots then corrects | [Overshoot](#overshoot) |
| Drifts slowly over time | [Drift](#drift) |
| Works sometimes, fails randomly | [Intermittent Failures](#intermittent-failures) |
| Jerky / stuttering motion | [Jitter](#jitter) |
| Very slow response | [Slow Response](#slow-response) |
| Works in one direction only | [Asymmetric Behavior](#asymmetric-behavior) |

---

## Not Moving

### Symptom
Motor doesn't move at all, or barely moves.

### Diagnostic Checklist

```
□ Is motor power being set? (Add telemetry to verify)
□ Is output clamped to valid range (-1 to 1)?
□ Is error being calculated correctly? (target - current, not current - target)
□ Is the motor configured correctly? (direction, mode)
□ Is the motor physically connected and working?
□ Is there a safety condition preventing movement?
```

### Common Causes & Fixes

**1. Output not reaching motor**
```java
// BAD: Calculating but not applying
double output = controller.calculate(current, target);
// Missing: motor.setPower(output);

// GOOD: Apply the output
double output = controller.calculate(current, target);
motor.setPower(output);
```

**2. Gains too low**
```java
// BAD: Gains so low output is negligible
double kP = 0.000001;  // Way too small
double output = kP * error;  // Output ≈ 0

// GOOD: Start with reasonable gains
double kP = 0.001;  // Start here, tune up
```

**3. Wrong error sign**
```java
// BAD: Inverted error drives away from target
double error = current - target;  // Wrong!

// GOOD: Error should be target - current
double error = target - current;
```

**4. Output clamped incorrectly**
```java
// BAD: Always clamping to 0
output = Math.max(0, Math.min(0, output));

// GOOD: Clamp to motor range
output = Math.max(-1.0, Math.min(1.0, output));
```

**5. Motor direction inverted**
```java
// Check if motor spins the right way
motor.setDirection(DcMotorSimple.Direction.REVERSE);  // Try toggling
```

### Debugging Steps

1. Add telemetry to see what's happening:
```java
telemetry.addData("Target", target);
telemetry.addData("Current", current);
telemetry.addData("Error", error);
telemetry.addData("Output", output);
telemetry.addData("Motor Power", motor.getPower());
telemetry.update();
```

2. Test motor directly:
```java
// Bypass controller, test motor works
motor.setPower(0.3);  // Should move
```

3. Test encoder:
```java
// Verify encoder counts change
telemetry.addData("Encoder", motor.getCurrentPosition());
```

---

## Not Reaching Target

### Symptom
Motor moves toward target but stops short (steady-state error).

### Diagnostic Checklist

```
□ Is feedforward being used? (Required for gravity systems)
□ Is feedforward value correct? (Tune kG/kV)
□ Is integral gain being used? (May be needed)
□ Is there mechanical resistance? (Friction, binding)
□ Is target within achievable range?
```

### Common Causes & Fixes

**1. Missing feedforward (most common)**
```java
// BAD: PID only - will always have error on gravity systems
double output = kP * error;

// GOOD: Add gravity compensation
double output = kP * error + kG;  // For elevator
double output = kP * error + kG * Math.cos(angle);  // For arm
```

**2. Feedforward too low**
```java
// BAD: kG doesn't fully counteract gravity
double kG = 0.05;  // Too weak

// GOOD: Tune kG until mechanism holds position
double kG = 0.15;  // Find this experimentally
```

**3. Integral not accumulating**
```java
// BAD: Integral reset every loop
public void update() {
    double integral = 0;  // Reset each call!
    integral += error;
}

// GOOD: Integral persists across loops
private double integral = 0;  // Class field
public void update() {
    integral += error;
}
```

**4. Friction not compensated**
```java
// BAD: Motor can't overcome static friction
double output = kP * error;  // Small near target

// GOOD: Add static friction compensation
double output = kP * error;
if (Math.abs(error) > deadband) {
    output += kS * Math.signum(error);  // Kick to overcome friction
}
```

**5. Target unreachable**
```java
// Check if target is within physical limits
if (target > MAX_POSITION || target < MIN_POSITION) {
    // Target is impossible
}
```

### Measuring Steady-State Error

```java
// Log error over time after reaching approximate position
if (timer.seconds() > 2.0) {  // Wait for settling
    telemetry.addData("Steady-State Error", error);
    // If consistently > 0, need more FF or integral
}
```

---

## Oscillation

### Symptom
Mechanism vibrates or swings back and forth around target.

### Diagnostic Checklist

```
□ Is kP too high?
□ Is kD being used?
□ Is kI too high?
□ Is there mechanical backlash?
□ Is the control loop running too slowly?
□ Is sensor data noisy?
```

### Types of Oscillation

**Fast oscillation (high frequency)**
- Cause: Usually kD too high, amplifying noise
- Fix: Reduce kD, add sensor filter

**Medium oscillation (around target)**
- Cause: Usually kP too high
- Fix: Reduce kP, add kD

**Slow oscillation (overshoots repeatedly)**
- Cause: Usually kI too high, or kP too high with no kD
- Fix: Reduce kI, add kD

### Common Causes & Fixes

**1. P gain too high**
```java
// BAD: Aggressive P causes overshoot and oscillation
double kP = 0.1;  // Too high

// GOOD: Reduce until oscillation stops
double kP = 0.03;  // Back off 50-70%
```

**2. Missing D gain**
```java
// BAD: P-only control oscillates
double output = kP * error;

// GOOD: Add derivative to dampen
double derivative = error - lastError;
double output = kP * error + kD * derivative;
```

**3. I gain too high**
```java
// BAD: Integral winds up and causes overshoot
double kI = 0.01;  // Too aggressive

// GOOD: Use very small integral, or none
double kI = 0.0001;  // Much smaller
```

**4. Integral windup**
```java
// BAD: Integral grows unbounded
integral += error;

// GOOD: Limit integral
integral += error;
integral = Math.max(-maxIntegral, Math.min(maxIntegral, integral));
```

**5. Noisy sensor + high D**
```java
// BAD: D amplifies sensor noise
double derivative = (position - lastPosition) / dt;  // Noisy!

// GOOD: Filter the derivative or position
double filteredPosition = alpha * position + (1 - alpha) * lastFilteredPosition;
double derivative = (filteredPosition - lastFilteredPosition) / dt;
```

### Tuning Out Oscillation

1. Set kI = 0, kD = 0
2. Reduce kP until oscillation stops
3. If still oscillating, add small kD
4. Only add kI if there's steady-state error

---

## Overshoot

### Symptom
Mechanism goes past target, then comes back.

### Diagnostic Checklist

```
□ Is kP too high?
□ Is feedforward too high?
□ Is kD being used?
□ Is mechanism moving too fast? (Need motion profile?)
□ Is there momentum that's not accounted for?
```

### Common Causes & Fixes

**1. P gain too high**
```java
// BAD: High P creates too much power near target
double kP = 0.05;

// GOOD: Reduce P, rely more on feedforward
double kP = 0.02;
```

**2. Missing derivative**
```java
// BAD: No damping
double output = kP * error + feedforward;

// GOOD: D slows approach to target
double output = kP * error + kD * derivative + feedforward;
```

**3. Feedforward oversized**
```java
// BAD: FF alone overshoots
double kV = 0.002;  // Too high

// GOOD: Tune FF to barely reach target, let PID fine-tune
double kV = 0.0015;
```

**4. No velocity limiting**
```java
// BAD: Full power at any distance
double output = kP * error;

// GOOD: Limit output or use motion profile
double output = kP * error;
output = Math.max(-0.5, Math.min(0.5, output));  // Limit max speed
```

### Measuring Overshoot

```java
private double maxOvershoot = 0;
private boolean passedTarget = false;

public void update() {
    double error = target - current;

    // Detect if we've passed target
    if (Math.signum(error) != Math.signum(lastError) && lastError != 0) {
        passedTarget = true;
    }

    if (passedTarget) {
        maxOvershoot = Math.max(maxOvershoot, Math.abs(error));
    }

    telemetry.addData("Max Overshoot", maxOvershoot);
}
```

---

## Drift

### Symptom
Mechanism slowly moves away from target over time.

### Diagnostic Checklist

```
□ Is encoder resetting unexpectedly?
□ Is there mechanical slip? (Belt, gear, shaft)
□ Is integral being used incorrectly?
□ Is feedforward fighting the wrong direction?
□ Is there an external force not accounted for?
```

### Common Causes & Fixes

**1. Encoder overflow/reset**
```java
// BAD: Using raw encoder that might reset
int position = motor.getCurrentPosition();

// GOOD: Track total position
private long totalPosition = 0;
private int lastRaw = 0;
public void update() {
    int raw = motor.getCurrentPosition();
    int delta = raw - lastRaw;
    // Handle overflow
    if (Math.abs(delta) > 30000) {
        delta = 0;  // Ignore overflow
    }
    totalPosition += delta;
    lastRaw = raw;
}
```

**2. Mechanical slip**
```java
// If encoder shows stable but mechanism drifts:
// - Check belt tension
// - Check setscrew on gear/pulley
// - Check shaft coupler
// No code fix - mechanical problem
```

**3. Wrong feedforward direction**
```java
// BAD: Fighting gravity wrong way
double gravityFF = -kG;  // Pulling down instead of up!

// GOOD: Verify direction
double gravityFF = kG;  // Positive = up for elevator
```

**4. Integral drift**
```java
// BAD: Integral accumulates indefinitely
integral += error * dt;

// GOOD: Reset integral when at target, or use decay
if (Math.abs(error) < tolerance) {
    integral = 0;
}
// Or use integral decay
integral = integral * 0.99 + error;
```

---

## Intermittent Failures

### Symptom
Works sometimes, fails randomly.

### Diagnostic Checklist

```
□ Is loop timing consistent?
□ Are there race conditions?
□ Is hardware connection loose?
□ Does it fail after motors heat up?
□ Is there a timing-dependent bug?
```

### Common Causes & Fixes

**1. Inconsistent loop timing**
```java
// BAD: Assumes consistent dt
double derivative = error - lastError;  // Wrong if dt varies!

// GOOD: Account for actual dt
double dt = timer.seconds();
timer.reset();
double derivative = (error - lastError) / dt;
```

**2. Initialization order issues**
```java
// BAD: Using motor before initialization
public void setTarget(int pos) {
    motor.setTargetPosition(pos);  // motor might be null!
}

// GOOD: Check initialization
public void setTarget(int pos) {
    if (motor != null) {
        motor.setTargetPosition(pos);
    }
}
```

**3. Motor heating**
```java
// Motors lose power when hot
// If control works when cold but fails when hot:
// - Reduce max power
// - Add cooling time between runs
// - Re-tune with warm motors
```

**4. Electrical brownout**
```java
// Monitor voltage
double voltage = hardwareMap.voltageSensor.iterator().next().getVoltage();
telemetry.addData("Voltage", voltage);
// If voltage drops below 11V, control may be unreliable
```

---

## Jitter

### Symptom
Motor output is noisy, causing vibration or stuttering.

### Diagnostic Checklist

```
□ Is kD too high?
□ Is sensor data noisy?
□ Is loop running very fast?
□ Are calculations causing numerical issues?
```

### Common Causes & Fixes

**1. D gain amplifying noise**
```java
// BAD: High D on noisy signal
double kD = 0.1;
double derivative = position - lastPosition;
double output = kD * derivative;  // Noisy!

// GOOD: Reduce D or filter
double kD = 0.01;  // Much lower
// Or filter the derivative
double filteredDerivative = 0.8 * lastDerivative + 0.2 * derivative;
```

**2. Encoder noise**
```java
// BAD: Raw encoder jumps around
int position = motor.getCurrentPosition();

// GOOD: Apply low-pass filter
double alpha = 0.1;  // Lower = more smoothing
filteredPosition = alpha * position + (1 - alpha) * filteredPosition;
```

**3. Floating point issues near zero**
```java
// BAD: Divide by very small number
double output = error / verySmallNumber;

// GOOD: Add deadband
if (Math.abs(error) < deadband) {
    output = 0;
} else {
    output = kP * error;
}
```

---

## Slow Response

### Symptom
Motor moves toward target but takes too long.

### Diagnostic Checklist

```
□ Is kP too low?
□ Is feedforward too low?
□ Is output being over-limited?
□ Is motor powerful enough?
□ Is there excessive friction?
```

### Common Causes & Fixes

**1. P gain too low**
```java
// BAD: Very conservative gains
double kP = 0.0001;

// GOOD: Increase until you see some overshoot, then back off
double kP = 0.005;
```

**2. Output over-limited**
```java
// BAD: Limiting output too much
output = Math.max(-0.2, Math.min(0.2, output));

// GOOD: Allow more power
output = Math.max(-0.8, Math.min(0.8, output));
```

**3. Feedforward undertuned**
```java
// BAD: Relying on PID alone
double output = kP * error;

// GOOD: Feedforward does heavy lifting
double output = kP * error + kV * targetVelocity + kG;
```

---

## Asymmetric Behavior

### Symptom
Works in one direction but not the other.

### Diagnostic Checklist

```
□ Is motor direction correct?
□ Is feedforward direction-aware?
□ Is there asymmetric friction?
□ Is gravity only in one direction?
□ Are limit switches blocking one direction?
```

### Common Causes & Fixes

**1. Gravity not compensated in both directions**
```java
// BAD: Only compensates when going up
if (error > 0) {
    output += kG;
}

// GOOD: Always compensate gravity
output += kG;  // Constant compensation regardless of direction
```

**2. Asymmetric friction**
```java
// BAD: Same kS both directions
double staticFF = kS * Math.signum(targetVelocity);

// GOOD: Different compensation per direction
double staticFF;
if (targetVelocity > 0) {
    staticFF = kS_up;
} else {
    staticFF = kS_down;
}
```

**3. Software limits blocking**
```java
// BAD: Asymmetric limits
if (position > MAX) {
    output = 0;  // Can't go up
}
// But no lower limit!

// GOOD: Symmetric limits
if (position > MAX && output > 0) output = 0;
if (position < MIN && output < 0) output = 0;
```

---

## Code Review Checklist

When reviewing existing control code, check for these issues:

### Structure & Safety

```
□ Motor is set to BRAKE mode (for position control)
□ Position limits are defined and enforced
□ Output is clamped to [-1, 1]
□ Integral has anti-windup limits
□ Encoder zero position is handled
```

### Control Design

```
□ Feedforward is used for gravity/velocity systems
□ Feedforward is tuned before PID
□ kI is only used if steady-state error exists
□ kD is not too high (noise sensitivity)
□ Loop timing is accounted for
```

### Code Quality

```
□ Error calculation is correct (target - current)
□ State variables persist across loops
□ Units are consistent (ticks vs inches vs radians)
□ Telemetry is available for debugging
□ No blocking operations in control loop
```

### Common Anti-Patterns to Flag

```java
// 1. PID without feedforward on gravity system
output = kP * error;  // MISSING: + kG

// 2. Starting with I gain
double kI = 0.01;  // Should be 0 initially

// 3. Inconsistent loop timing with D
derivative = error - lastError;  // Should divide by dt

// 4. Unbounded integral
integral += error;  // Should have limits

// 5. Wrong error sign
error = current - target;  // Should be target - current

// 6. Blocking in control loop
Thread.sleep(100);  // NEVER do this

// 7. Magic numbers without explanation
output = 0.037 * error + 0.0042;  // What are these?
```

---

## Diagnostic Telemetry Template

Add this to any control system for debugging:

```java
public void updateTelemetry(Telemetry telemetry) {
    telemetry.addData("=== CONTROL DEBUG ===", "");

    // Setpoint and measurement
    telemetry.addData("Target", target);
    telemetry.addData("Current", current);
    telemetry.addData("Error", error);

    // Controller components
    telemetry.addData("P Output", kP * error);
    telemetry.addData("I Output", kI * integral);
    telemetry.addData("D Output", kD * derivative);
    telemetry.addData("FF Output", feedforward);
    telemetry.addData("Total Output", output);

    // State
    telemetry.addData("Integral", integral);
    telemetry.addData("At Target?", Math.abs(error) < tolerance);

    // Timing
    telemetry.addData("Loop dt (ms)", dt * 1000);

    telemetry.update();
}
```

---

## When to Ask for Help

If you've tried the above and still have issues:

1. **Capture telemetry data** - Log target, current, error, output over time
2. **Describe the symptom precisely** - "oscillates at 5Hz" not "doesn't work"
3. **Share your control code** - Include constants and the update loop
4. **Note physical setup** - Gear ratio, motor type, mechanism weight
5. **Mention what you've tried** - Helps avoid duplicate suggestions

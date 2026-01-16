# Control System Diagnostics

Troubleshooting guide for common control system problems.

## Quick Diagnosis

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| Motor doesn't move | Output not applied, gains too low | Check `motor.setPower()`, increase kP |
| Doesn't reach target | Missing feedforward | Add kG (elevator) or kG*cos(θ) (arm) |
| Oscillates around target | kP too high | Reduce kP, add kD |
| Overshoots then corrects | kP too high, no kD | Add kD, reduce kP |
| Drifts over time | Encoder reset, mechanical slip | Check encoder, mechanical connections |
| Jerky motion | kD too high, noisy sensor | Reduce kD, filter sensor |
| Slow response | kP too low | Increase kP |
| Works one direction only | Asymmetric friction, wrong FF sign | Check feedforward direction |

## Not Moving

**Diagnostic checklist:**
- [ ] Is `motor.setPower(output)` being called?
- [ ] Is output clamped correctly to [-1, 1]?
- [ ] Is error = target - current (not reversed)?
- [ ] Is kP high enough? (start at 0.001)

**Common fixes:**
```java
// Wrong: calculating but not applying
double output = kP * error;
// Missing: motor.setPower(output);

// Wrong: inverted error
double error = current - target;  // Should be target - current

// Wrong: gains too low
double kP = 0.000001;  // Too small, try 0.001
```

## Not Reaching Target (Steady-State Error)

**Root cause:** PID alone can't fight gravity. Need feedforward.

```java
// Wrong: PID only
double output = kP * error;

// Correct: Add feedforward
double output = kP * error + kG;  // Elevator
double output = kP * error + kG * Math.cos(angle);  // Arm
```

**Finding kG:**
1. Set kP = 0
2. Raise elevator to mid-height
3. Increase constant power until it holds
4. That power value = kG

## Oscillation

**Types:**
- Fast oscillation (jitter) → kD too high or noisy sensor
- Medium oscillation → kP too high
- Slow oscillation → kI too high

**Fixes:**
```java
// Reduce kP
double kP = 0.05;  // If oscillating, try 0.03

// Add derivative damping
double derivative = error - lastError;
double output = kP * error + kD * derivative;

// Limit integral
integral = Math.max(-1000, Math.min(1000, integral));
```

## Overshoot

**Fixes:**
```java
// Add D term
double output = kP * error + kD * derivative;

// Limit max power
output = Math.max(-0.5, Math.min(0.5, output));
```

## Drift

**Common causes:**
- Encoder overflow/reset
- Belt slip or loose setscrew
- Wrong feedforward direction

```java
// Check feedforward direction
double gravityFF = kG;  // Positive = up for elevator
// If drifting down, kG might be negative when it should be positive
```

## Jitter

**Fix noisy derivative:**
```java
// Filter position before differentiating
double alpha = 0.1;
filteredPosition = alpha * position + (1 - alpha) * filteredPosition;
double derivative = (filteredPosition - lastFiltered) / dt;
```

## Code Review Checklist

### Structure
- [ ] Motor set to BRAKE mode (for position control)
- [ ] Position limits defined and enforced
- [ ] Output clamped to [-1, 1]
- [ ] Integral has anti-windup limits

### Control Design
- [ ] Feedforward used for gravity/velocity systems
- [ ] Feedforward tuned BEFORE PID
- [ ] kI only used if steady-state error exists
- [ ] Loop timing accounted for in derivative

### Common Anti-Patterns
```java
// 1. PID without feedforward on gravity system
output = kP * error;  // WRONG: missing + kG

// 2. Wrong error sign
error = current - target;  // WRONG: should be target - current

// 3. Unbounded integral
integral += error;  // WRONG: needs limits

// 4. Inconsistent loop timing with D
derivative = error - lastError;  // WRONG: should divide by dt
```

## Debug Telemetry

Add this to any controller for debugging:

```java
telemetry.addData("Target", target);
telemetry.addData("Current", current);
telemetry.addData("Error", error);
telemetry.addData("P Output", kP * error);
telemetry.addData("D Output", kD * derivative);
telemetry.addData("FF Output", feedforward);
telemetry.addData("Total Output", output);
telemetry.update();
```

## When to Ask for Help

Capture this information before asking:
1. Telemetry data (target, current, error, output over time)
2. Symptom description ("oscillates at 5Hz" not "doesn't work")
3. Control code with constants
4. Physical setup (motor, gear ratio, mechanism type)
5. What you've already tried

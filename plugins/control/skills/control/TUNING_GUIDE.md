# Control System Tuning Guide

Step-by-step methodology for tuning any control system in FTC.

## Philosophy: Feedforward First

**The key insight**: Feedforward should do 80-90% of the work. PID handles the remaining 10-20%.

Why this matters:
- PID reacts to **error** (already wrong)
- Feedforward **predicts** the right output (proactive)
- A well-tuned FF means PID only handles disturbances

**If you're struggling with PID tuning, your feedforward is probably wrong.**

## Tuning Order

Always tune in this order:

```
1. Feedforward (kG, kV, kS) → Gets you 80% there
2. P gain                   → Adds correction for error
3. D gain                   → Reduces oscillation (if needed)
4. I gain                   → Fixes steady-state error (rarely needed)
```

## Step 1: Find Feedforward Constants

### For Elevators: Finding kG

kG = power required to hold the elevator against gravity

**Procedure:**
1. Set all PID gains to 0 (kP = 0, kI = 0, kD = 0)
2. Write a test OpMode that lets you adjust power with a gamepad
3. Manually raise the elevator to mid-height
4. Slowly increase power until the elevator holds position
5. That power value is your `kG`

```java
// Test OpMode for finding kG
@TeleOp(name = "Elevator kG Finder")
public class ElevatorKGFinder extends LinearOpMode {
    @Override
    public void runOpMode() {
        DcMotorEx elevator = hardwareMap.get(DcMotorEx.class, "elevator");
        elevator.setMode(DcMotor.RunMode.RUN_WITHOUT_ENCODER);

        double power = 0;

        waitForStart();

        while (opModeIsActive()) {
            // Adjust power with triggers
            power += gamepad1.right_trigger * 0.001;
            power -= gamepad1.left_trigger * 0.001;
            power = Math.max(0, Math.min(1, power));

            elevator.setPower(power);

            telemetry.addData("Power (kG)", "%.3f", power);
            telemetry.addData("Position", elevator.getCurrentPosition());
            telemetry.addData("Instructions", "Adjust until elevator holds still");
            telemetry.update();
        }
    }
}
```

**Expected values**: Typically 0.05 to 0.25 depending on gear ratio and weight.

### For Arms: Finding kG

kG = power required to hold the arm at **horizontal position**

**Procedure:**
1. Set all PID gains to 0
2. Move arm to horizontal position (perpendicular to vertical)
3. Find power to hold at horizontal
4. That value is your `kG`

**Important**: The arm's gravity compensation uses `kG * cos(angle)`, so:
- At horizontal (angle = 0): full kG is applied
- At vertical (angle = π/2): zero gravity compensation

```java
// Test OpMode for finding arm kG
@TeleOp(name = "Arm kG Finder")
public class ArmKGFinder extends LinearOpMode {
    @Override
    public void runOpMode() {
        DcMotorEx arm = hardwareMap.get(DcMotorEx.class, "arm");
        arm.setMode(DcMotor.RunMode.RUN_WITHOUT_ENCODER);

        double power = 0;

        waitForStart();

        while (opModeIsActive()) {
            power += gamepad1.right_trigger * 0.001;
            power -= gamepad1.left_trigger * 0.001;
            power = Math.max(-1, Math.min(1, power));

            arm.setPower(power);

            telemetry.addData("Power (kG at horizontal)", "%.3f", power);
            telemetry.addData("Position", arm.getCurrentPosition());
            telemetry.addData("Instructions", "Move arm to horizontal, find holding power");
            telemetry.update();
        }
    }
}
```

**Expected values**: Typically 0.05 to 0.4 depending on arm length and weight.

### For Flywheels: Finding kV

kV = power per unit velocity

**Procedure:**
1. Set all PID gains to 0
2. Apply a known power (e.g., 0.5)
3. Wait for velocity to stabilize
4. Record the velocity
5. kV = power / velocity

```java
// Test OpMode for finding flywheel kV
@TeleOp(name = "Flywheel kV Finder")
public class FlywheelKVFinder extends LinearOpMode {
    @Override
    public void runOpMode() {
        DcMotorEx flywheel = hardwareMap.get(DcMotorEx.class, "flywheel");
        flywheel.setMode(DcMotor.RunMode.RUN_WITHOUT_ENCODER);

        double power = 0;

        waitForStart();

        while (opModeIsActive()) {
            // Set power with left stick
            power = gamepad1.left_stick_y * -1;
            flywheel.setPower(power);

            double velocity = flywheel.getVelocity();
            double calculatedKV = (velocity != 0) ? power / velocity : 0;

            telemetry.addData("Power", "%.3f", power);
            telemetry.addData("Velocity (ticks/sec)", "%.1f", velocity);
            telemetry.addData("Calculated kV", "%.6f", calculatedKV);
            telemetry.addData("Instructions", "Apply steady power, wait for velocity to stabilize");
            telemetry.update();
        }
    }
}
```

**Expected values**: Very small numbers, typically 0.0001 to 0.001.

### Finding kS (Static Friction)

kS = minimum power to overcome static friction and start moving

**Procedure:**
1. With mechanism at rest, slowly increase power
2. Note the power when it just starts moving
3. That power is your `kS`

**Expected values**: Typically 0.02 to 0.1.

## Step 2: Tune P Gain (kP)

After feedforward is set, add proportional gain.

**Procedure:**
1. Start with a very small kP
   - Position control: start at 0.001
   - Velocity control: start at 0.0001
2. Test by setting a target and observing response
3. Double kP until you see oscillation
4. Back off to 60-70% of the oscillating value

**Signs kP is too high:**
- Oscillation around the target
- Overshoot followed by correction

**Signs kP is too low:**
- Very slow approach to target
- Doesn't reach target

```java
// Example: Testing P gain
double[] kP_values = {0.001, 0.002, 0.004, 0.008, 0.016, 0.032};

// Try each value, look for oscillation
// Good kP is slightly below where oscillation starts
```

## Step 3: Tune D Gain (kD)

Add derivative gain only if you're seeing oscillation that P alone can't fix.

**Procedure:**
1. If system oscillates with tuned kP, add small kD
2. Start with kD = kP / 10
3. Increase until oscillation stops
4. Don't over-tune - too much D causes jitter

**Signs kD is too high:**
- Jittery, noisy output
- Slow to respond (D resists all change)
- Amplifies sensor noise

**Signs kD is right:**
- Smooth approach to target
- No oscillation
- Quick settling

**Note**: D gain is sensitive to loop time. If your loop runs inconsistently, D will behave erratically.

## Step 4: Tune I Gain (kI) - Usually Not Needed

**Only add I gain if:**
1. Feedforward is correctly tuned
2. P and D are tuned
3. There's still persistent steady-state error

**Procedure:**
1. Start with kI = kP / 100
2. Increase slowly
3. Watch for overshoot and oscillation

**Signs kI is too high:**
- Overshoot
- Slow oscillation
- "Windup" - mechanism overshoots badly after being held back

**Anti-windup**: Always limit your integral term:
```java
integral += error;
integral = Math.max(-maxIntegral, Math.min(maxIntegral, integral));
```

## Common Problems and Solutions

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| Fast oscillation | kP too high | Reduce kP by 30-50% |
| Slow oscillation | kI too high or no kD | Reduce kI, add kD |
| Never reaches target | kP too low | Increase kP |
| Overshoots then settles | kP too high, no kD | Add kD, reduce kP slightly |
| Jittery output | kD too high | Reduce kD, add sensor filter |
| Drifts when holding | Missing feedforward | Add kG for gravity systems |
| Windup overshoot | kI too high, no limits | Add integral limits, reduce kI |
| Slow in one direction | Asymmetric friction | Use different kS for each direction |
| Works cold, fails hot | Motor heating changes kV | Re-tune when warm, or add margin |

## Tuning Checklist

### Before You Start
- [ ] Motor direction is correct
- [ ] Encoder is working and counting correctly
- [ ] Mechanism moves freely (no binding)
- [ ] Limits are set to prevent damage

### Feedforward Tuning
- [ ] kG found for gravity systems (elevator/arm)
- [ ] kV found for velocity systems (flywheel)
- [ ] kS found if needed (high friction systems)
- [ ] Mechanism roughly tracks target with FF alone

### PID Tuning
- [ ] kP tuned to just below oscillation
- [ ] kD added if oscillation present
- [ ] kI added only if steady-state error persists
- [ ] Integral limits added if using kI

### Final Validation
- [ ] Full range of motion tested
- [ ] Both directions tested
- [ ] Rapid target changes tested
- [ ] Long hold at position tested
- [ ] Tested with and without load
- [ ] Tested after motors warm up

## Live Tuning Tips

### Using FTC Dashboard

```java
@Config  // Makes these tunable in dashboard
public class TuningConstants {
    public static double ELEVATOR_KP = 0.005;
    public static double ELEVATOR_KD = 0.001;
    public static double ELEVATOR_KG = 0.15;
}
```

### Using Panels (NextFTC)

```kotlin
object TuningConfig {
    @Editable var ELEVATOR_KP = 0.005
    @Editable var ELEVATOR_KD = 0.001
    @Editable var ELEVATOR_KG = 0.15
}
```

### Logging for Analysis

```java
telemetry.addData("Target", targetPosition);
telemetry.addData("Current", currentPosition);
telemetry.addData("Error", error);
telemetry.addData("P Output", kP * error);
telemetry.addData("D Output", kD * derivative);
telemetry.addData("FF Output", feedforward);
telemetry.addData("Total Output", output);
```

## Advanced: Gain Scheduling

Sometimes a single set of gains doesn't work across the full range. Solutions:

**Position-dependent gains:**
```java
// Lower gains at extremes where mechanism is weaker
double gainFactor = 1.0;
if (position < 500 || position > 2500) {
    gainFactor = 0.7;
}
double effectiveKP = kP * gainFactor;
```

**Velocity-dependent gains:**
```java
// Higher P at low velocity for better holding
if (Math.abs(velocity) < 100) {
    kP = kP_hold;  // Higher for position holding
} else {
    kP = kP_moving;  // Lower while moving
}
```

## Debugging: Step Response Test

The step response tells you everything about your tuning:

```java
// Step response test
@TeleOp(name = "Step Response Test")
public class StepResponseTest extends LinearOpMode {
    @Override
    public void runOpMode() {
        // Initialize your subsystem
        ElapsedTime timer = new ElapsedTime();

        waitForStart();

        // Set a target (step input)
        subsystem.setTarget(1000);
        timer.reset();

        // Log the response
        while (opModeIsActive() && timer.seconds() < 5) {
            subsystem.update();
            telemetry.addData("Time", "%.3f", timer.seconds());
            telemetry.addData("Position", subsystem.getCurrentPosition());
            telemetry.addData("Target", 1000);
            telemetry.update();
        }
    }
}
```

**What to look for:**
- Rise time: How fast it reaches target
- Overshoot: Does it go past target?
- Settling time: How long until stable?
- Steady-state error: Does it reach exactly the target?

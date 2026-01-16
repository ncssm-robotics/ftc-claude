# Advanced Control Methods

Advanced techniques for experienced teams. **Most FTC teams don't need these.** Get PID+feedforward working well first.

## When to Consider Advanced Control

Use only when:
- Simple PID+FF gives >10% steady-state error after proper tuning
- Mechanism has multiple coupled degrees of freedom
- You need optimal performance (state/worlds competitions)
- You've maxed out what PID+FF can do

**If PID isn't working, go back and tune feedforward properly first.**

## State-Space Control

Represents a system as state vector x (position, velocity, etc.) evolving over time:
```
x(k+1) = A * x(k) + B * u(k)    // State update
y(k)   = C * x(k)                // Measurement
```

**Use for:** Multi-variable systems, optimal control (LQR), state estimation

```java
public class StateSpaceFlywheel {
    // Model: v(k+1) = a * v(k) + b * u(k)
    private double a = 0.98;  // Velocity retention (friction)
    private double b = 50.0;  // Motor gain
    private double K = 0.01;  // Feedback gain (from LQR or pole placement)

    private double velocityEstimate = 0;

    public double calculate(double measuredVel, double targetVel, double lastOutput) {
        // Predict next state using model
        velocityEstimate = a * velocityEstimate + b * lastOutput;
        // Correct with measurement
        velocityEstimate = 0.5 * velocityEstimate + 0.5 * measuredVel;
        // State feedback control
        return K * (targetVel - velocityEstimate);
    }
}
```

## LQR (Linear Quadratic Regulator)

Finds optimal feedback gain K that minimizes cost J = Σ(x'Qx + u'Ru).

- **Q** = state error weight (higher = faster response)
- **R** = control effort weight (higher = gentler on motors)

```java
// For 1D system, optimal K from Riccati equation
public class SimpleLQR {
    private double a = 0.98, b = 0.5;
    private double Q = 1.0, R = 0.1;
    private double K;

    public SimpleLQR() {
        K = computeOptimalGain();
    }

    private double computeOptimalGain() {
        double P = Q;
        for (int i = 0; i < 100; i++) {
            double newP = Q + a*a*P - (a*P*b)*(a*P*b) / (R + b*b*P);
            if (Math.abs(newP - P) < 0.0001) break;
            P = newP;
        }
        return b * P / (R + b*b*P);
    }

    public double calculate(double current, double target) {
        return K * (target - current);
    }
}
```

## Kalman Filters

Estimates true state from noisy measurements by combining prediction and correction.

**Use for:** Noisy sensors, estimating velocity from position encoder, sensor fusion

```java
public class SimpleKalmanFilter {
    private double x = 0;  // State estimate
    private double P = 1;  // Uncertainty
    private double Q = 0.1;  // Process noise (model uncertainty)
    private double R = 1.0;  // Measurement noise (sensor uncertainty)

    // Simple model: x(k+1) = x(k) + u(k) (integrator)
    public double update(double measurement, double controlInput) {
        // Predict: x_pred = A*x + B*u (here A=1, B=1)
        double x_pred = x + controlInput;
        double P_pred = P + Q;

        // Update
        double K = P_pred / (P_pred + R);  // Kalman gain
        x = x_pred + K * (measurement - x_pred);
        P = (1 - K) * P_pred;

        return x;
    }
}
```

## Motion Profiling

Plans smooth trajectory through velocity/acceleration limits.

**Trapezoidal profile:** Accelerate → Cruise → Decelerate

```java
public class TrapezoidalProfile {
    private double maxVel, maxAccel;
    private double startPos, endPos, direction;
    private double accelTime, cruiseTime, totalTime;

    public TrapezoidalProfile(double maxVel, double maxAccel) {
        this.maxVel = maxVel;
        this.maxAccel = maxAccel;
    }

    public void setTarget(double start, double end) {
        startPos = start;
        endPos = end;
        direction = Math.signum(end - start);
        double distance = Math.abs(end - start);

        accelTime = maxVel / maxAccel;
        double accelDist = 0.5 * maxAccel * accelTime * accelTime;

        if (2 * accelDist > distance) {
            // Triangle profile
            accelTime = Math.sqrt(distance / maxAccel);
            cruiseTime = 0;
        } else {
            // Trapezoidal
            cruiseTime = (distance - 2 * accelDist) / maxVel;
        }
        totalTime = 2 * accelTime + cruiseTime;
    }

    public double getPosition(double time) {
        if (time <= 0) return startPos;
        if (time >= totalTime) return endPos;

        double pos;
        if (time < accelTime) {
            pos = 0.5 * maxAccel * time * time;
        } else if (time < accelTime + cruiseTime) {
            double t = time - accelTime;
            pos = 0.5 * maxAccel * accelTime * accelTime + maxVel * t;
        } else {
            double t = time - accelTime - cruiseTime;
            double accelDist = 0.5 * maxAccel * accelTime * accelTime;
            pos = accelDist + maxVel * cruiseTime + maxVel * t - 0.5 * maxAccel * t * t;
        }
        return startPos + direction * pos;
    }
}
```

## Cascaded Control

Nested loops where outer loop output is inner loop setpoint:
```
Position setpoint → [Pos Controller] → Velocity setpoint → [Vel Controller] → Motor
```

```java
public class CascadedController {
    private double kP_pos = 0.05;
    private double kP_vel = 0.001;
    private double kV = 0.0001;
    private double maxVelocity = 2000;

    public double calculate(double currentPos, double currentVel, double targetPos) {
        // Outer: position → velocity setpoint
        double targetVel = kP_pos * (targetPos - currentPos);
        targetVel = Math.max(-maxVelocity, Math.min(maxVelocity, targetVel));

        // Inner: velocity → power
        double velError = targetVel - currentVel;
        return kP_vel * velError + kV * targetVel;
    }
}
```

## External Resources

- [CTRL ALT FTC](https://www.ctrlaltftc.com/) - Control theory for FTC
- [WPILib State-Space](https://docs.wpilib.org/en/stable/docs/software/advanced-controls/state-space/state-space-intro.html)
- [Controls Engineering in FRC](https://file.tavsys.net/control/controls-engineering-in-frc.pdf) - Tyler Veness
- [Game Manual 0 - Control](https://gm0.org/en/latest/docs/software/concepts/control-loops.html)

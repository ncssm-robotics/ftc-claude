# Advanced Control Methods

Advanced control techniques for experienced teams. **Most FTC teams don't need these.** Get PID+feedforward working well first.

## When to Consider Advanced Control

Use advanced methods only when:
- Simple PID+FF gives >10% steady-state error after proper tuning
- Mechanism has multiple coupled degrees of freedom
- You need optimal performance (state competitions, worlds)
- You have a controls mentor to help debug
- You've maxed out what PID+FF can do

**If you're reading this because PID isn't working, go back and tune feedforward properly first.**

---

## State-Space Control

### What It Is

State-space models represent a system as:
- **State vector (x)**: All variables describing the system (position, velocity, etc.)
- **State equation**: How state evolves over time
- **Output equation**: What we can measure

**Model form:**
```
x(k+1) = A * x(k) + B * u(k)    // State update
y(k)   = C * x(k)                // Measurement
```

Where:
- `x` = state vector (e.g., [position, velocity])
- `u` = control input (motor power)
- `y` = measured output
- `A`, `B`, `C` = system matrices

### When to Use

- Multi-variable systems (controlling position AND velocity together)
- When you want optimal control (LQR)
- When you need state estimation (observers/Kalman)

### Simple Example: Flywheel

For a flywheel, the state is velocity, and the dynamics are:

```
velocity(k+1) = a * velocity(k) + b * power(k)
```

Where:
- `a` = decay factor (friction)
- `b` = motor gain

```java
public class StateSpaceFlywheel {
    // System model parameters (characterize your system)
    private double a = 0.98;  // Velocity retention (1 = no friction)
    private double b = 50.0;  // Motor gain (velocity per unit power)

    // Controller gain
    private double K = 0.01;  // State feedback gain

    private double velocity = 0;  // Estimated state

    public double calculate(double measuredVelocity, double targetVelocity) {
        // Update state estimate with measurement
        velocity = measuredVelocity;

        // State feedback: u = K * (target - current)
        double error = targetVelocity - velocity;
        return K * error;
    }
}
```

### Advantages Over PID

- Naturally handles multiple states
- Can be mathematically optimized (LQR)
- Provides framework for state estimation

### Disadvantages

- Requires accurate system model
- More complex to implement and debug
- Overkill for simple mechanisms

---

## LQR (Linear Quadratic Regulator)

### What It Is

LQR finds the **optimal** state feedback gain K that minimizes a cost function balancing:
- **Q**: How much we care about state error
- **R**: How much we care about control effort

**Cost function:**
```
J = sum(x'Qx + u'Ru)
```

### Why Use LQR

- Mathematically optimal for linear systems
- Systematic way to tune multi-state controllers
- Balances performance vs. control effort

### Simple Implementation

For a single-state system (like a flywheel), LQR simplifies to:

```java
public class SimpleLQR {
    // System model
    private double a = 0.98;  // State transition
    private double b = 0.5;   // Control input gain

    // LQR weights
    private double Q = 1.0;   // State error weight
    private double R = 0.1;   // Control effort weight

    // Computed optimal gain (solve Riccati equation)
    private double K;

    public SimpleLQR() {
        // For simple 1D case, optimal K can be computed
        // In practice, use numerical solver
        K = computeOptimalGain();
    }

    private double computeOptimalGain() {
        // Simplified: K = B' * P / R where P solves Riccati equation
        // For 1D: P = Q + a^2 * P - (a * P * b)^2 / (R + b^2 * P)
        // Iterate to find P, then K = b * P / (R + b^2 * P)

        double P = Q;  // Initial guess
        for (int i = 0; i < 100; i++) {
            double newP = Q + a * a * P - (a * P * b) * (a * P * b) / (R + b * b * P);
            if (Math.abs(newP - P) < 0.0001) break;
            P = newP;
        }
        return b * P / (R + b * b * P);
    }

    public double calculate(double current, double target) {
        double error = target - current;
        return K * error;  // Optimal control
    }
}
```

### Practical Notes

- Q/R ratio matters more than absolute values
- Higher Q = faster response, more aggressive control
- Higher R = slower response, gentler on motors
- WPILib has built-in LQR solver (FRC, not FTC)

---

## Kalman Filters

### What It Is

A Kalman filter optimally estimates the true state from noisy measurements. It combines:
- **Prediction**: Where we expect to be based on model
- **Correction**: Adjust based on measurement

### When to Use

- Sensor data is noisy
- Need to estimate velocity from position-only encoder
- Fusing multiple sensors
- Sensor has significant latency

### Simple 1D Kalman Filter

```java
public class SimpleKalmanFilter {
    // State estimate
    private double x = 0;  // Position estimate
    private double P = 1;  // Estimate uncertainty

    // Model parameters
    private double A = 1;  // State transition (position stays same if no input)
    private double B = 1;  // Control input gain
    private double Q = 0.1;  // Process noise (model uncertainty)
    private double R = 1.0;  // Measurement noise (sensor uncertainty)

    public double update(double measurement, double controlInput) {
        // Predict step
        double x_pred = A * x + B * controlInput;
        double P_pred = A * P * A + Q;

        // Update step
        double K = P_pred / (P_pred + R);  // Kalman gain
        x = x_pred + K * (measurement - x_pred);
        P = (1 - K) * P_pred;

        return x;  // Filtered estimate
    }
}
```

### Position + Velocity Estimation

```java
public class PositionVelocityKalman {
    // State: [position, velocity]
    private double pos = 0;
    private double vel = 0;

    // Covariance matrix (simplified as scalars)
    private double P_pos = 1;
    private double P_vel = 1;

    // Tuning parameters
    private double Q_pos = 0.01;  // Process noise - position
    private double Q_vel = 0.1;   // Process noise - velocity
    private double R = 1.0;       // Measurement noise

    private double dt = 0.02;  // Loop time in seconds

    public void update(double measuredPosition) {
        // Predict
        double pos_pred = pos + vel * dt;
        double vel_pred = vel;  // Assume constant velocity

        double P_pos_pred = P_pos + 2 * dt * P_vel + Q_pos;
        double P_vel_pred = P_vel + Q_vel;

        // Update (only position is measured)
        double K_pos = P_pos_pred / (P_pos_pred + R);
        double innovation = measuredPosition - pos_pred;

        pos = pos_pred + K_pos * innovation;
        vel = vel_pred + (K_pos / dt) * innovation;  // Implicit velocity update

        P_pos = (1 - K_pos) * P_pos_pred;
        P_vel = P_vel_pred - K_pos * K_pos * P_vel_pred;
    }

    public double getPosition() { return pos; }
    public double getVelocity() { return vel; }
}
```

### Practical Notes

- Q/R ratio determines filter responsiveness
- High Q = trust model less, respond to measurements faster
- High R = trust measurements less, smoother output
- Can estimate velocity even without velocity sensor

---

## Observer-Based Control

### What It Is

An observer estimates unmeasured states (like velocity) from measured states (like position). The controller then uses the estimated states.

### Luenberger Observer

```java
public class LuenbergerObserver {
    // Estimated states
    private double pos_est = 0;
    private double vel_est = 0;

    // Observer gains (tune these)
    private double L_pos = 0.5;  // Position correction gain
    private double L_vel = 0.1;  // Velocity correction gain

    private double dt = 0.02;

    public void update(double measuredPosition, double controlInput) {
        // Predict based on model
        double pos_pred = pos_est + vel_est * dt;
        double vel_pred = vel_est + controlInput * dt;  // Simplified model

        // Correct based on measurement error
        double error = measuredPosition - pos_pred;
        pos_est = pos_pred + L_pos * error;
        vel_est = vel_pred + L_vel * error;
    }

    public double getVelocityEstimate() { return vel_est; }
}
```

### Using Observer with Controller

```java
public class ObserverBasedController {
    private LuenbergerObserver observer = new LuenbergerObserver();

    // Position controller
    private double kP_pos = 0.01;
    // Velocity controller (inner loop)
    private double kP_vel = 0.001;

    public double calculate(double measuredPosition, double targetPosition) {
        // Update observer
        double lastOutput = 0;  // Track this
        observer.update(measuredPosition, lastOutput);

        // Cascaded control using estimated velocity
        double posError = targetPosition - measuredPosition;
        double targetVelocity = kP_pos * posError;

        double velError = targetVelocity - observer.getVelocityEstimate();
        double output = kP_vel * velError;

        return output;
    }
}
```

---

## Motion Profiling

### What It Is

Motion profiling plans a smooth trajectory through velocity and acceleration limits. Instead of jumping to the target, the setpoint moves smoothly over time.

### Trapezoidal Profile

The classic motion profile with three phases:
1. **Acceleration**: Speed up at max acceleration
2. **Cruise**: Hold max velocity
3. **Deceleration**: Slow down at max deceleration

```java
public class TrapezoidalProfile {
    private double maxVel;
    private double maxAccel;

    private double startPos;
    private double endPos;
    private double direction;

    private double accelTime;
    private double cruiseTime;
    private double decelTime;
    private double totalTime;

    public TrapezoidalProfile(double maxVel, double maxAccel) {
        this.maxVel = maxVel;
        this.maxAccel = maxAccel;
    }

    public void setTarget(double start, double end) {
        startPos = start;
        endPos = end;
        direction = Math.signum(end - start);

        double distance = Math.abs(end - start);

        // Time to accelerate to max velocity
        accelTime = maxVel / maxAccel;
        double accelDist = 0.5 * maxAccel * accelTime * accelTime;

        if (2 * accelDist > distance) {
            // Triangle profile (can't reach max velocity)
            accelTime = Math.sqrt(distance / maxAccel);
            cruiseTime = 0;
            decelTime = accelTime;
        } else {
            // Trapezoidal profile
            double cruiseDist = distance - 2 * accelDist;
            cruiseTime = cruiseDist / maxVel;
            decelTime = accelTime;
        }

        totalTime = accelTime + cruiseTime + decelTime;
    }

    public double getPosition(double time) {
        if (time < 0) return startPos;
        if (time > totalTime) return endPos;

        double pos;

        if (time < accelTime) {
            // Accelerating
            pos = 0.5 * maxAccel * time * time;
        } else if (time < accelTime + cruiseTime) {
            // Cruising
            double t = time - accelTime;
            pos = 0.5 * maxAccel * accelTime * accelTime + maxVel * t;
        } else {
            // Decelerating
            double t = time - accelTime - cruiseTime;
            double accelDist = 0.5 * maxAccel * accelTime * accelTime;
            double cruiseDist = maxVel * cruiseTime;
            pos = accelDist + cruiseDist + maxVel * t - 0.5 * maxAccel * t * t;
        }

        return startPos + direction * pos;
    }

    public double getVelocity(double time) {
        if (time < 0 || time > totalTime) return 0;

        if (time < accelTime) {
            return direction * maxAccel * time;
        } else if (time < accelTime + cruiseTime) {
            return direction * maxVel;
        } else {
            double t = time - accelTime - cruiseTime;
            return direction * (maxVel - maxAccel * t);
        }
    }

    public boolean isFinished(double time) {
        return time >= totalTime;
    }
}
```

### Using Motion Profile with Controller

```java
public class ProfiledController {
    private TrapezoidalProfile profile;
    private SimplePID positionPID;
    private double kV;  // Velocity feedforward
    private ElapsedTime timer;

    public ProfiledController(double maxVel, double maxAccel, double kP, double kV) {
        profile = new TrapezoidalProfile(maxVel, maxAccel);
        positionPID = new SimplePID(kP, 0, 0);
        this.kV = kV;
        timer = new ElapsedTime();
    }

    public void setTarget(double current, double target) {
        profile.setTarget(current, target);
        timer.reset();
    }

    public double calculate(double currentPosition) {
        double t = timer.seconds();

        // Get profiled setpoint
        double targetPos = profile.getPosition(t);
        double targetVel = profile.getVelocity(t);

        // PID on position error from profiled setpoint
        double pidOutput = positionPID.calculate(currentPosition, targetPos);

        // Feedforward on profiled velocity
        double ffOutput = kV * targetVel;

        return pidOutput + ffOutput;
    }

    public boolean isFinished() {
        return profile.isFinished(timer.seconds());
    }
}
```

---

## Cascaded Control

### What It Is

Nested control loops where the outer loop's output is the inner loop's setpoint.

**Structure:**
```
[Position setpoint] → [Position Controller] → [Velocity setpoint] → [Velocity Controller] → [Motor power]
```

### Advantages

- Inner loop responds faster
- Can tune loops independently
- Natural way to add velocity limiting

### Implementation

```java
public class CascadedController {
    // Outer loop (position)
    private double kP_pos = 0.05;

    // Inner loop (velocity)
    private double kP_vel = 0.001;
    private double kV = 0.0001;  // Velocity feedforward

    private double maxVelocity = 2000;  // Velocity limit

    public double calculate(double currentPos, double currentVel, double targetPos) {
        // Outer loop: position error → velocity setpoint
        double posError = targetPos - currentPos;
        double targetVelocity = kP_pos * posError;

        // Clamp velocity setpoint
        targetVelocity = Math.max(-maxVelocity, Math.min(maxVelocity, targetVelocity));

        // Inner loop: velocity error → motor power
        double velError = targetVelocity - currentVel;
        double pidOutput = kP_vel * velError;
        double ffOutput = kV * targetVelocity;

        return pidOutput + ffOutput;
    }
}
```

---

## External Resources

- [CTRL ALT FTC](https://www.ctrlaltftc.com/) - Control theory for FTC
- [WPILib State-Space Control](https://docs.wpilib.org/en/stable/docs/software/advanced-controls/state-space/state-space-intro.html)
- [Controls Engineering in FRC](https://file.tavsys.net/control/controls-engineering-in-frc.pdf) - Tyler Veness (FRC, but concepts apply)
- [Game Manual 0 - Control](https://gm0.org/en/latest/docs/software/concepts/control-loops.html)

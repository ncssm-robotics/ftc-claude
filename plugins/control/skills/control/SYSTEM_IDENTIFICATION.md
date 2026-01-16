# System Identification for FTC

Physics-based modeling to calculate optimal control gains from measured robot data.

## When to Use SysID vs Empirical Tuning

| Scenario | Method | Rationale |
|----------|--------|-----------|
| Day before competition | Empirical | No time for analysis |
| New mechanism design | SysID | Understand physical parameters |
| Optimal performance needed | SysID + refinement | Get 90% there with math |
| Limited robot access (<1hr) | Empirical | Can't iterate on data |

## Quick Start

```bash
# 1. Select model structure
uv run scripts/select_model.py --mechanism elevator --quick

# 2. Collect data (run step test OpMode, save telemetry)

# 3. Identify parameters
uv run scripts/identify_params.py --data sysid_data.json --auto-select

# 4. Validate model
uv run scripts/validate_model.py --model identified_model.json

# 5. Calculate gains
uv run scripts/calculate_gains.py --model identified_model.json --rise-time 1.0
```

## Model Types

| Model | Parameters | Use Case |
|-------|------------|----------|
| First-order | K, τ | Flywheels, turrets |
| First-order + gravity | K, τ, kg | Elevators, arms (limited range) |
| Second-order | K, ωn, ζ | Mechanisms with overshoot/oscillation |
| Angle-dependent | K, τ, kg(θ) | Arms with large range of motion |

## Data Collection

### Step Input Test (Recommended)

```java
@Autonomous(name = "SysID Step Test")
public class StepTestOpMode extends LinearOpMode {
    @Override
    public void runOpMode() {
        DcMotorEx motor = hardwareMap.get(DcMotorEx.class, "mechanism");
        motor.setMode(DcMotor.RunMode.RUN_WITHOUT_ENCODER);

        waitForStart();

        double testPower = 0.4;
        double testDuration = 3.0;  // Should be > 5× time constant
        ElapsedTime timer = new ElapsedTime();

        motor.setPower(testPower);

        while (opModeIsActive() && timer.seconds() < testDuration) {
            telemetry.addData("time", timer.seconds());
            telemetry.addData("power", testPower);
            telemetry.addData("position", motor.getCurrentPosition());
            telemetry.addData("velocity", motor.getVelocity());
            telemetry.update();
            sleep(20);  // 50 Hz sampling
        }

        motor.setPower(0);
    }
}
```

### Data Quality Checklist

- [ ] Duration: >5× expected time constant (typically 3-10 seconds)
- [ ] Sample rate: ≥20 Hz (50 Hz preferred)
- [ ] Signal amplitude: Large motion (hundreds of ticks)
- [ ] Multiple runs: At least 3 runs, average results
- [ ] Fresh battery: >12.5V for consistent motor behavior
- [ ] No limit hits: Stay within safe range

## Identification

### First-Order Model

For step response data, identify K and τ:

```python
from scipy.optimize import curve_fit
import numpy as np

def first_order_response(t, K, tau, y0):
    return y0 + K * (1 - np.exp(-t / tau))

# Load data
data = np.loadtxt('step_test.csv', delimiter=',', skiprows=1)
time, position = data[:, 0], data[:, 2]
input_power = 0.4

# Fit model
params, _ = curve_fit(first_order_response, time, position,
                      p0=[position[-1]/input_power, 0.5, position[0]])
K, tau = params[0], params[1]

print(f"K = {K:.1f} ticks/power, τ = {tau:.3f} s")
```

### Validation Metrics

| Metric | Good | Acceptable | Poor |
|--------|------|------------|------|
| R² | >0.95 | 0.85-0.95 | <0.85 |
| NRMSE | <3% | 3-10% | >10% |
| Parameter confidence | >0.9 | 0.8-0.9 | <0.8 |

**If R² < 0.85:** Don't use the model. Collect cleaner data or try simpler model.

## Gain Calculation

### From First-Order Model

For desired closed-loop time constant τ_cl:

```
kP = (τ / τ_cl - 1) / K
```

**Example:** K=2500, τ=0.4s, want τ_cl=0.1s (4× faster)
```
kP = (0.4 / 0.1 - 1) / 2500 = 0.0012
```

### Ziegler-Nichols (from model)

| Controller | kP | kI | kD |
|------------|-----|-----|-----|
| P | 1/K | - | - |
| PI | 0.9/K | kP/(3τ) | - |
| PID | 1.2/K | kP/(2τ) | kP×τ/2 |

**Note:** Z-N often gives aggressive gains. Start at 50-70% and increase.

## Troubleshooting

### Poor Fit (R² < 0.85)

| Cause | Solution |
|-------|----------|
| Wrong model structure | Try simpler model (first-order) |
| Noisy data | Filter velocity, increase amplitude |
| Short duration | Run test longer (>5τ) |
| Mechanism binding | Fix mechanical issues first |

### Gains Don't Work on Robot

| Cause | Solution |
|-------|----------|
| Delays not modeled | Start at 50% of calculated gains |
| Battery voltage different | Tune with typical voltage |
| Model linearization invalid | Identify over full operating range |

## Scripts Reference

```bash
# List available models
uv run scripts/select_model.py --list-models

# Identify with specific model
uv run scripts/identify_params.py --data data.json --model first-order-gravity

# Calculate gains with constraints
uv run scripts/calculate_gains.py --model model.json --rise-time 0.5 --overshoot 5

# Validate on new data
uv run scripts/validate_model.py --model model.json --data validation.json
```

## External Resources

- [Controls Engineering in FRC](https://file.tavsys.net/control/controls-engineering-in-frc.pdf) - Tyler Veness
- [CTRL ALT FTC](https://www.ctrlaltftc.com/) - Control theory for FTC
- [Python Control Library](https://python-control.readthedocs.io/) - Transfer function analysis

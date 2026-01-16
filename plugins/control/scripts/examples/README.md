# Calculate Gains Examples

This directory contains example input files and expected outputs for the `calculate_gains.py` script.

## Example 1: First-Order Elevator with Gravity

Input: `elevator_first_order_model.json`

A typical elevator mechanism identified with first-order + gravity compensation model.

```bash
python3 ../calculate_gains.py \
  --model elevator_first_order_model.json \
  --rise-time 1.0 \
  --overshoot 10 \
  --output elevator_gains.json
```

Expected output:
- kP ≈ 0.34
- kD ≈ 0.76
- kG = 0.15 (gravity compensation)
- Predicted rise time: 1.0s
- Predicted overshoot: 10%

## Example 2: Second-Order Cable-Driven Mechanism

Input: `cable_second_order_model.json`

A cable-driven elevator or arm that shows oscillatory behavior (overshoot).

```bash
python3 ../calculate_gains.py \
  --model cable_second_order_model.json \
  --rise-time 0.8 \
  --overshoot 5 \
  --output cable_gains.json
```

Expected output:
- kP ≈ 0.0001 (very low, plant already has high gain)
- kD ≈ 0.04 (adds damping)
- kG = 0.15
- Predicted rise time: 0.8s
- Predicted overshoot: 5%

## Example 3: Ziegler-Nichols Tuning

Conservative tuning using model-based Ziegler-Nichols method (doesn't require rise time/overshoot specs).

```bash
python3 ../calculate_gains.py \
  --model elevator_first_order_model.json \
  --method model-based-zn \
  --output zn_gains.json
```

Expected output:
- Conservative gains
- ~10% overshoot typical for ZN
- Longer rise time (more damped)

## Example 4: Lambda Tuning for Smooth Response

Lambda tuning gives smooth, non-oscillatory response (no overshoot).

```bash
python3 ../calculate_gains.py \
  --model elevator_first_order_model.json \
  --method lambda-tuning \
  --lambda-factor 1.5 \
  --output lambda_gains.json
```

Expected output:
- 0% overshoot
- Smooth response
- Slower rise time (trade-off for smoothness)

## Testing the Gains

After calculating gains, test them on your robot:

```bash
# Option 1: Use /tune command with initial gains
/tune --initial-gains elevator_gains.json

# Option 2: Manually copy gains into your OpMode
# See the calculated_gains section in the JSON file
```

## Comparing Methods

To see which method works best for your mechanism, try all three:

```bash
# Pole placement
python3 ../calculate_gains.py --model model.json --rise-time 1.0 --overshoot 10 -o pp_gains.json

# Ziegler-Nichols
python3 ../calculate_gains.py --model model.json --method model-based-zn -o zn_gains.json

# Lambda tuning
python3 ../calculate_gains.py --model model.json --method lambda-tuning -o lambda_gains.json

# Then compare them on the robot
/tune --compare pp_gains.json zn_gains.json lambda_gains.json
```

## Understanding the Output

The `calculated_gains.json` file contains:

- **calculated_gains**: The kP, kD, kG values to use in your OpMode
- **predicted_performance**: Expected rise time, overshoot, settling time
- **robustness**: Parameter sensitivity analysis
- **design_parameters**: Internal design values (zeta, omega_n)

Always review the predicted performance before deploying. If predictions seem unrealistic (e.g., rise time too fast), adjust your specifications.

## Troubleshooting

### Gains seem too high/low

Check your model's K (gain) and tau (time constant) parameters. If they're off, the calculated gains will be wrong. Validate your model first with `validate_model.py`.

### Predicted performance doesn't match specifications

This can happen with second-order plants or when the model doesn't capture all dynamics. Use the predicted values as a starting point and refine on the robot.

### No stability margins shown

Stability margins are only calculated if scipy is installed. If not shown, the system likely has very good margins (very stable). Install scipy for detailed analysis:

```bash
uv pip install scipy
```

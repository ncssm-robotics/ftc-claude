# Model Selection Guide

Choose the right model structure for system identification based on your mechanism.

## Quick Decision Matrix

| Mechanism | Default Model | Upgrade If... |
|-----------|---------------|---------------|
| **Flywheel** | First-order | Overshoots → Second-order |
| **Turret** | First-order | Oscillates → Second-order |
| **Elevator** | First-order + gravity | Cable-driven → Second-order |
| **Arm** | First-order + gravity | Large angle range → Angle-dependent |

## Model Library

### Model 1: First-Order

**Transfer Function:** `G(s) = K / (τs + 1)`

| Parameter | Meaning |
|-----------|---------|
| K | Steady-state gain (output / input) |
| τ | Time constant (seconds to 63% of final) |

**Use for:** Flywheels, turrets, horizontal mechanisms

**Output:**
```json
{"model_type": "first_order", "parameters": {"K": 15.0, "tau": 2.5}}
```

### Model 2: First-Order + Gravity

**Equation:** `output = (K/τ) * error + kg`

| Parameter | Meaning |
|-----------|---------|
| K, τ | Same as first-order |
| kg | Constant power to hold against gravity |

**Use for:** Elevators, lifts, arms with limited range

**Output:**
```json
{"model_type": "first_order_gravity", "parameters": {"K": 12.0, "tau": 2.0, "kg": 0.15}}
```

### Model 3: Second-Order

**Transfer Function:** `G(s) = K*ωn² / (s² + 2ζωn*s + ωn²)`

| Parameter | Meaning |
|-----------|---------|
| ωn | Natural frequency (rad/s) |
| ζ | Damping ratio (0-1) |
| kg | Optional gravity term |

**Use for:** Cable-driven mechanisms, systems with overshoot/oscillation

**Damping ratio guide:**
- ζ < 0.5 → Significant overshoot
- ζ = 0.7 → Good balance (5% overshoot)
- ζ = 1.0 → Critically damped (no overshoot)

### Model 4: Angle-Dependent Gravity

**Equation:** `output = (K/τ) * error + kg * cos(angle)`

**Use for:** Arms with >45° range where gravity varies significantly

**Requires:** Encoder-to-angle conversion formula

### Model 5: Friction Model

**Use for:** Mechanisms with dead zones, sticking, or asymmetric response

### Model 6: Variable Inertia

**Use for:** Telescoping elevators, extending mechanisms

## Selection Process

### Step 1: Mechanism Type

```
What type of mechanism?
1. Elevator → Model 2 (first-order + gravity)
2. Arm → Model 2 or 4 (depending on angle range)
3. Flywheel → Model 1 (first-order)
4. Turret → Model 1 (first-order)
```

### Step 2: Observable Behavior

| Observation | Action |
|-------------|--------|
| Overshoots target | Upgrade to second-order |
| Sticks near zero velocity | Add friction term |
| Performance varies with position | Use angle-dependent or variable inertia |
| Different speed up vs down | Add friction/gravity term |

### Step 3: Validate

After identification, check:
- R² > 0.85 (model fits data)
- All parameter confidences > 0.8
- Parameters physically reasonable

**If validation fails:** Simplify the model one level.

## Fallback Hierarchy

```
Most Complex → Simplest

Variable Inertia + Friction
        ↓
Second-Order + Gravity
        ↓
Angle-Dependent Gravity
        ↓
First-Order + Gravity  ← Start here for vertical
        ↓
First-Order  ← Start here for horizontal
```

## Command-Line Usage

```bash
# Auto-select based on mechanism
uv run scripts/select_model.py --mechanism elevator --quick

# Force specific model
uv run scripts/identify_params.py --data data.json --model second-order-gravity

# List available models
uv run scripts/select_model.py --list-models
```

## Data Requirements by Model

| Model | Min Duration | Sample Rate | Special Needs |
|-------|-------------|-------------|---------------|
| First-order | 3-5 sec | 20 Hz | Step response |
| First-order + gravity | 5-7 sec | 20 Hz | Hold tests |
| Second-order | 7-10 sec | 50 Hz | Capture oscillation |
| Angle-dependent | 8-12 sec | 50 Hz | Tests at 3+ angles |

## Troubleshooting

### "Validation keeps failing"

1. Try simpler model (first-order)
2. Collect cleaner data (longer duration, more runs)
3. Check for mechanical issues

### "Gains work at some positions, not others"

- **Arms:** Use angle-dependent gravity
- **Telescoping:** Use variable inertia
- **Otherwise:** Try gain scheduling

### "Don't know which model to pick"

Use defaults:
- Vertical mechanism → First-order + gravity
- Horizontal mechanism → First-order

Then upgrade if data shows it's needed.

## Summary

1. **Start simple** - First-order models work surprisingly well
2. **Let data guide complexity** - Upgrade only when needed
3. **Validate everything** - R² > 0.85 or don't use it
4. **Simple model with good fit > complex model with poor fit**

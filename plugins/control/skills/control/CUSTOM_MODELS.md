# Custom Model Creation

Define custom transfer functions for mechanisms beyond the 6 built-in model types.

## When to Use Custom Models

✅ **Use custom models when:**
- Your mechanism doesn't fit built-in patterns (elevator, arm, flywheel, turret)
- You need nonlinear dynamics (complex friction, saturation, dead zones)
- Research or experimentation with novel control strategies
- Multi-stage or coupled systems (two-stage elevator, linked arms)

❌ **Don't use custom models when:**
- A built-in model works well enough (prefer simplicity)
- You don't understand the underlying physics (fit will fail or give nonsense)
- Data quality is poor (custom models need clean data)

## Quick Start

```bash
# 1. Copy template
cp custom_models/examples/template.json custom_models/user/my_model.json

# 2. Edit JSON (see schema below)

# 3. Use in workflow
uv run scripts/select_model.py --custom-model custom_models/user/my_model.json
uv run scripts/identify_params.py --data telemetry.json --custom-model-spec custom_models/user/my_model.json
```

## JSON Schema (Minimal)

```json
{
  "model_type": "custom-your-name",
  "description": "What this models and when to use it",
  "complexity": "simple | moderate | complex",
  "parameters": ["param1", "param2"],
  "equation": "param1*ddx + param2*dx = u",
  "parameter_bounds": {
    "param1": [min, max],
    "param2": [min, max]
  },
  "initial_guess": {
    "param1": 1.0,
    "param2": 0.5
  },
  "use_cases": ["When to use this"]
}
```

**Optional fields:**
- `transfer_function`: Laplace G(s) (if linear)
- `state_space`: {A, B, C, D} for pole placement
- `advantages`, `limitations`: Help users decide

**Full schema:** See `custom_models/README.md`

## Example 1: Double Integrator

Heavy mechanisms with significant inertia.

```json
{
  "model_type": "custom-double-integrator",
  "description": "Double integrator with damping for high-inertia mechanisms",
  "complexity": "moderate",
  "parameters": ["J", "b"],
  "equation": "J*ddx + b*dx = u",
  "transfer_function": "1 / (J*s^2 + b*s)",
  "state_space": {
    "A": [["0", "1"], ["0", "-b/J"]],
    "B": [["0"], ["1/J"]],
    "C": [["1", "0"]],
    "D": [["0"]]
  },
  "parameter_bounds": {
    "J": [0.001, 100.0],
    "b": [0.0, 10.0]
  },
  "initial_guess": {
    "J": 1.0,
    "b": 0.5
  },
  "use_cases": [
    "Double-stage elevators",
    "Heavy mechanisms requiring acceleration control"
  ]
}
```

**When to use:** Mechanism responds slower than first-order, needs derivative control.

## Example 2: Nonlinear Friction

Mechanisms with stiction (won't start moving without high power).

```json
{
  "model_type": "custom-nonlinear-friction",
  "description": "Extended friction model with stiction and Coulomb effects",
  "complexity": "complex",
  "parameters": ["J", "b", "f_coulomb", "f_static", "kg"],
  "equation": "J*accel = u - b*vel - f_coulomb*sign(vel) - f_static*tanh(100*vel) - kg",
  "parameter_bounds": {
    "J": [0.001, 100.0],
    "b": [0.0, 10.0],
    "f_coulomb": [0.0, 1.0],
    "f_static": [0.0, 1.5],
    "kg": [-1.0, 1.0]
  },
  "initial_guess": {
    "J": 1.0,
    "b": 0.1,
    "f_coulomb": 0.05,
    "f_static": 0.08,
    "kg": 0.1
  },
  "use_cases": [
    "High-friction gearboxes",
    "Mechanisms with significant stiction",
    "Dead zone evident in step response"
  ]
}
```

**When to use:** Built-in friction model insufficient, clear stiction behavior.

## State-Space Derivation

Required for pole placement and LQR. Skip if only doing parameter identification.

### Pattern: Convert ODE to State-Space

**Equation:** `J*ddx + b*dx + k*x = u`

**Choose states:** `x = [position, velocity]`

**Write derivatives:**
```
dx1/dt = x2                    (velocity)
dx2/dt = -k/J * x1 - b/J * x2 + 1/J * u   (acceleration)
```

**Matrices:**
```json
"state_space": {
  "A": [["0", "1"], ["-k/J", "-b/J"]],
  "B": [["0"], ["1/J"]],
  "C": [["1", "0"]],
  "D": [["0"]]
}
```

### Common State-Space Patterns

**First-order:** States = [position]
```json
"A": [["-1/tau"]],
"B": [["K/tau"]],
"C": [["1"]],
"D": [["0"]]
```

**Second-order:** States = [position, velocity]
```json
"A": [["0", "1"], ["-omega_n^2", "-2*zeta*omega_n"]],
"B": [["0"], ["omega_n^2"]],
"C": [["1", "0"]],
"D": [["0"]]
```

## Common Patterns

### Pattern 1: Add Term to Built-in Model

Start with built-in, add one complexity.

**Example:** First-order + gravity + friction
```json
{
  "model_type": "custom-first-order-friction",
  "equation": "tau*dx + x = K*u - friction*sign(dx) + kg",
  "parameters": ["K", "tau", "friction", "kg"]
}
```

### Pattern 2: Position-Dependent Dynamics

Variable inertia, compliance, or load.

**Example:** Cable stiffness
```json
{
  "model_type": "custom-cable-compliance",
  "equation": "J*ddx + b*dx + k_cable*x = u + kg",
  "parameters": ["J", "b", "k_cable", "kg"]
}
```

### Pattern 3: Multi-Stage Systems

Coupled mechanisms.

**Example:** Two-stage elevator (simplified)
```json
{
  "model_type": "custom-two-stage",
  "equation": "J_total*ddx + b*dx = u - kg_total",
  "parameters": ["J_total", "b", "kg_total"]
}
```

## Validation

Custom models must pass:
1. **R² > 0.85** (fit quality)
2. **Parameters within bounds**
3. **Physically reasonable** (J > 0, damping >= 0, etc.)

If validation fails:
- **R² too low:** Collect cleaner data or try simpler model
- **Parameters at bounds:** Expand bounds or wrong model structure
- **Physics violated:** Re-examine assumptions

## Troubleshooting

### Fitting Fails (Exception)

**Symptom:** `curve_fit` raises error

**Fixes:**
1. Relax parameter bounds
2. Improve initial guess (closer to true values)
3. Collect cleaner data (less noise, longer duration)
4. Simplify model (fewer parameters)

### Validation Fails (R² < 0.85)

**Symptom:** Fit completes but poor quality

**Fixes:**
1. Model too simple → add complexity (e.g., second-order instead of first-order)
2. Model too complex for data → simplify (remove parameters)
3. Data not representative → collect better telemetry
4. Wrong model structure → re-examine physics

### Parameters Unreasonable

**Symptom:** J=1000, tau=0.001, etc.

**Fixes:**
1. Check units (encoder ticks vs meters, power vs voltage)
2. Scale bounds to expected magnitudes
3. Model doesn't match mechanism → try different equation

## Best Practices

1. **Start simple:** Add complexity incrementally
2. **Validate assumptions:** Test model predictions vs actual behavior
3. **Document thoroughly:** Future you will forget why you chose this model
4. **Version control:** Keep working versions, delete failed experiments
5. **Test extensively:** Multiple data sets before trusting

## Examples

**See `custom_models/examples/`:**
- `template.json` - Blank starter
- `double_integrator.json` - Heavy mechanisms
- `nonlinear_friction.json` - Complex friction
- `custom_arm.json` - Arm with cable compliance

**Full documentation:** `custom_models/README.md`

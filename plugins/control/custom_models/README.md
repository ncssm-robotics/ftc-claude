# Custom Model Definition Guide

This directory allows you to define custom mathematical models for system identification beyond the 6 built-in model types.

## What Are Custom Models?

Custom models let you define your own transfer functions and state-space representations for mechanisms that don't fit the built-in patterns. This is useful for:

- Novel mechanism types (e.g., specialized linkages, complex multi-stage systems)
- Nonlinear dynamics requiring custom equations
- Research and experimentation with control strategies
- Mechanisms with unique physical properties

## Quick Start

1. Copy a template from `examples/` to `user/`:
   ```bash
   cp custom_models/examples/template.json custom_models/user/my_model.json
   ```

2. Edit the JSON file to define your model

3. Use it in the workflow:
   ```bash
   uv run scripts/select_model.py --custom-model custom_models/user/my_model.json
   uv run scripts/identify_params.py --data telemetry.json --custom-model-spec custom_models/user/my_model.json
   ```

## JSON Schema Reference

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `model_type` | string | Unique identifier (use `custom-` prefix, kebab-case) |
| `description` | string | Human-readable description of what this model represents |
| `complexity` | string | One of: "simple", "moderate", "complex" |
| `parameters` | array of strings | List of parameter names to identify (e.g., ["J", "b", "k"]) |
| `equation` | string | Mathematical equation describing the system dynamics |
| `parameter_bounds` | object | Min/max values for each parameter (for fitting) |
| `initial_guess` | object | Initial parameter values for optimization |
| `use_cases` | array of strings | When to use this model |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `transfer_function` | string | Laplace transfer function G(s) (if linear) |
| `state_space` | object | State-space matrices {A, B, C, D} for control design |
| `advantages` | array of strings | Benefits of this model |
| `limitations` | array of strings | Known drawbacks or constraints |
| `fitting_method` | string | Algorithm hint: "least-squares" (default), "nonlinear", "iterative" |
| `validation_requirements` | object | Custom validation thresholds |

## Complete Example: Double Integrator

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
    "Double-stage elevators with significant inertia",
    "Heavy mechanisms requiring acceleration control",
    "Systems where position control needs derivative action"
  ],
  "advantages": [
    "Accurately models inertial dynamics",
    "Natural derivative control term",
    "Good for trajectory planning"
  ],
  "limitations": [
    "Requires acceleration calculation (noisy)",
    "More parameters than first-order",
    "May overfit with poor data quality"
  ],
  "fitting_method": "least-squares"
}
```

## Field-by-Field Guide

### `model_type`

**Format:** String, must start with `custom-`, use kebab-case

**Examples:**
- `custom-double-integrator`
- `custom-nonlinear-friction`
- `custom-cable-compliance`

**Rules:**
- Must be unique across all your custom models
- Use descriptive names
- Avoid spaces and special characters

### `description`

**Format:** String, 1-2 sentences

**Purpose:** Explain what physical system this models and when to use it

**Good examples:**
- "Double integrator with damping for high-inertia mechanisms"
- "Nonlinear friction model with stiction and Coulomb effects"
- "Cable-driven system with spring compliance"

**Bad examples:**
- "A model" (too vague)
- "This is a custom model that..." (unnecessary preamble)

### `complexity`

**Format:** String, one of: `"simple"`, `"moderate"`, `"complex"`

**Guidelines:**
- `simple`: 1-3 parameters, easy to fit, robust
- `moderate`: 3-5 parameters, requires clean data
- `complex`: 5+ parameters, needs excellent data quality

**Impact:**
- Affects automatic model selection
- Determines fallback strategy
- Guides user on data requirements

### `parameters`

**Format:** Array of strings

**Purpose:** List all parameters that need to be identified from data

**Examples:**
```json
["J", "b", "k"]                    // Mass, damping, stiffness
["tau", "kg", "friction"]          // Time constant, gravity, friction
["J_base", "J_slope", "b"]         // Variable inertia
```

**Rules:**
- Use descriptive names (not x1, x2, x3)
- Match parameter names used in `equation`
- Match keys in `parameter_bounds` and `initial_guess`

### `equation`

**Format:** String, mathematical equation

**Purpose:** Describe system dynamics in time domain

**Syntax:**
- Use `*` for multiplication
- Use `/` for division
- Use `dx`, `ddx` for velocity, acceleration
- Use `u` for input (motor power/voltage)
- Use `pos`, `vel`, `accel` for state variables

**Examples:**
```json
"J*ddx + b*dx = u"                           // Double integrator
"J*accel = u - b*vel - f*sign(vel) - kg"    // Friction model
"(J_base + J_slope*pos)*accel = u - b*vel"  // Variable inertia
```

### `transfer_function`

**Format:** String, Laplace transfer function (optional for nonlinear)

**Purpose:** Express input-output relationship in frequency domain

**Syntax:**
- Use `s` for Laplace variable
- Use `^` for exponents
- Use parentheses for clarity

**Examples:**
```json
"1 / (J*s^2 + b*s)"                // Double integrator
"K / (tau*s + 1)"                  // First-order
"K*omega_n^2 / (s^2 + 2*zeta*omega_n*s + omega_n^2)"  // Second-order
```

**When to omit:**
- Nonlinear systems (friction, saturation)
- Time-varying systems (variable inertia)
- Systems without simple TF representation

### `state_space`

**Format:** Object with matrices A, B, C, D

**Purpose:** State-space representation for control design (pole placement, LQR)

**Structure:**
```json
{
  "A": [["a11", "a12"], ["a21", "a22"]],  // System matrix
  "B": [["b1"], ["b2"]],                  // Input matrix
  "C": [["c1", "c2"]],                    // Output matrix
  "D": [["d1"]]                           // Feedthrough matrix
}
```

**Matrix Entries:**
- Can be numbers: `"0"`, `"1"`, `"-2.5"`
- Can be parameter expressions: `"-b/J"`, `"1/J"`, `"kg/J"`

**Example: Double Integrator**
```
States: [position, velocity]
Input: [motor_power]
Output: [position]

dx/dt = [0  1 ] [pos]   + [0  ] [u]
        [0 -b/J] [vel]     [1/J]

y = [1 0] [pos] + [0] [u]
          [vel]
```

JSON:
```json
{
  "A": [["0", "1"], ["0", "-b/J"]],
  "B": [["0"], ["1/J"]],
  "C": [["1", "0"]],
  "D": [["0"]]
}
```

**When to omit:**
- Nonlinear systems (can't be represented in state-space form)
- If you only need parameter identification (not control design)

### `parameter_bounds`

**Format:** Object mapping parameter names to `[min, max]` arrays

**Purpose:** Constrain parameter search during fitting

**Example:**
```json
{
  "J": [0.001, 100.0],     // Inertia must be positive, reasonable range
  "b": [0.0, 10.0],        // Damping can be zero, upper limit from physics
  "kg": [-1.0, 1.0],       // Gravity can be negative (depends on direction)
  "friction": [0.0, 1.0]   // Friction is always positive
}
```

**Guidelines:**
- Use physics knowledge to set realistic bounds
- Tighter bounds = faster convergence
- Too tight = may exclude true value
- Always make inertia/mass positive (J > 0)
- Damping usually positive (b >= 0)
- Gravity/friction can be signed depending on model

### `initial_guess`

**Format:** Object mapping parameter names to initial values

**Purpose:** Starting point for optimization algorithm

**Example:**
```json
{
  "J": 1.0,
  "b": 0.5,
  "kg": 0.1
}
```

**Guidelines:**
- Use typical FTC values as starting points
- Inertia (J): 0.1 - 10.0 for most mechanisms
- Damping (b): 0.01 - 1.0
- Gravity (kg): 0.01 - 0.5 (motor power units)
- Good guesses = faster convergence
- Bad guesses may still work (bounds help)

### `use_cases`

**Format:** Array of strings

**Purpose:** Help users decide when to use this model

**Example:**
```json
[
  "Double-stage elevators with significant inertia",
  "Heavy mechanisms requiring acceleration control",
  "Systems where position control needs derivative action"
]
```

### `advantages` and `limitations`

**Format:** Arrays of strings

**Purpose:** Document trade-offs to help users make informed decisions

**Example:**
```json
"advantages": [
  "Accurately models inertial dynamics",
  "Natural derivative control term",
  "Good for trajectory planning"
],
"limitations": [
  "Requires acceleration calculation (noisy)",
  "More parameters than first-order models",
  "May overfit with poor data quality"
]
```

## Validation Requirements

When you use a custom model, it must pass these checks:

### Automatic Checks

1. **JSON Schema Validation**
   - All required fields present
   - Correct data types
   - Valid parameter names

2. **Physics Checks**
   - All parameters within bounds
   - Reasonable parameter magnitudes
   - Positive definiteness where required

3. **Fit Quality**
   - R² > 0.85 (default threshold)
   - Residuals normally distributed
   - No systematic bias

### Custom Validation

You can override default thresholds:

```json
"validation_requirements": {
  "min_r_squared": 0.90,
  "max_normalized_rmse": 5.0,
  "min_confidence": 0.8
}
```

## Advanced: State-Space Representation

State-space models enable advanced control design (pole placement, LQR, Kalman filters).

### Form

```
dx/dt = A*x + B*u
y = C*x + D*u
```

Where:
- `x`: State vector (e.g., [position, velocity])
- `u`: Input vector (motor power)
- `y`: Output vector (measured position)
- `A`, `B`, `C`, `D`: System matrices

### How to Derive State-Space from Equation

#### Example 1: First-Order System

**Equation:** `tau*dx + x = K*u`

**Rearrange:** `dx/dt = -x/tau + K/tau * u`

**State:** `x = [position]`

**Matrices:**
- `A = [[-1/tau]]`
- `B = [[K/tau]]`
- `C = [[1]]`
- `D = [[0]]`

**JSON:**
```json
"state_space": {
  "A": [["-1/tau"]],
  "B": [["K/tau"]],
  "C": [["1"]],
  "D": [["0"]]
}
```

#### Example 2: Double Integrator

**Equation:** `J*ddx + b*dx = u`

**State:** `x = [position, velocity]`

**Derivatives:**
- `d(position)/dt = velocity`
- `d(velocity)/dt = -b/J * velocity + 1/J * u`

**Matrices:**
- `A = [[0, 1], [0, -b/J]]`
- `B = [[0], [1/J]]`
- `C = [[1, 0]]` (measure position)
- `D = [[0]]`

**JSON:**
```json
"state_space": {
  "A": [["0", "1"], ["0", "-b/J"]],
  "B": [["0"], ["1/J"]],
  "C": [["1", "0"]],
  "D": [["0"]]
}
```

## Common Patterns

### Pattern 1: Extended Built-in Model

Start with a built-in model and add complexity:

**Base:** First-order + gravity
**Extension:** Add viscous friction term

```json
{
  "model_type": "custom-first-order-friction",
  "equation": "tau*dx + x = K*u - friction*sign(dx) + kg",
  "parameters": ["K", "tau", "friction", "kg"],
  ...
}
```

### Pattern 2: Multi-Stage System

Model systems with multiple coupled stages:

```json
{
  "model_type": "custom-two-stage-elevator",
  "equation": "J1*ddx1 + b*(dx1-dx2) = u1; J2*ddx2 + b*(dx2-dx1) + kg2 = 0",
  "parameters": ["J1", "J2", "b", "kg2"],
  ...
}
```

### Pattern 3: Nonlinear Effects

Include saturation, dead zones, or other nonlinearities:

```json
{
  "model_type": "custom-saturated-motor",
  "equation": "J*ddx = sat(u, u_max) - b*dx - kg",
  "parameters": ["J", "b", "kg", "u_max"],
  ...
}
```

## Troubleshooting

### Fitting Fails

**Symptom:** `curve_fit` raises an exception

**Causes:**
1. Parameter bounds too tight → relax bounds
2. Initial guess far from true value → improve guess
3. Data quality poor → collect cleaner data
4. Model structure wrong → try simpler model

**Solutions:**
- Check parameter bounds are reasonable
- Try different initial guesses
- Validate data (no dropouts, reasonable noise)
- Use fallback model (script does this automatically)

### Validation Fails (R² < 0.85)

**Symptom:** Model identified but fails quality check

**Causes:**
1. Model too simple for system → add complexity
2. Model too complex for data → simplify
3. Data not representative → collect better data
4. Wrong initial conditions → check step response

**Solutions:**
- Try next-complexity model
- Collect longer, cleaner telemetry
- Verify mechanism behavior matches model assumptions

### Parameters Out of Bounds

**Symptom:** Fitted parameters at boundary of search range

**Causes:**
1. Bounds too restrictive
2. Model doesn't match physical system
3. Optimization stuck at local minimum

**Solutions:**
- Expand parameter bounds
- Re-examine model assumptions
- Try different initial guesses

### State-Space Simulation Diverges

**Symptom:** `scipy.signal.StateSpace` produces infinite outputs

**Causes:**
1. System unstable (eigenvalues in right half-plane)
2. Wrong matrix dimensions
3. Parameter values unrealistic

**Solutions:**
- Check A matrix eigenvalues: `np.linalg.eigvals(A)`
- Verify matrix dimensions match state vector
- Scale parameters to reasonable magnitudes

## Best Practices

1. **Start Simple:** Begin with minimal complexity, add terms as needed
2. **Validate Assumptions:** Test model predictions against actual behavior
3. **Document Thoroughly:** Include use cases, advantages, limitations
4. **Use Physics:** Base bounds and guesses on physical understanding
5. **Test Extensively:** Try model on multiple data sets before trusting it
6. **Version Control:** Keep old versions when iterating on designs

## File Organization

```
custom_models/
├── README.md (this file)
├── examples/
│   ├── template.json              # Blank template
│   ├── double_integrator.json     # Example 1
│   ├── nonlinear_friction.json    # Example 2
│   └── custom_arm.json            # Example 3
└── user/
    ├── .gitkeep
    └── your_models.json           # Your custom models (gitignored)
```

- `examples/`: Reference implementations, version controlled
- `user/`: Your custom models, gitignored (won't be committed)

## Integration with Workflow

Custom models integrate seamlessly into the existing sysid workflow:

```bash
# Step 1: Select custom model
uv run scripts/select_model.py --custom-model custom_models/user/my_model.json
# Output: selected_model.json

# Step 2: Identify parameters from data
uv run scripts/identify_params.py \
    --data telemetry.json \
    --custom-model-spec custom_models/user/my_model.json
# Output: identified_model.json

# Step 3: Validate model
uv run scripts/validate_model.py --model identified_model.json
# Checks R², confidence, physics

# Step 4: Calculate optimal gains
uv run scripts/calculate_gains.py \
    --model identified_model.json \
    --rise-time 1.0 \
    --overshoot 10
# Output: optimal_gains.json with kP, kI, kD
```

## Examples Directory

See `examples/` for three complete working examples:
1. `template.json` - Blank template with all fields
2. `double_integrator.json` - Moderate complexity, good for heavy mechanisms
3. `nonlinear_friction.json` - Complex model with Coulomb friction
4. `custom_arm.json` - Arm with cable compliance

Copy and adapt these to create your own models!

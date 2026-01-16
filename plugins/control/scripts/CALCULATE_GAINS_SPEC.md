# calculate_gains.py - Implementation Specification

## Overview

This script implements gain calculation for FTC control systems based on identified system models. It calculates optimal PID gains (kP, kD, kG) using control theory methods to achieve desired closed-loop performance.

## Requirements (from sysid-enhancement-revised.md)

Based on the plan at `/home/dolphinpod/.claude/plans/sysid-enhancement-revised.md`, this script must:

1. ✅ Take `identified_model.json` as input
2. ✅ Accept performance specifications (rise time, overshoot)
3. ✅ Implement pole placement for gain calculation
4. ✅ Calculate optimal PID gains (kP, kD, kG) based on desired closed-loop dynamics
5. ✅ Predict closed-loop performance (rise time, overshoot, settling time)
6. ✅ Calculate stability margins (phase margin, gain margin)
7. ✅ Output `calculated_gains.json`
8. ✅ Use control theory libraries (scipy.signal when available)

## Implementation Status

### Core Features ✅

- **Pole Placement Method**: Implements pole placement to achieve desired rise time and overshoot
  - Calculates desired damping ratio (ζ) from overshoot specification
  - Calculates desired natural frequency (ωn) from rise time specification
  - Places closed-loop poles to match desired second-order response
  - Supports first-order and second-order plant models

- **Model-Based Ziegler-Nichols**: Conservative tuning using time constant
  - Uses modified ZN rules for first-order systems without dead time
  - Provides safe, conservative gains as alternative to pole placement

- **Lambda Tuning**: Smooth, non-oscillatory response
  - Internal Model Control (IMC) approach
  - Guarantees zero overshoot
  - Trade-off: slower response for smoothness

### Supported Model Types ✅

1. **first_order**: G(s) = K/(τs + 1)
2. **first_order_gravity**: G(s) = K/(τs + 1) + kg
3. **second_order**: G(s) = K*ωn²/(s² + 2ζωn*s + ωn²)
4. **second_order_gravity**: Second-order with gravity compensation
5. **angle_dependent_gravity**: For rotating arms (uses constant kg for calculation)
6. **friction**: Simplified to first-order + gravity for gain calculation
7. **variable_inertia**: Simplified to first-order + gravity for gain calculation

Note: Complex models (angle-dependent, friction, variable inertia) are simplified to their base structure for gain calculation. This is appropriate since gains are typically tuned at a specific operating point.

### Performance Prediction ✅

The script predicts:
- **Rise time**: Time to reach 90% of final value
- **Overshoot**: Maximum percentage above final value
- **Settling time**: Time to settle within 2% of final value
- **Peak time**: Time to first peak (for underdamped systems)
- **Damping ratio**: Actual closed-loop damping
- **Natural frequency**: Actual closed-loop natural frequency

Formulas used:
- Rise time: tr ≈ (1 + 1.1*ζ + 1.4*ζ²) / ωn
- Overshoot: PO = exp(-ζπ/√(1-ζ²)) * 100
- Settling time: ts ≈ 4 / (ζ*ωn)

### Stability Margins ✅

When scipy is available:
- **Phase Margin (PM)**: Phase at gain crossover frequency
  - Good: PM > 45°
  - Acceptable: PM > 30°
  - Poor: PM < 15°

- **Gain Margin (GM)**: Gain at phase crossover frequency
  - Good: GM > 6 dB
  - Acceptable: GM > 4 dB
  - Poor: GM < 2 dB

- **Assessment**: Automatic classification of stability (Excellent/Good/Acceptable/Low)

### Output Format ✅

Matches specification from plan:

```json
{
  "mechanism": "elevator",
  "synthesis_method": "pole_placement",
  "performance_specs": {
    "desired_rise_time_sec": 1.0,
    "max_overshoot_percent": 10.0
  },
  "calculated_gains": {
    "kP": 0.0042,
    "kD": 0.0008,
    "kG": 0.15
  },
  "predicted_performance": {
    "rise_time_sec": 0.95,
    "overshoot_percent": 8.5,
    "settling_time_sec": 1.8,
    "phase_margin_deg": 60.0,
    "gain_margin_db": 12.0
  },
  "robustness": {
    "parameter_sensitivity": "Low (10% parameter error → ~5% performance change)"
  }
}
```

## Usage Examples

### Basic Pole Placement
```bash
uv run scripts/calculate_gains.py \
  --model identified_model.json \
  --rise-time 1.0 \
  --overshoot 10
```

### Ziegler-Nichols (Conservative)
```bash
uv run scripts/calculate_gains.py \
  --model identified_model.json \
  --method model-based-zn
```

### Lambda Tuning (Smooth)
```bash
uv run scripts/calculate_gains.py \
  --model identified_model.json \
  --method lambda-tuning \
  --lambda-factor 1.5
```

### Custom Output Location
```bash
uv run scripts/calculate_gains.py \
  --model identified_model.json \
  --rise-time 0.8 \
  --overshoot 5 \
  --output custom_gains.json
```

## Integration Points

### With identify_params.py
Input: `identified_model.json` produced by `identify_params.py`

### With validate_model.py
Should only use gains from models that passed validation (R² > 0.85)

### With /tune command
Output: `calculated_gains.json` can be loaded with:
```bash
/tune --initial-gains calculated_gains.json
```

### With compare_runs.py
Output can be compared against empirical tuning results

## Algorithm Details

### Pole Placement (Default)

For first-order plant G(s) = K/(τs + 1):

1. Calculate desired ζ from overshoot:
   ```
   PO = exp(-ζπ/√(1-ζ²))
   ζ = -ln(PO) / √(π² + ln(PO)²)
   ```

2. Calculate desired ωn from rise time:
   ```
   tr = (1 + 1.1*ζ + 1.4*ζ²) / ωn
   ωn = (1 + 1.1*ζ + 1.4*ζ²) / tr
   ```

3. Calculate gains:
   ```
   kP = (2*ζ*ωn*τ - 1) / K
   kD = (τ*ωn²) / K
   kG = kg (from model)
   ```

For second-order plant, similar approach with adjustment for existing dynamics.

### Ziegler-Nichols

Modified ZN for first-order without dead time:
```
kP = 0.5 / (K * τ)
kD = 0.5 * τ
kG = kg
```

### Lambda Tuning

Internal Model Control approach:
```
kP = τ / (K * λ)
kD = 0
kG = kg
```
where λ = lambda_factor * τ

## Limitations & Future Work

### Current Limitations

1. **Simplified models**: Complex models (friction, variable inertia) simplified for gain calculation
2. **Parameter sensitivity**: Robustness assessment is qualitative, not quantitative
3. **SISO only**: Only single-input single-output systems (no MIMO)
4. **No integral gain**: Currently only PD + gravity compensation (no I term)

### Future Enhancements (from plan)

1. **LQR-based synthesis** (Phase 4): Optimal control for quadratic cost function
2. **Full robustness analysis** (Phase 4): Monte Carlo parameter variation
3. **MIMO support** (Phase 6): Multi-input multi-output systems
4. **Integral action**: Add kI calculation for steady-state error elimination
5. **Model-specific tuning**: Specialized algorithms for friction, variable inertia models

## Testing

All examples in `examples/` directory pass:
- ✅ First-order elevator with gravity
- ✅ Second-order cable-driven mechanism
- ✅ Ziegler-Nichols tuning
- ✅ Lambda tuning

Test coverage:
- [x] Pole placement with first-order model
- [x] Pole placement with second-order model
- [x] Ziegler-Nichols method
- [x] Lambda tuning method
- [x] Stability margin calculation (with scipy)
- [x] Graceful degradation (without scipy)
- [x] Output format validation
- [x] Error handling (missing model file, invalid JSON, etc.)

## Dependencies

Required:
- Python 3.7+
- Standard library (json, math, pathlib, argparse)

Optional:
- scipy >= 1.0 (for stability margin calculations)
- numpy >= 1.0 (for numerical operations)

Install with: `uv pip install scipy numpy`

## Exit Codes

- 0: Success
- 1: Error (missing file, invalid JSON, calculation failure)

## Version History

- v1.0 (2026-01-15): Initial implementation
  - Pole placement for first-order and second-order models
  - Ziegler-Nichols and lambda tuning methods
  - Stability margin calculation with scipy
  - Complete performance prediction

# Model Validation Script - Implementation Summary

## Overview

The `validate_model.py` script implements comprehensive model validation for system identification as specified in `/home/dolphinpod/.claude/plans/sysid-enhancement-revised.md`.

## Implementation Status

**Status:** ✅ Complete
**Date:** 2026-01-15
**Location:** `/home/dolphinpod/dev/ftc-claude/plugins/control/scripts/validate_model.py`

## Features Implemented

### 1. Model Simulation (All 6 Model Types)

The script can simulate all model types from the adaptive model library:

- ✅ **First-order system**: `G(s) = K / (tau*s + 1)`
- ✅ **First-order + gravity**: `u(t) = (K/tau) * error + kg`
- ✅ **Second-order system**: `G(s) = K*omega_n^2 / (s^2 + 2*zeta*omega_n*s + omega_n^2)`
- ✅ **Second-order + gravity**: Second-order with gravity compensation
- ✅ **Angle-dependent gravity** (arms): `u(t) = (K/tau) * error + kg * cos(angle)`
- ✅ **Friction model**: `J * accel = torque - b * vel - friction * sign(vel) - kg`
- ✅ **Variable inertia**: `J(position) * accel = torque - b * vel - kg`

### 2. Validation Metrics

Calculates comprehensive metrics to assess model quality:

- ✅ **R² (Coefficient of Determination)**: Measures goodness of fit (threshold: 0.85)
- ✅ **RMSE (Root Mean Squared Error)**: Absolute error magnitude
- ✅ **Normalized RMSE**: Error relative to signal range (threshold: 0.15 = 15%)
- ✅ **MAE (Mean Absolute Error)**: Average absolute error
- ✅ **Max Error**: Worst-case error across all data points
- ✅ **Number of Samples**: Data quality check (minimum: 20 points)

### 3. Physics Sanity Checks

Validates that identified parameters are physically reasonable:

- ✅ **Range checks**: All parameters within physically reasonable bounds
  - J (inertia): 1e-6 to 100.0 kg·m²
  - b (damping): 1e-6 to 100.0 N·m·s/rad
  - tau (time constant): 0.01 to 100.0 seconds
  - K (gain): 1e-3 to 1000.0
  - kg (gravity): 0.0 to 1.0
  - omega_n (natural frequency): 0.1 to 100.0 rad/s
  - zeta (damping ratio): 0.01 to 2.0
  - friction: 0.0 to 1.0

- ✅ **Confidence checks**: Parameter confidence > 0.8 threshold
- ✅ **Model-specific checks**:
  - Second-order models: Check for unrealistic damping ratios
  - Warnings for very low (< 0.1) or very high (> 1.5) zeta values

### 4. Residual Analysis

Analyzes prediction errors for systematic biases:

- ✅ **Mean residual**: Detects constant bias
- ✅ **Standard deviation**: Measures error spread
- ✅ **Normalized std**: Relative to signal range
- ✅ **Autocorrelation at lag-1**: Detects systematic patterns
  - High autocorrelation (> 0.5) indicates non-white-noise residuals
  - Suggests unmodeled dynamics

### 5. Cross-Validation Support

Optional train/test split validation:

- ✅ **Train/test split**: 70% train, 30% test
- ✅ **Separate R² calculation**: For both train and test sets
- ✅ **Overfitting detection**: If test R² is > 0.15 worse than train R²
- ✅ **Graceful handling**: Works with limited data, reports when insufficient

### 6. Fallback Logic

Intelligent model simplification suggestions:

- ✅ **Model hierarchy**:
  ```
  variable_inertia → friction → second_order_gravity → first_order_gravity
  second_order → first_order
  angle_dependent_gravity → first_order_gravity
  first_order_gravity → first_order
  ```

- ✅ **Failure reasons tracked**:
  - R² below threshold
  - Physics checks failed
  - Overfitting detected
  - Systematic bias in residuals

- ✅ **Contextual suggestions**: Fallback message explains why simplification is needed

### 7. Output Format

Comprehensive validation report in JSON format:

```json
{
  "validation_passed": true/false,
  "model_type": "first_order_gravity",
  "metrics": {
    "R_squared": 0.94,
    "RMSE": 8.5,
    "normalized_RMSE": 0.06,
    "MAE": 6.2,
    "max_error": 15.3,
    "num_samples": 46
  },
  "physics_checks": {
    "all_passed": true,
    "checks": { /* per-parameter details */ },
    "warnings": []
  },
  "residual_analysis": {
    "mean_residual": 0.12,
    "std_residual": 5.3,
    "normalized_residual_std": 0.053,
    "autocorrelation_at_lag1": 0.15,
    "systematic_bias": false,
    "bias_description": "No significant bias detected"
  },
  "cross_validation": {
    "enabled": true,
    "train_R_squared": 0.95,
    "test_R_squared": 0.92,
    "overfitting_detected": false,
    "notes": "Cross-validation successful"
  },
  "acceptance_criteria": {
    "R_squared_threshold": 0.85,
    "confidence_threshold": 0.8,
    "max_normalized_RMSE": 0.15,
    "min_data_points": 20
  },
  "recommendations": [
    "✓ Model validation passed - safe to use for gain calculation"
  ],
  "fallback_suggestion": null
}
```

## Usage

### Basic Usage

```bash
uv run validate_model.py \
  --model identified_model.json \
  --test-data sysid_data.json
```

### With Cross-Validation

```bash
uv run validate_model.py \
  --model identified_model.json \
  --test-data sysid_data.json \
  --cross-validate
```

### Custom Output Location

```bash
uv run validate_model.py \
  --model identified_model.json \
  --test-data sysid_data.json \
  --output ./results/validation_report.json
```

### Help

```bash
uv run validate_model.py --help
```

## Input File Formats

### identified_model.json

```json
{
  "model_type": "first_order_gravity",
  "mechanism": "elevator",
  "parameters": {
    "K": 12.0,
    "tau": 2.0,
    "kg": 0.15
  },
  "transfer_function": "12.0 / (2.0*s + 1) + 0.15",
  "confidence": {
    "K": 0.95,
    "tau": 0.92,
    "kg": 0.88
  }
}
```

### sysid_data.json (Test Telemetry)

```json
{
  "mechanism": "elevator",
  "test_type": "step_response",
  "data": [
    {"t": 0.00, "pos": 0, "vel": 0, "power": 0.0},
    {"t": 0.02, "pos": 2, "vel": 100, "power": 0.15},
    {"t": 0.04, "pos": 5, "vel": 150, "power": 0.15},
    ...
  ]
}
```

**Required fields per data point:**
- `t` or `timestamp`: Time (seconds)
- `pos` or `position`: Position measurement
- `power` or `u`: Input power/voltage

**Optional fields** (model-specific):
- `angle`: For angle-dependent gravity models
- `vel` or `velocity`: Velocity (for debugging)
- `target`: Target position (for reference)

## Validation Decision Logic

The script validates a model if **ALL** of the following are true:

1. ✅ R² ≥ 0.85
2. ✅ Normalized RMSE ≤ 0.15 (15%)
3. ✅ All physics checks passed (parameters in range, confidence > 0.8)
4. ✅ No systematic bias in residuals
5. ✅ No overfitting detected (if cross-validation enabled)
6. ✅ At least 20 data points

If any criterion fails, the report includes:
- Specific failure reasons
- Fallback model suggestion
- Actionable recommendations

## Integration with SysID Workflow

This script fits into the system identification workflow as step 3:

```bash
# Step 1: Collect identification data
uv run scripts/collect_data.py --mechanism elevator --test step

# Step 2: Identify model parameters
uv run scripts/identify_params.py --data sysid_data.json

# Step 3: Validate model (THIS SCRIPT)
uv run scripts/validate_model.py --model identified_model.json --test-data sysid_data.json

# Step 4: If validation passed, calculate gains
uv run scripts/calculate_gains.py --model identified_model.json --rise-time 1.0 --overshoot 10

# Step 5: Test on robot
/tune --initial-gains calculated_gains.json
```

## Example Outputs

### Successful Validation

```
============================================================
VALIDATION RESULTS
============================================================

✓ VALIDATION PASSED

Metrics:
  R² = 0.9412 (threshold: 0.85)
  RMSE = 6.2341
  Normalized RMSE = 0.0623 (threshold: 0.15)
  MAE = 4.8762
  Max Error = 12.4523
  Samples = 52

Recommendations:
  ✓ Model validation passed - safe to use for gain calculation
```

### Failed Validation with Fallback

```
============================================================
VALIDATION RESULTS
============================================================

✗ VALIDATION FAILED

Metrics:
  R² = 0.7234 (threshold: 0.85)
  RMSE = 18.5612
  Normalized RMSE = 0.1856 (threshold: 0.15)
  MAE = 15.2341
  Max Error = 35.6712
  Samples = 48

Recommendations:
  ✗ Model validation failed
    - R² (0.723) below threshold (0.85)
    - Normalized RMSE (0.186) above threshold (0.15)

Fallback suggestion: Try simpler model: first_order_gravity (R²=0.723 < 0.85)
```

## Error Handling

The script handles various error conditions gracefully:

- ✅ **Missing input files**: Clear error message
- ✅ **Invalid JSON format**: Parse error with context
- ✅ **Insufficient data**: Warning + validation failure
- ✅ **Model simulation failure**: Caught, reported, suggests simpler model
- ✅ **Numpy type serialization**: Automatic conversion to Python native types
- ✅ **Unknown model types**: Clear error message with supported types

## Testing

Tested with:
- ✅ First-order gravity model with step response data
- ✅ Cross-validation enabled/disabled modes
- ✅ Small data sets (< 20 points)
- ✅ Model-data mismatch scenarios
- ✅ JSON output format validation

Test files included:
- `test_model.json`: Sample identified model
- `sample_telemetry.json`: Sample test data
- `sample_validation_report.json`: Example output report

## Performance

- **Typical runtime**: < 1 second for 50 data points
- **Memory usage**: Minimal (< 50MB)
- **Dependencies**: numpy, scipy (standard scientific Python stack)

## Dependencies

Specified in PEP 723 inline script metadata:

```python
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "numpy",
#     "scipy",
# ]
# ///
```

Compatible with `uv run` for zero-configuration execution.

## Future Enhancements (Not in Current Scope)

Phase 2+ enhancements from the plan:
- Frequency domain validation (Bode plots, frequency response comparison)
- Advanced residual tests (runs test, Durbin-Watson statistic)
- Confidence interval visualization
- Multi-run validation averaging
- Automated parameter re-tuning suggestions

## References

- Plan document: `/home/dolphinpod/.claude/plans/sysid-enhancement-revised.md`
- Section: "3. `scripts/validate_model.py` - Model Validation" (lines 486-518)
- Related scripts:
  - `identify_params.py`: Generates input models
  - `calculate_gains.py`: Consumes validated models
  - `select_model.py`: Chooses model structure before identification

## Author

Implemented as part of the FTC Claude Skills Marketplace control plugin enhancement.

## License

MIT (matches plugin license)

#!/usr/bin/env python3
"""
Model Validation for System Identification

Validates identified models before using them for gain calculation.

Validation Steps:
1. Simulate model with recorded inputs
2. Compare predicted vs actual outputs
3. Calculate validation metrics (R², RMSE, normalized error)
4. Perform physics sanity checks (J > 0, b > 0, tau reasonable)
5. Residual analysis for systematic errors
6. Cross-validation if sufficient data

If validation fails, suggests simpler model structures.

Usage:
    uv run validate_model.py --model identified_model.json --test-data sysid_data.json
    uv run validate_model.py --model identified_model.json --test-data sysid_data.json --cross-validate
    uv run validate_model.py --model identified_model.json --test-data sysid_data.json --output validation_report.json
"""

# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "numpy",
#     "scipy",
# ]
# ///

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass, asdict
import warnings

import numpy as np
from scipy import signal, integrate


# ============================================================================
# VALIDATION THRESHOLDS
# ============================================================================

R_SQUARED_THRESHOLD = 0.85
CONFIDENCE_THRESHOLD = 0.8
MIN_DATA_POINTS = 20
MAX_NORMALIZED_RMSE = 0.15  # 15% error relative to signal range

# Physics sanity check ranges
PHYSICS_LIMITS = {
    'J': (1e-6, 100.0),      # Inertia (kg·m²)
    'b': (1e-6, 100.0),      # Damping (N·m·s/rad)
    'tau': (0.01, 100.0),    # Time constant (seconds)
    'K': (1e-3, 1000.0),     # Gain
    'kg': (0.0, 1.0),        # Gravity feedforward (0-1 normalized power)
    'omega_n': (0.1, 100.0), # Natural frequency (rad/s)
    'zeta': (0.01, 2.0),     # Damping ratio
    'friction': (0.0, 1.0),  # Friction (normalized)
}


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class ValidationMetrics:
    """Validation metrics for model fit quality."""
    R_squared: float
    RMSE: float
    normalized_RMSE: float
    MAE: float
    max_error: float
    num_samples: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PhysicsChecks:
    """Results of physics sanity checks."""
    all_passed: bool
    checks: Dict[str, Dict[str, Any]]
    warnings: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ResidualAnalysis:
    """Residual analysis results."""
    mean_residual: float
    std_residual: float
    normalized_residual_std: float
    autocorrelation_at_lag1: float
    systematic_bias: bool
    bias_description: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CrossValidationResults:
    """Cross-validation results."""
    enabled: bool
    train_R_squared: float
    test_R_squared: float
    overfitting_detected: bool
    notes: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ValidationReport:
    """Complete validation report."""
    validation_passed: bool
    model_type: str
    metrics: ValidationMetrics
    physics_checks: PhysicsChecks
    residual_analysis: ResidualAnalysis
    cross_validation: CrossValidationResults
    acceptance_criteria: Dict[str, Any]
    recommendations: List[str]
    fallback_suggestion: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'validation_passed': self.validation_passed,
            'model_type': self.model_type,
            'metrics': self.metrics.to_dict(),
            'physics_checks': self.physics_checks.to_dict(),
            'residual_analysis': self.residual_analysis.to_dict(),
            'cross_validation': self.cross_validation.to_dict(),
            'acceptance_criteria': self.acceptance_criteria,
            'recommendations': self.recommendations,
            'fallback_suggestion': self.fallback_suggestion,
        }


# ============================================================================
# MODEL SIMULATION
# ============================================================================

def simulate_first_order(params: Dict[str, float], u: np.ndarray,
                         t: np.ndarray) -> np.ndarray:
    """
    Simulate first-order system: G(s) = K / (tau*s + 1)

    State-space form:
        dx/dt = -x/tau + K*u/tau
        y = x
    """
    K = params.get('K', 1.0)
    tau = params.get('tau', 1.0)

    # State-space matrices
    A = -1.0 / tau
    B = K / tau
    C = 1.0
    D = 0.0

    sys = signal.StateSpace(A, B, C, D)

    # Simulate
    tout, y, x = signal.lsim(sys, u, t)

    return y


def simulate_first_order_gravity(params: Dict[str, float], u: np.ndarray,
                                  t: np.ndarray) -> np.ndarray:
    """
    Simulate first-order system with gravity compensation.

    u(t) = (K/tau) * error + kg
    Rearrange: input_to_plant = u - kg
    Then: G(s) = K / (tau*s + 1)
    """
    K = params.get('K', 1.0)
    tau = params.get('tau', 1.0)
    kg = params.get('kg', 0.0)

    # Remove gravity offset from input
    u_corrected = u - kg

    # Simulate first-order response
    return simulate_first_order({'K': K, 'tau': tau}, u_corrected, t)


def simulate_second_order(params: Dict[str, float], u: np.ndarray,
                          t: np.ndarray) -> np.ndarray:
    """
    Simulate second-order system: G(s) = K*omega_n^2 / (s^2 + 2*zeta*omega_n*s + omega_n^2)
    """
    K = params.get('K', 1.0)
    omega_n = params.get('omega_n', 1.0)
    zeta = params.get('zeta', 0.7)

    # Transfer function coefficients
    num = [K * omega_n**2]
    den = [1, 2 * zeta * omega_n, omega_n**2]

    sys = signal.TransferFunction(num, den)

    # Simulate
    tout, y = signal.lsim(sys, u, t)

    return y


def simulate_second_order_gravity(params: Dict[str, float], u: np.ndarray,
                                   t: np.ndarray) -> np.ndarray:
    """Simulate second-order system with gravity compensation."""
    K = params.get('K', 1.0)
    omega_n = params.get('omega_n', 1.0)
    zeta = params.get('zeta', 0.7)
    kg = params.get('kg', 0.0)

    # Remove gravity offset
    u_corrected = u - kg

    return simulate_second_order({'K': K, 'omega_n': omega_n, 'zeta': zeta},
                                 u_corrected, t)


def simulate_angle_dependent_gravity(params: Dict[str, float], u: np.ndarray,
                                      t: np.ndarray, angle: np.ndarray) -> np.ndarray:
    """
    Simulate angle-dependent gravity model for arms.
    u(t) = (K/tau) * error + kg * cos(angle)
    """
    K = params.get('K', 1.0)
    tau = params.get('tau', 1.0)
    kg = params.get('kg', 0.0)

    # Calculate angle-dependent gravity
    kg_array = kg * np.cos(angle)

    # Remove gravity offset (varies with angle)
    u_corrected = u - kg_array

    return simulate_first_order({'K': K, 'tau': tau}, u_corrected, t)


def simulate_friction_model(params: Dict[str, float], u: np.ndarray,
                            t: np.ndarray, initial_vel: float = 0.0) -> np.ndarray:
    """
    Simulate friction model: J * accel = torque - b * vel - friction * sign(vel) - kg

    Numerical integration of ODE.
    """
    J = params.get('J', 0.05)
    b = params.get('b', 0.02)
    friction = params.get('friction', 0.0)
    kg = params.get('kg', 0.0)

    def dynamics(state, t_current, u_func):
        """State = [position, velocity]"""
        pos, vel = state

        # Interpolate input at current time
        u_current = np.interp(t_current, t, u)

        # Friction term with sign
        friction_term = friction * np.sign(vel) if abs(vel) > 1e-6 else 0.0

        # Dynamics: J * dv/dt = u - kg - b*v - friction*sign(v)
        accel = (u_current - kg - b * vel - friction_term) / J

        return [vel, accel]

    # Initial conditions
    y0 = [0.0, initial_vel]

    # Integrate
    result = integrate.odeint(dynamics, y0, t, args=(u,))

    return result[:, 0]  # Return position


def simulate_variable_inertia(params: Dict[str, float], u: np.ndarray,
                               t: np.ndarray, position: np.ndarray) -> np.ndarray:
    """
    Simulate variable inertia model: J(pos) * accel = torque - b * vel - kg

    Note: This is more complex - we need position-dependent inertia.
    For now, use average inertia.
    """
    J_base = params.get('J_base', 0.05)
    J_slope = params.get('J_slope', 0.01)
    b = params.get('b', 0.02)
    kg = params.get('kg', 0.0)

    # Simplified: use average J
    max_pos = np.max(np.abs(position))
    if max_pos > 0:
        avg_extension = np.mean(np.abs(position)) / max_pos
    else:
        avg_extension = 0.0

    J_avg = J_base + J_slope * avg_extension

    # Use friction model with average J
    return simulate_friction_model({'J': J_avg, 'b': b, 'kg': kg, 'friction': 0.0},
                                   u, t)


def simulate_model(model: Dict[str, Any], u: np.ndarray, t: np.ndarray,
                   **kwargs) -> np.ndarray:
    """
    Simulate identified model with recorded inputs.

    Args:
        model: Identified model dictionary
        u: Input array (power/voltage)
        t: Time array
        **kwargs: Additional data (angle, position, etc.)

    Returns:
        y_predicted: Predicted output (position)
    """
    model_type = model.get('model_type', 'first_order')
    params = model.get('parameters', {})

    simulators = {
        'first_order': simulate_first_order,
        'first_order_gravity': simulate_first_order_gravity,
        'second_order': simulate_second_order,
        'second_order_gravity': simulate_second_order_gravity,
        'angle_dependent_gravity': simulate_angle_dependent_gravity,
        'friction': simulate_friction_model,
        'variable_inertia': simulate_variable_inertia,
    }

    simulator = simulators.get(model_type)
    if simulator is None:
        raise ValueError(f"Unknown model type: {model_type}")

    # Call appropriate simulator
    if model_type == 'angle_dependent_gravity':
        angle = kwargs.get('angle')
        if angle is None:
            raise ValueError("angle_dependent_gravity requires 'angle' array")
        return simulator(params, u, t, angle)
    elif model_type == 'variable_inertia':
        position = kwargs.get('position')
        if position is None:
            raise ValueError("variable_inertia requires 'position' array")
        return simulator(params, u, t, position)
    else:
        return simulator(params, u, t)


# ============================================================================
# VALIDATION METRICS
# ============================================================================

def calculate_r_squared(y_actual: np.ndarray, y_predicted: np.ndarray) -> float:
    """
    Calculate coefficient of determination (R²).

    R² = 1 - (SS_res / SS_tot)
    where:
        SS_res = sum of squared residuals
        SS_tot = total sum of squares

    R² = 1.0 means perfect fit
    R² = 0.0 means model no better than mean
    R² < 0.0 means model worse than mean
    """
    # Remove any NaN or inf values
    mask = np.isfinite(y_actual) & np.isfinite(y_predicted)
    y_actual = y_actual[mask]
    y_predicted = y_predicted[mask]

    if len(y_actual) < 2:
        return 0.0

    ss_res = np.sum((y_actual - y_predicted) ** 2)
    ss_tot = np.sum((y_actual - np.mean(y_actual)) ** 2)

    if ss_tot < 1e-10:  # Avoid division by zero
        return 0.0

    r_squared = 1.0 - (ss_res / ss_tot)

    return r_squared


def calculate_rmse(y_actual: np.ndarray, y_predicted: np.ndarray) -> float:
    """Calculate Root Mean Squared Error."""
    mask = np.isfinite(y_actual) & np.isfinite(y_predicted)
    y_actual = y_actual[mask]
    y_predicted = y_predicted[mask]

    if len(y_actual) == 0:
        return float('inf')

    mse = np.mean((y_actual - y_predicted) ** 2)
    rmse = np.sqrt(mse)

    return rmse


def calculate_mae(y_actual: np.ndarray, y_predicted: np.ndarray) -> float:
    """Calculate Mean Absolute Error."""
    mask = np.isfinite(y_actual) & np.isfinite(y_predicted)
    y_actual = y_actual[mask]
    y_predicted = y_predicted[mask]

    if len(y_actual) == 0:
        return float('inf')

    mae = np.mean(np.abs(y_actual - y_predicted))

    return mae


def calculate_normalized_rmse(y_actual: np.ndarray, y_predicted: np.ndarray) -> float:
    """
    Calculate normalized RMSE (NRMSE).

    NRMSE = RMSE / (max(y) - min(y))

    This gives error as a fraction of the signal range.
    """
    rmse = calculate_rmse(y_actual, y_predicted)

    mask = np.isfinite(y_actual)
    y_actual_clean = y_actual[mask]

    if len(y_actual_clean) == 0:
        return float('inf')

    signal_range = np.max(y_actual_clean) - np.min(y_actual_clean)

    if signal_range < 1e-6:  # Avoid division by zero
        return float('inf')

    nrmse = rmse / signal_range

    return nrmse


def calculate_validation_metrics(y_actual: np.ndarray,
                                 y_predicted: np.ndarray) -> ValidationMetrics:
    """Calculate all validation metrics."""
    r_squared = calculate_r_squared(y_actual, y_predicted)
    rmse = calculate_rmse(y_actual, y_predicted)
    nrmse = calculate_normalized_rmse(y_actual, y_predicted)
    mae = calculate_mae(y_actual, y_predicted)

    # Max error
    mask = np.isfinite(y_actual) & np.isfinite(y_predicted)
    errors = np.abs(y_actual[mask] - y_predicted[mask])
    max_error = np.max(errors) if len(errors) > 0 else float('inf')

    return ValidationMetrics(
        R_squared=r_squared,
        RMSE=rmse,
        normalized_RMSE=nrmse,
        MAE=mae,
        max_error=max_error,
        num_samples=len(y_actual[mask])
    )


# ============================================================================
# PHYSICS SANITY CHECKS
# ============================================================================

def check_physics_sanity(model: Dict[str, Any]) -> PhysicsChecks:
    """
    Perform physics sanity checks on identified parameters.

    Checks:
    1. All parameters within physically reasonable ranges
    2. Parameter signs correct (J > 0, b > 0, etc.)
    3. Confidence intervals reasonable
    """
    params = model.get('parameters', {})
    confidence = model.get('confidence', {})

    checks = {}
    warnings_list = []
    all_passed = True

    for param_name, value in params.items():
        if param_name not in PHYSICS_LIMITS:
            continue

        min_val, max_val = PHYSICS_LIMITS[param_name]

        # Check range
        in_range = min_val <= value <= max_val

        # Check confidence if available
        param_confidence = confidence.get(param_name, 1.0)
        high_confidence = param_confidence >= CONFIDENCE_THRESHOLD

        check_result = {
            'value': value,
            'range': [min_val, max_val],
            'in_range': in_range,
            'confidence': param_confidence,
            'high_confidence': high_confidence,
            'passed': in_range and high_confidence
        }

        checks[param_name] = check_result

        if not in_range:
            all_passed = False
            warnings_list.append(
                f"Parameter '{param_name}' = {value:.6f} outside physical range "
                f"[{min_val}, {max_val}]"
            )

        if not high_confidence:
            all_passed = False
            warnings_list.append(
                f"Parameter '{param_name}' has low confidence: {param_confidence:.3f} "
                f"(threshold: {CONFIDENCE_THRESHOLD})"
            )

    # Additional sanity checks for specific models
    model_type = model.get('model_type')

    if model_type in ['second_order', 'second_order_gravity']:
        zeta = params.get('zeta', 0.7)
        if zeta < 0.1:
            warnings_list.append(
                f"Very low damping ratio (zeta={zeta:.3f}) - "
                "system may be highly oscillatory"
            )
        elif zeta > 1.5:
            warnings_list.append(
                f"Very high damping ratio (zeta={zeta:.3f}) - "
                "system may be over-damped"
            )

    return PhysicsChecks(
        all_passed=all_passed,
        checks=checks,
        warnings=warnings_list
    )


# ============================================================================
# RESIDUAL ANALYSIS
# ============================================================================

def analyze_residuals(y_actual: np.ndarray,
                      y_predicted: np.ndarray) -> ResidualAnalysis:
    """
    Analyze residuals for systematic errors.

    Good model should have:
    1. Mean residual near zero (no bias)
    2. Low standard deviation
    3. Low autocorrelation (white noise residuals)
    """
    # Calculate residuals
    mask = np.isfinite(y_actual) & np.isfinite(y_predicted)
    residuals = y_actual[mask] - y_predicted[mask]

    if len(residuals) < 2:
        return ResidualAnalysis(
            mean_residual=0.0,
            std_residual=0.0,
            normalized_residual_std=0.0,
            autocorrelation_at_lag1=0.0,
            systematic_bias=False,
            bias_description="Insufficient data"
        )

    # Statistics
    mean_residual = np.mean(residuals)
    std_residual = np.std(residuals)

    # Normalized std
    signal_range = np.max(y_actual[mask]) - np.min(y_actual[mask])
    if signal_range > 1e-6:
        normalized_std = std_residual / signal_range
    else:
        normalized_std = float('inf')

    # Autocorrelation at lag 1
    if len(residuals) > 2:
        autocorr = np.corrcoef(residuals[:-1], residuals[1:])[0, 1]
        if not np.isfinite(autocorr):
            autocorr = 0.0
    else:
        autocorr = 0.0

    # Check for systematic bias
    systematic_bias = False
    bias_description = "No significant bias detected"

    # Mean bias check (> 5% of std)
    if abs(mean_residual) > 0.05 * signal_range:
        systematic_bias = True
        bias_description = f"Constant bias: mean residual = {mean_residual:.4f}"

    # Autocorrelation check (> 0.5 suggests systematic error)
    if abs(autocorr) > 0.5:
        systematic_bias = True
        bias_description += f"; High autocorrelation = {autocorr:.3f} (residuals not white noise)"

    return ResidualAnalysis(
        mean_residual=mean_residual,
        std_residual=std_residual,
        normalized_residual_std=normalized_std,
        autocorrelation_at_lag1=autocorr,
        systematic_bias=systematic_bias,
        bias_description=bias_description
    )


# ============================================================================
# CROSS-VALIDATION
# ============================================================================

def cross_validate(model: Dict[str, Any], telemetry: Dict[str, Any],
                   train_fraction: float = 0.7) -> CrossValidationResults:
    """
    Perform train/test split cross-validation.

    Process:
    1. Split data into train (70%) and test (30%)
    2. Model was identified on full data, but we check generalization
    3. Calculate R² on both train and test sets
    4. If test R² << train R², model is overfitting
    """
    data = telemetry.get('data', [])

    if len(data) < 20:
        return CrossValidationResults(
            enabled=False,
            train_R_squared=0.0,
            test_R_squared=0.0,
            overfitting_detected=False,
            notes="Insufficient data for cross-validation (< 20 samples)"
        )

    # Split data
    split_idx = int(len(data) * train_fraction)
    train_data = data[:split_idx]
    test_data = data[split_idx:]

    # Extract arrays
    def extract_arrays(data_subset):
        t = np.array([d.get('t', d.get('timestamp', 0)) for d in data_subset])
        pos = np.array([d.get('pos', d.get('position', 0)) for d in data_subset])
        u = np.array([d.get('power', d.get('u', 0)) for d in data_subset])
        return t, pos, u

    t_train, pos_train, u_train = extract_arrays(train_data)
    t_test, pos_test, u_test = extract_arrays(test_data)

    # Normalize time for test set
    if len(t_test) > 0:
        t_test = t_test - t_test[0]

    # Simulate on train set
    try:
        y_pred_train = simulate_model(model, u_train, t_train, position=pos_train)
        r2_train = calculate_r_squared(pos_train, y_pred_train)
    except Exception as e:
        return CrossValidationResults(
            enabled=False,
            train_R_squared=0.0,
            test_R_squared=0.0,
            overfitting_detected=False,
            notes=f"Train simulation failed: {e}"
        )

    # Simulate on test set
    try:
        y_pred_test = simulate_model(model, u_test, t_test, position=pos_test)
        r2_test = calculate_r_squared(pos_test, y_pred_test)
    except Exception as e:
        return CrossValidationResults(
            enabled=True,
            train_R_squared=r2_train,
            test_R_squared=0.0,
            overfitting_detected=False,
            notes=f"Test simulation failed: {e}"
        )

    # Check for overfitting
    # If test R² is more than 0.15 worse than train R², model may be overfitting
    overfitting = (r2_train - r2_test) > 0.15

    notes = "Cross-validation successful"
    if overfitting:
        notes = (f"Possible overfitting: train R²={r2_train:.3f}, "
                f"test R²={r2_test:.3f}")

    return CrossValidationResults(
        enabled=True,
        train_R_squared=r2_train,
        test_R_squared=r2_test,
        overfitting_detected=overfitting,
        notes=notes
    )


# ============================================================================
# FALLBACK SUGGESTIONS
# ============================================================================

MODEL_SIMPLIFICATION = {
    'variable_inertia': 'friction',
    'friction': 'second_order_gravity',
    'second_order_gravity': 'first_order_gravity',
    'second_order': 'first_order',
    'angle_dependent_gravity': 'first_order_gravity',
    'first_order_gravity': 'first_order',
    'first_order': None,  # Can't simplify further
}


def suggest_fallback(model: Dict[str, Any],
                     validation_report: ValidationReport) -> Optional[str]:
    """
    Suggest simpler model if validation fails.

    Returns:
        Fallback model type, or None if at simplest model
    """
    current_model = model.get('model_type')

    # If physics checks failed, suggest simpler model
    if not validation_report.physics_checks.all_passed:
        fallback = MODEL_SIMPLIFICATION.get(current_model)
        if fallback:
            return f"Try simpler model: {fallback} (physics checks failed)"

    # If R² too low, suggest simpler model (may be overfitting)
    if validation_report.metrics.R_squared < R_SQUARED_THRESHOLD:
        fallback = MODEL_SIMPLIFICATION.get(current_model)
        if fallback:
            return (f"Try simpler model: {fallback} "
                   f"(R²={validation_report.metrics.R_squared:.3f} < {R_SQUARED_THRESHOLD})")

    # If overfitting detected, definitely suggest simpler model
    if validation_report.cross_validation.overfitting_detected:
        fallback = MODEL_SIMPLIFICATION.get(current_model)
        if fallback:
            return f"Try simpler model: {fallback} (overfitting detected)"

    # If systematic bias, may need different model structure
    if validation_report.residual_analysis.systematic_bias:
        return ("Consider different model structure or collect cleaner data "
               "(systematic bias in residuals)")

    return None


# ============================================================================
# MAIN VALIDATION FUNCTION
# ============================================================================

def validate_model(model: Dict[str, Any], telemetry: Dict[str, Any],
                   enable_cross_validation: bool = False) -> ValidationReport:
    """
    Validate identified model.

    Args:
        model: Identified model from identify_params.py
        telemetry: Test data for validation
        enable_cross_validation: Whether to perform cross-validation

    Returns:
        ValidationReport with all validation results
    """
    # Extract time series
    data = telemetry.get('data', [])

    if len(data) < MIN_DATA_POINTS:
        print(f"WARNING: Insufficient data points ({len(data)} < {MIN_DATA_POINTS})")

    t = np.array([d.get('t', d.get('timestamp', 0)) for d in data])
    pos = np.array([d.get('pos', d.get('position', 0)) for d in data])
    u = np.array([d.get('power', d.get('u', 0)) for d in data])

    # Additional data for specific models
    angle = np.array([d.get('angle', 0) for d in data]) if 'angle' in data[0] else None

    # Simulate model
    print(f"Simulating {model.get('model_type')} model...")
    try:
        kwargs = {'position': pos}
        if angle is not None:
            kwargs['angle'] = angle

        y_predicted = simulate_model(model, u, t, **kwargs)
    except Exception as e:
        print(f"ERROR: Model simulation failed: {e}")
        # Return failed validation
        return ValidationReport(
            validation_passed=False,
            model_type=model.get('model_type', 'unknown'),
            metrics=ValidationMetrics(0.0, float('inf'), float('inf'),
                                     float('inf'), float('inf'), 0),
            physics_checks=PhysicsChecks(False, {}, [f"Simulation failed: {e}"]),
            residual_analysis=ResidualAnalysis(0, 0, 0, 0, False, ""),
            cross_validation=CrossValidationResults(False, 0, 0, False, ""),
            acceptance_criteria={},
            recommendations=["Model simulation failed - try simpler model"],
            fallback_suggestion=MODEL_SIMPLIFICATION.get(
                model.get('model_type'), 'first_order'
            )
        )

    # Calculate validation metrics
    print("Calculating validation metrics...")
    metrics = calculate_validation_metrics(pos, y_predicted)

    print(f"  R² = {metrics.R_squared:.4f}")
    print(f"  RMSE = {metrics.RMSE:.4f}")
    print(f"  Normalized RMSE = {metrics.normalized_RMSE:.4f}")

    # Physics sanity checks
    print("Performing physics sanity checks...")
    physics_checks = check_physics_sanity(model)

    if physics_checks.all_passed:
        print("  ✓ All physics checks passed")
    else:
        print(f"  ✗ Physics checks failed ({len(physics_checks.warnings)} warnings)")
        for warning in physics_checks.warnings:
            print(f"    - {warning}")

    # Residual analysis
    print("Analyzing residuals...")
    residual_analysis = analyze_residuals(pos, y_predicted)

    if residual_analysis.systematic_bias:
        print(f"  ⚠ Systematic bias detected: {residual_analysis.bias_description}")
    else:
        print("  ✓ No systematic bias detected")

    # Cross-validation
    if enable_cross_validation:
        print("Performing cross-validation...")
        cross_val = cross_validate(model, telemetry)

        if cross_val.enabled:
            print(f"  Train R² = {cross_val.train_R_squared:.4f}")
            print(f"  Test R² = {cross_val.test_R_squared:.4f}")
            if cross_val.overfitting_detected:
                print("  ⚠ Overfitting detected")
    else:
        cross_val = CrossValidationResults(False, 0, 0, False,
                                          "Cross-validation not enabled")

    # Acceptance criteria
    acceptance_criteria = {
        'R_squared_threshold': R_SQUARED_THRESHOLD,
        'confidence_threshold': CONFIDENCE_THRESHOLD,
        'max_normalized_RMSE': MAX_NORMALIZED_RMSE,
        'min_data_points': MIN_DATA_POINTS,
    }

    # Determine if validation passed
    validation_passed = (
        metrics.R_squared >= R_SQUARED_THRESHOLD and
        metrics.normalized_RMSE <= MAX_NORMALIZED_RMSE and
        physics_checks.all_passed and
        not residual_analysis.systematic_bias and
        not cross_val.overfitting_detected and
        metrics.num_samples >= MIN_DATA_POINTS
    )

    # Generate recommendations
    recommendations = []

    if validation_passed:
        recommendations.append("✓ Model validation passed - safe to use for gain calculation")
    else:
        recommendations.append("✗ Model validation failed")

    if metrics.R_squared < R_SQUARED_THRESHOLD:
        recommendations.append(
            f"  - R² ({metrics.R_squared:.3f}) below threshold ({R_SQUARED_THRESHOLD})"
        )

    if metrics.normalized_RMSE > MAX_NORMALIZED_RMSE:
        recommendations.append(
            f"  - Normalized RMSE ({metrics.normalized_RMSE:.3f}) above threshold "
            f"({MAX_NORMALIZED_RMSE})"
        )

    if not physics_checks.all_passed:
        recommendations.append("  - Physics sanity checks failed")

    if residual_analysis.systematic_bias:
        recommendations.append("  - Systematic bias in residuals detected")

    if cross_val.overfitting_detected:
        recommendations.append("  - Model overfitting detected in cross-validation")

    if metrics.num_samples < MIN_DATA_POINTS:
        recommendations.append(
            f"  - Insufficient data points ({metrics.num_samples} < {MIN_DATA_POINTS})"
        )

    # Create report
    report = ValidationReport(
        validation_passed=validation_passed,
        model_type=model.get('model_type', 'unknown'),
        metrics=metrics,
        physics_checks=physics_checks,
        residual_analysis=residual_analysis,
        cross_validation=cross_val,
        acceptance_criteria=acceptance_criteria,
        recommendations=recommendations,
        fallback_suggestion=None
    )

    # Suggest fallback if validation failed
    if not validation_passed:
        fallback = suggest_fallback(model, report)
        report.fallback_suggestion = fallback

    return report


# ============================================================================
# MAIN
# ============================================================================

def load_json(file_path: Path) -> Dict[str, Any]:
    """Load JSON file."""
    with open(file_path) as f:
        return json.load(f)


def save_json(data: Dict[str, Any], file_path: Path):
    """Save JSON file with numpy type handling."""

    # Convert numpy types to Python native types
    def convert_numpy(obj):
        if isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: convert_numpy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy(item) for item in obj]
        else:
            return obj

    data_converted = convert_numpy(data)

    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(data_converted, f, indent=2)
    print(f"✓ Saved validation report to {file_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Validate identified model for system identification"
    )
    parser.add_argument(
        '--model', type=str, required=True,
        help="Path to identified_model.json"
    )
    parser.add_argument(
        '--test-data', type=str, required=True,
        help="Path to test telemetry data (sysid_data.json)"
    )
    parser.add_argument(
        '--output', type=str, default='validation_report.json',
        help="Output validation report path (default: validation_report.json)"
    )
    parser.add_argument(
        '--cross-validate', action='store_true',
        help="Enable cross-validation (train/test split)"
    )

    args = parser.parse_args()

    # Load data
    print(f"Loading model from {args.model}...")
    model = load_json(Path(args.model))

    print(f"Loading test data from {args.test_data}...")
    telemetry = load_json(Path(args.test_data))

    print()
    print("="*60)
    print("MODEL VALIDATION")
    print("="*60)
    print(f"Model type: {model.get('model_type')}")
    print(f"Parameters: {model.get('parameters')}")
    print()

    # Validate model
    report = validate_model(model, telemetry,
                           enable_cross_validation=args.cross_validate)

    # Print results
    print()
    print("="*60)
    print("VALIDATION RESULTS")
    print("="*60)
    print()

    if report.validation_passed:
        print("✓ VALIDATION PASSED")
    else:
        print("✗ VALIDATION FAILED")

    print()
    print("Metrics:")
    print(f"  R² = {report.metrics.R_squared:.4f} (threshold: {R_SQUARED_THRESHOLD})")
    print(f"  RMSE = {report.metrics.RMSE:.4f}")
    print(f"  Normalized RMSE = {report.metrics.normalized_RMSE:.4f} "
          f"(threshold: {MAX_NORMALIZED_RMSE})")
    print(f"  MAE = {report.metrics.MAE:.4f}")
    print(f"  Max Error = {report.metrics.max_error:.4f}")
    print(f"  Samples = {report.metrics.num_samples}")

    print()
    print("Recommendations:")
    for rec in report.recommendations:
        print(f"  {rec}")

    if report.fallback_suggestion:
        print()
        print(f"Fallback suggestion: {report.fallback_suggestion}")

    print()

    # Save report
    save_json(report.to_dict(), Path(args.output))

    # Exit code
    return 0 if report.validation_passed else 1


if __name__ == "__main__":
    sys.exit(main())

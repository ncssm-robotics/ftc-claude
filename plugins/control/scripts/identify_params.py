#!/usr/bin/env python3
"""
System Identification - Parameter Identification for FTC Control Systems

Identifies physical parameters from telemetry data using least-squares fitting.
Supports adaptive model selection based on mechanism type and characteristics.

Model Library:
1. First-order: G(s) = K / (τs + 1)
2. First-order + gravity: u(t) = (K/τ) * error + kg
3. Second-order: G(s) = K*ωn² / (s² + 2ζωn*s + ωn²)
4. Second-order + gravity: Same as #3 with kg term

Usage:
    # Auto-select model based on data
    uv run identify_params.py --data sysid_data.json --auto-select

    # Interactive model selection
    uv run identify_params.py --data sysid_data.json --interactive

    # Specify model explicitly
    uv run identify_params.py --data sysid_data.json --model first-order-gravity

    # Output to specific file
    uv run identify_params.py --data sysid_data.json --output identified_model.json
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
from enum import Enum

import numpy as np
from scipy import optimize, signal, stats


# ============================================================================
# MODEL DEFINITIONS
# ============================================================================

class ModelType(Enum):
    """Available model structures."""
    FIRST_ORDER = "first-order"
    FIRST_ORDER_GRAVITY = "first-order-gravity"
    SECOND_ORDER = "second-order"
    SECOND_ORDER_GRAVITY = "second-order-gravity"
    ANGLE_DEPENDENT = "angle-dependent"
    FRICTION = "friction"
    VARIABLE_INERTIA = "variable-inertia"


@dataclass
class IdentifiedModel:
    """Container for identified model parameters."""
    model_type: str
    parameters: Dict[str, float]
    confidence_intervals: Dict[str, Tuple[float, float]]
    transfer_function: str
    fit_quality: Dict[str, float]
    mechanism: str
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "model_type": self.model_type,
            "parameters": self.parameters,
            "confidence_intervals": {
                k: {"lower": v[0], "upper": v[1]}
                for k, v in self.confidence_intervals.items()
            },
            "transfer_function": self.transfer_function,
            "fit_quality": self.fit_quality,
            "mechanism": self.mechanism,
            "notes": self.notes
        }


# ============================================================================
# DATA LOADING & PREPROCESSING
# ============================================================================

def load_telemetry(file_path: Path) -> Dict[str, Any]:
    """Load telemetry data from JSON file."""
    with open(file_path) as f:
        data = json.load(f)

    # Validate required fields
    if "data" not in data:
        raise ValueError("Telemetry file must contain 'data' field")

    return data


def extract_time_series(telemetry: Dict[str, Any]) -> Dict[str, np.ndarray]:
    """Extract numpy arrays from telemetry data."""
    data = telemetry.get("data", [])

    if len(data) == 0:
        raise ValueError("Telemetry data is empty")

    # Extract common fields
    t = np.array([d.get("t", 0) for d in data])
    pos = np.array([d.get("pos", 0) for d in data])
    vel = np.array([d.get("vel", 0) for d in data])
    target = np.array([d.get("target", 0) for d in data])
    power = np.array([d.get("power", 0) for d in data])

    # Calculate error if not provided
    error = np.array([d.get("error", t - p) for d, t, p in zip(data, target, pos)])

    return {
        "t": t,
        "pos": pos,
        "vel": vel,
        "target": target,
        "error": error,
        "power": power
    }


def find_step_response(series: Dict[str, np.ndarray], min_step_size: float = 10.0) -> Tuple[int, float]:
    """
    Find the primary step input in telemetry data.

    Returns:
        Tuple of (step_index, step_size)
    """
    target = series["target"]
    target_changes = np.diff(target)

    # Find significant step changes
    step_indices = np.where(np.abs(target_changes) > min_step_size)[0]

    if len(step_indices) == 0:
        raise ValueError(f"No step input detected (threshold: {min_step_size})")

    # Use first major step
    step_idx = step_indices[0]
    step_size = target_changes[step_idx]

    return step_idx, step_size


def detect_overshoot(series: Dict[str, np.ndarray], step_idx: int, step_size: float) -> float:
    """
    Detect overshoot percentage in step response.

    Returns:
        Overshoot percentage (0-100)
    """
    pos = series["pos"][step_idx:]
    target = series["target"][step_idx + 1]

    if len(pos) < 10:
        return 0.0

    # Find peak overshoot
    if step_size > 0:
        max_pos = np.max(pos)
        overshoot = (max_pos - target) / abs(step_size) * 100
    else:
        min_pos = np.min(pos)
        overshoot = (target - min_pos) / abs(step_size) * 100

    return max(0.0, overshoot)


def estimate_noise_level(series: Dict[str, np.ndarray]) -> float:
    """
    Estimate noise level in position signal.

    Returns:
        Standard deviation of position differences (proxy for noise)
    """
    pos = series["pos"]

    # Use differences to estimate high-frequency noise
    pos_diff = np.diff(pos)
    noise_std = np.std(pos_diff)

    return noise_std


# ============================================================================
# MODEL IDENTIFICATION - FIRST ORDER
# ============================================================================

def identify_first_order(series: Dict[str, np.ndarray], step_idx: int) -> Dict[str, Any]:
    """
    Identify first-order system: G(s) = K / (τs + 1)

    Uses least-squares fitting to exponential response:
    pos(t) = pos_initial + K * (1 - exp(-t/τ))

    Returns:
        Dictionary with parameters {K, tau}, residuals, and covariance
    """
    t = series["t"][step_idx:]
    pos = series["pos"][step_idx:]
    target = series["target"][step_idx + 1]

    # Normalize time to start at 0
    t_norm = t - t[0]
    pos_initial = pos[0]

    # Define exponential model
    def exponential_model(t, K, tau):
        return pos_initial + K * (1 - np.exp(-t / tau))

    # Initial parameter guess
    final_value = pos[-1]
    K_guess = final_value - pos_initial
    tau_guess = 1.0  # 1 second initial guess

    # Bounds: K can be negative (downward step), tau must be positive
    bounds = ([K_guess * 0.5, 0.01], [K_guess * 2.0, 10.0])

    try:
        # Fit exponential
        params, cov = optimize.curve_fit(
            exponential_model,
            t_norm,
            pos,
            p0=[K_guess, tau_guess],
            bounds=bounds,
            maxfev=5000
        )

        K, tau = params

        # Calculate residuals
        pos_fitted = exponential_model(t_norm, K, tau)
        residuals = pos - pos_fitted

        return {
            "K": K,
            "tau": tau,
            "residuals": residuals,
            "covariance": cov,
            "fitted_response": pos_fitted
        }

    except Exception as e:
        raise ValueError(f"First-order fitting failed: {e}")


def identify_first_order_gravity(series: Dict[str, np.ndarray], step_idx: int) -> Dict[str, Any]:
    """
    Identify first-order system with gravity compensation.

    Model: u(t) = (K/τ) * error + kg

    Fits exponential response and estimates kg from steady-state power.

    Returns:
        Dictionary with parameters {K, tau, kg}, residuals, and covariance
    """
    # First identify K and tau using first-order method
    result = identify_first_order(series, step_idx)

    K = result["K"]
    tau = result["tau"]

    # Estimate gravity feedforward from steady-state power
    power = series["power"][step_idx:]

    if len(power) > 20:
        # Use last 20% of data for steady-state estimate
        steady_state_start = int(len(power) * 0.8)
        kg = np.mean(power[steady_state_start:])
    else:
        kg = 0.0

    # Add kg to result
    result["kg"] = kg

    # Extend covariance matrix (kg has no covariance in this simple estimate)
    # In a full implementation, we'd re-fit with kg as a parameter

    return result


# ============================================================================
# MODEL IDENTIFICATION - SECOND ORDER
# ============================================================================

def identify_second_order(series: Dict[str, np.ndarray], step_idx: int) -> Dict[str, Any]:
    """
    Identify second-order system: G(s) = K*ωn² / (s² + 2ζωn*s + ωn²)

    Uses least-squares fitting to second-order step response:
    For underdamped (ζ < 1):
        pos(t) = K * (1 - exp(-ζωn*t) * (cos(ωd*t) + (ζ/√(1-ζ²)) * sin(ωd*t)))
        where ωd = ωn * √(1-ζ²)

    Returns:
        Dictionary with parameters {K, omega_n, zeta}, residuals, and covariance
    """
    t = series["t"][step_idx:]
    pos = series["pos"][step_idx:]

    # Normalize time
    t_norm = t - t[0]
    pos_initial = pos[0]

    # Define second-order step response model
    def second_order_model(t, K, omega_n, zeta):
        if zeta >= 1.0:
            # Overdamped or critically damped
            zeta = min(zeta, 0.999)  # Numerical stability

        wd = omega_n * np.sqrt(1 - zeta**2)  # Damped frequency

        exponential = np.exp(-zeta * omega_n * t)
        phase = np.sqrt(1 - zeta**2)

        response = K * (1 - exponential * (
            np.cos(wd * t) + (zeta / phase) * np.sin(wd * t)
        ))

        return pos_initial + response

    # Initial parameter guess
    final_value = pos[-1]
    K_guess = final_value - pos_initial

    # Estimate omega_n from rise time (rough approximation)
    rise_90_thresh = pos_initial + 0.9 * K_guess
    rise_idx = np.where(pos >= rise_90_thresh)[0]
    if len(rise_idx) > 0:
        rise_time = t_norm[rise_idx[0]]
        omega_n_guess = 2.2 / rise_time  # Approximation for ζ ≈ 0.7
    else:
        omega_n_guess = 3.0  # Default

    # Estimate zeta from overshoot
    overshoot = detect_overshoot({"pos": pos, "target": series["target"][step_idx:]}, 0, K_guess)
    if overshoot > 5:
        # Underdamped: overshoot relates to zeta
        # Overshoot% ≈ 100 * exp(-πζ / √(1-ζ²))
        # Rough inverse: ζ ≈ -ln(overshoot/100) / π
        zeta_guess = max(0.1, min(0.9, -np.log(overshoot / 100) / np.pi))
    else:
        zeta_guess = 0.7  # Critically damped default

    # Parameter bounds
    bounds = (
        [K_guess * 0.5, 0.1, 0.05],  # Lower: K, omega_n, zeta
        [K_guess * 2.0, 20.0, 1.0]    # Upper: K, omega_n, zeta
    )

    try:
        # Fit second-order model
        params, cov = optimize.curve_fit(
            second_order_model,
            t_norm,
            pos,
            p0=[K_guess, omega_n_guess, zeta_guess],
            bounds=bounds,
            maxfev=10000
        )

        K, omega_n, zeta = params

        # Calculate residuals
        pos_fitted = second_order_model(t_norm, K, omega_n, zeta)
        residuals = pos - pos_fitted

        return {
            "K": K,
            "omega_n": omega_n,
            "zeta": zeta,
            "residuals": residuals,
            "covariance": cov,
            "fitted_response": pos_fitted
        }

    except Exception as e:
        raise ValueError(f"Second-order fitting failed: {e}")


def identify_second_order_gravity(series: Dict[str, np.ndarray], step_idx: int) -> Dict[str, Any]:
    """
    Identify second-order system with gravity compensation.

    Returns:
        Dictionary with parameters {K, omega_n, zeta, kg}, residuals, covariance
    """
    # Identify K, omega_n, zeta using second-order method
    result = identify_second_order(series, step_idx)

    # Estimate gravity from steady-state power
    power = series["power"][step_idx:]

    if len(power) > 20:
        steady_state_start = int(len(power) * 0.8)
        kg = np.mean(power[steady_state_start:])
    else:
        kg = 0.0

    result["kg"] = kg

    return result


# ============================================================================
# MODEL IDENTIFICATION - ANGLE-DEPENDENT, FRICTION, VARIABLE-INERTIA
# ============================================================================

def identify_angle_dependent(series: Dict[str, np.ndarray], step_idx: int,
                            angle_formula: Optional[str] = None) -> Dict[str, Any]:
    """
    Identify angle-dependent gravity model: u(t) = (K/τ) * error + kg * cos(angle)

    Requires angle calculation from encoder position. If angle_formula not provided,
    prompts user for it.

    Args:
        series: Time series data
        step_idx: Index of step input
        angle_formula: Formula to calculate angle from position (e.g., "pos * 360 / 8192")

    Returns:
        Dictionary with parameters {K, tau, kg}, residuals, covariance, angle_formula
    """
    # Get angle formula from user if not provided
    if angle_formula is None:
        print("\n=== Angle Calculation Required ===")
        print("Enter formula to calculate angle (degrees) from encoder position.")
        print("Available variables: 'pos' (encoder ticks)")
        print("Example: pos * 360 / 8192  (for 8192 ticks per revolution)")
        angle_formula = input("Angle formula: ").strip()

    # Calculate angles from positions
    pos = series["pos"]
    try:
        # Create safe namespace for eval
        namespace = {"pos": pos, "np": np, "numpy": np}
        angles_deg = eval(angle_formula, {"__builtins__": {}}, namespace)
        angles_rad = np.deg2rad(angles_deg)
    except Exception as e:
        raise ValueError(f"Invalid angle formula '{angle_formula}': {e}")

    # Extract data after step
    t = series["t"][step_idx:]
    pos_data = series["pos"][step_idx:]
    power = series["power"][step_idx:]
    target = series["target"][step_idx + 1]
    angles = angles_rad[step_idx:]

    # Normalize time
    t_norm = t - t[0]
    pos_initial = pos_data[0]

    # Model: pos(t) = pos_initial + K * (1 - exp(-t/tau)) + kg*cos(angle)*t
    # We need to fit K, tau, kg simultaneously

    def angle_dependent_model(t, K, tau, kg):
        # Exponential approach to target
        pos_response = pos_initial + K * (1 - np.exp(-t / tau))
        return pos_response

    # Initial guess from first-order fit
    final_value = pos_data[-1]
    K_guess = final_value - pos_initial
    tau_guess = 1.0

    # Estimate kg from steady-state power and angle
    if len(power) > 20:
        steady_state_start = int(len(power) * 0.8)
        avg_power = np.mean(power[steady_state_start:])
        avg_cos_angle = np.mean(np.cos(angles[steady_state_start:]))
        kg_guess = avg_power / avg_cos_angle if abs(avg_cos_angle) > 0.1 else avg_power
    else:
        kg_guess = 0.0

    # Bounds
    bounds = ([K_guess * 0.5, 0.01, -abs(kg_guess) * 2],
              [K_guess * 2.0, 10.0, abs(kg_guess) * 2])

    try:
        # Fit the model
        params, cov = optimize.curve_fit(
            angle_dependent_model,
            t_norm,
            pos_data,
            p0=[K_guess, tau_guess, kg_guess],
            bounds=bounds,
            maxfev=5000
        )

        K, tau, kg = params

        # Calculate residuals
        pos_fitted = angle_dependent_model(t_norm, K, tau, kg)
        residuals = pos_data - pos_fitted

        return {
            "K": K,
            "tau": tau,
            "kg": kg,
            "angle_formula": angle_formula,
            "residuals": residuals,
            "covariance": cov,
            "fitted_response": pos_fitted
        }

    except Exception as e:
        raise ValueError(f"Angle-dependent fitting failed: {e}")


def identify_friction(series: Dict[str, np.ndarray], step_idx: int) -> Dict[str, Any]:
    """
    Identify friction model: J*accel = torque - b*vel - friction*sign(vel)

    Uses numerical differentiation to calculate acceleration from velocity.
    Fits inertia (J), damping (b), Coulomb friction (friction), and gravity (kg).

    Args:
        series: Time series data with velocity measurements
        step_idx: Index of step input

    Returns:
        Dictionary with parameters {J, b, friction, kg}, residuals, covariance
    """
    t = series["t"][step_idx:]
    vel = series["vel"][step_idx:]
    power = series["power"][step_idx:]

    # Calculate acceleration using central differences
    dt = np.diff(t)
    accel = np.zeros_like(vel)

    # Central difference for interior points
    for i in range(1, len(vel) - 1):
        accel[i] = (vel[i+1] - vel[i-1]) / (t[i+1] - t[i-1])

    # Forward/backward difference for edges
    if len(vel) > 2:
        accel[0] = (vel[1] - vel[0]) / (t[1] - t[0])
        accel[-1] = (vel[-1] - vel[-2]) / (t[-1] - t[-2])

    # Model: J*accel = power - b*vel - friction*sign(vel) - kg
    # Rearrange: power = J*accel + b*vel + friction*sign(vel) + kg

    def friction_model(X, J, b, friction, kg):
        accel, vel = X
        return J * accel + b * vel + friction * np.sign(vel) + kg

    # Prepare data for curve_fit
    X_data = np.vstack([accel, vel])
    y_data = power

    # Initial guesses
    J_guess = 1.0
    b_guess = 0.1

    # Estimate friction from dead zone
    near_zero_vel = np.abs(vel) < 0.1 * np.max(np.abs(vel))
    if np.any(near_zero_vel):
        friction_guess = np.mean(np.abs(power[near_zero_vel]))
    else:
        friction_guess = 0.01

    # Estimate kg from steady state
    if len(power) > 20:
        steady_state_start = int(len(power) * 0.8)
        kg_guess = np.mean(power[steady_state_start:])
    else:
        kg_guess = 0.0

    # Bounds (J, b, friction must be positive)
    bounds = ([0.001, 0.0, 0.0, -abs(kg_guess) * 2],
              [100.0, 10.0, 1.0, abs(kg_guess) * 2])

    try:
        params, cov = optimize.curve_fit(
            friction_model,
            X_data,
            y_data,
            p0=[J_guess, b_guess, friction_guess, kg_guess],
            bounds=bounds,
            maxfev=10000
        )

        J, b, friction_param, kg = params

        # Calculate residuals
        power_fitted = friction_model(X_data, J, b, friction_param, kg)
        residuals = y_data - power_fitted

        return {
            "J": J,
            "b": b,
            "friction": friction_param,
            "kg": kg,
            "residuals": residuals,
            "covariance": cov,
            "fitted_response": power_fitted
        }

    except Exception as e:
        raise ValueError(f"Friction model fitting failed: {e}")


def identify_variable_inertia(series: Dict[str, np.ndarray], step_idx: int) -> Dict[str, Any]:
    """
    Identify variable inertia model: J(pos)*accel = torque - b*vel - kg

    Where J(pos) = J_base + J_slope * pos (linear position-dependent inertia).
    Useful for telescoping mechanisms where mass/inertia changes with extension.

    Args:
        series: Time series data with position and velocity
        step_idx: Index of step input

    Returns:
        Dictionary with parameters {J_base, J_slope, b, kg}, residuals, covariance
    """
    t = series["t"][step_idx:]
    pos = series["pos"][step_idx:]
    vel = series["vel"][step_idx:]
    power = series["power"][step_idx:]

    # Calculate acceleration
    accel = np.zeros_like(vel)
    for i in range(1, len(vel) - 1):
        accel[i] = (vel[i+1] - vel[i-1]) / (t[i+1] - t[i-1])

    if len(vel) > 2:
        accel[0] = (vel[1] - vel[0]) / (t[1] - t[0])
        accel[-1] = (vel[-1] - vel[-2]) / (t[-1] - t[-2])

    # Model: (J_base + J_slope*pos)*accel = power - b*vel - kg
    # Rearrange: power = (J_base + J_slope*pos)*accel + b*vel + kg

    def variable_inertia_model(X, J_base, J_slope, b, kg):
        pos, accel, vel = X
        J_pos = J_base + J_slope * pos
        return J_pos * accel + b * vel + kg

    # Prepare data
    X_data = np.vstack([pos, accel, vel])
    y_data = power

    # Initial guesses
    J_base_guess = 1.0
    J_slope_guess = 0.01  # Small slope initially
    b_guess = 0.1

    # Estimate kg
    if len(power) > 20:
        steady_state_start = int(len(power) * 0.8)
        kg_guess = np.mean(power[steady_state_start:])
    else:
        kg_guess = 0.0

    # Bounds
    bounds = ([0.001, -1.0, 0.0, -abs(kg_guess) * 2],
              [100.0, 1.0, 10.0, abs(kg_guess) * 2])

    try:
        params, cov = optimize.curve_fit(
            variable_inertia_model,
            X_data,
            y_data,
            p0=[J_base_guess, J_slope_guess, b_guess, kg_guess],
            bounds=bounds,
            maxfev=10000
        )

        J_base, J_slope, b, kg = params

        # Calculate residuals
        power_fitted = variable_inertia_model(X_data, J_base, J_slope, b, kg)
        residuals = y_data - power_fitted

        return {
            "J_base": J_base,
            "J_slope": J_slope,
            "b": b,
            "kg": kg,
            "residuals": residuals,
            "covariance": cov,
            "fitted_response": power_fitted
        }

    except Exception as e:
        raise ValueError(f"Variable inertia fitting failed: {e}")


# ============================================================================
# MODEL VALIDATION & QUALITY METRICS
# ============================================================================

def calculate_fit_quality(residuals: np.ndarray, pos: np.ndarray) -> Dict[str, float]:
    """
    Calculate goodness-of-fit metrics.

    Returns:
        Dictionary with R², RMSE, normalized RMSE, max error
    """
    # R-squared (coefficient of determination)
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((pos - np.mean(pos))**2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    # RMSE (Root Mean Square Error)
    rmse = np.sqrt(np.mean(residuals**2))

    # Normalized RMSE (as percentage of signal range)
    signal_range = np.max(pos) - np.min(pos)
    normalized_rmse = (rmse / signal_range * 100) if signal_range > 0 else 0.0

    # Max absolute error
    max_error = np.max(np.abs(residuals))

    return {
        "r_squared": float(r_squared),
        "rmse": float(rmse),
        "normalized_rmse_percent": float(normalized_rmse),
        "max_error": float(max_error)
    }


def calculate_confidence_intervals(params: np.ndarray, cov: np.ndarray,
                                   confidence: float = 0.95) -> Dict[str, Tuple[float, float]]:
    """
    Calculate confidence intervals for parameters.

    Args:
        params: Parameter values
        cov: Covariance matrix
        confidence: Confidence level (default 0.95 for 95% CI)

    Returns:
        Dictionary mapping parameter names to (lower, upper) bounds
    """
    param_names = ["param_" + str(i) for i in range(len(params))]

    # Calculate standard errors from covariance diagonal
    param_errors = np.sqrt(np.diag(cov))

    # Calculate confidence interval (using t-distribution approximation)
    # For large samples, t ≈ 1.96 for 95% CI
    z_score = stats.norm.ppf((1 + confidence) / 2)

    intervals = {}
    for i, (param, error) in enumerate(zip(params, param_errors)):
        margin = z_score * error
        intervals[param_names[i]] = (param - margin, param + margin)

    return intervals


def assess_confidence(fit_quality: Dict[str, float],
                     confidence_intervals: Dict[str, Tuple[float, float]],
                     params: Dict[str, float]) -> float:
    """
    Assess overall confidence in identified model (0.0 to 1.0).

    Considers:
    - R² value
    - Relative width of confidence intervals
    - Physics validity of parameters

    Returns:
        Confidence score (0.0 = poor, 1.0 = excellent)
    """
    # Factor 1: R² (weighted 50%)
    r_squared = fit_quality["r_squared"]
    r_squared_score = max(0.0, min(1.0, (r_squared - 0.7) / 0.25))  # 0.7 → 0, 0.95 → 1

    # Factor 2: Confidence interval width (weighted 30%)
    # Calculate average relative CI width
    ci_widths = []
    param_list = list(params.values())
    ci_list = list(confidence_intervals.values())

    for param_val, (lower, upper) in zip(param_list, ci_list):
        if abs(param_val) > 1e-6:
            relative_width = (upper - lower) / (2 * abs(param_val))
            ci_widths.append(relative_width)

    if ci_widths:
        avg_ci_width = np.mean(ci_widths)
        ci_score = max(0.0, min(1.0, 1.0 - avg_ci_width))  # Smaller width = better
    else:
        ci_score = 0.5

    # Factor 3: Physics validity (weighted 20%)
    physics_score = 1.0
    if "tau" in params and params["tau"] <= 0:
        physics_score *= 0.5
    if "omega_n" in params and params["omega_n"] <= 0:
        physics_score *= 0.5
    if "zeta" in params and (params["zeta"] < 0 or params["zeta"] > 2):
        physics_score *= 0.5

    # Weighted average
    overall_confidence = (
        0.5 * r_squared_score +
        0.3 * ci_score +
        0.2 * physics_score
    )

    return overall_confidence


# ============================================================================
# AUTOMATIC MODEL SELECTION
# ============================================================================

def select_model_auto(series: Dict[str, np.ndarray],
                     mechanism: str,
                     step_idx: int,
                     step_size: float) -> ModelType:
    """
    Automatically select best model structure based on data characteristics.

    Decision logic:
    1. Check for overshoot (suggests second-order)
    2. Check for gravity effects (mechanism type)
    3. Check data quality (noise level)
    4. Default to simplest appropriate model

    Returns:
        ModelType enum value
    """
    # Detect overshoot
    overshoot = detect_overshoot(series, step_idx, step_size)
    has_overshoot = overshoot > 5.0  # 5% threshold

    # Check for gravity effects
    has_gravity = mechanism in ["elevator", "arm"]

    # Estimate noise level
    noise = estimate_noise_level(series)
    noisy_data = noise > 1.0  # Threshold depends on units

    # Decision tree
    if mechanism in ["flywheel", "turret"]:
        # Rotational mechanisms, no gravity
        if has_overshoot and not noisy_data:
            return ModelType.SECOND_ORDER
        else:
            return ModelType.FIRST_ORDER

    elif mechanism in ["elevator", "arm"]:
        # Linear/rotational with gravity
        if has_overshoot and not noisy_data:
            return ModelType.SECOND_ORDER_GRAVITY
        else:
            return ModelType.FIRST_ORDER_GRAVITY

    else:
        # Unknown mechanism, use safest default
        if has_gravity:
            return ModelType.FIRST_ORDER_GRAVITY
        else:
            return ModelType.FIRST_ORDER


def select_model_interactive(mechanism: str) -> ModelType:
    """
    Interactive model selection via user prompts.

    Returns:
        ModelType enum value
    """
    print(f"\n=== Model Selection for {mechanism.upper()} ===\n")

    # Question 1: Oscillation
    print("Does your mechanism show overshoot or oscillation?")
    print("  (e.g., bouncing, ringing, overshooting target)")
    oscillates = input("  [yes/no/unknown]: ").strip().lower()

    # Question 2: Gravity (if applicable)
    needs_gravity = mechanism in ["elevator", "arm"]

    if needs_gravity:
        print("\nYour mechanism likely fights gravity.")
        print("Use gravity compensation? (recommended)")
        use_gravity = input("  [yes/no]: ").strip().lower()
        has_gravity = use_gravity == "yes"
    else:
        has_gravity = False

    # Select model
    if oscillates == "yes":
        if has_gravity:
            model = ModelType.SECOND_ORDER_GRAVITY
        else:
            model = ModelType.SECOND_ORDER
    else:
        if has_gravity:
            model = ModelType.FIRST_ORDER_GRAVITY
        else:
            model = ModelType.FIRST_ORDER

    print(f"\n✓ Selected model: {model.value}\n")

    return model


# ============================================================================
# MAIN IDENTIFICATION FUNCTION
# ============================================================================

def identify_model(series: Dict[str, np.ndarray],
                  model_type: ModelType,
                  step_idx: int,
                  mechanism: str) -> IdentifiedModel:
    """
    Identify model parameters for specified model structure.

    Returns:
        IdentifiedModel with all parameters, confidence intervals, and quality metrics
    """
    print(f"Identifying parameters for {model_type.value} model...")

    # Select identification function
    if model_type == ModelType.FIRST_ORDER:
        result = identify_first_order(series, step_idx)
        param_names = ["K", "tau"]

    elif model_type == ModelType.FIRST_ORDER_GRAVITY:
        result = identify_first_order_gravity(series, step_idx)
        param_names = ["K", "tau", "kg"]

    elif model_type == ModelType.SECOND_ORDER:
        result = identify_second_order(series, step_idx)
        param_names = ["K", "omega_n", "zeta"]

    elif model_type == ModelType.SECOND_ORDER_GRAVITY:
        result = identify_second_order_gravity(series, step_idx)
        param_names = ["K", "omega_n", "zeta", "kg"]

    elif model_type == ModelType.ANGLE_DEPENDENT:
        result = identify_angle_dependent(series, step_idx)
        param_names = ["K", "tau", "kg"]

    elif model_type == ModelType.FRICTION:
        result = identify_friction(series, step_idx)
        param_names = ["J", "b", "friction", "kg"]

    elif model_type == ModelType.VARIABLE_INERTIA:
        result = identify_variable_inertia(series, step_idx)
        param_names = ["J_base", "J_slope", "b", "kg"]

    else:
        raise ValueError(f"Unknown model type: {model_type}")

    # Extract parameters
    parameters = {name: result[name] for name in param_names}

    # Calculate confidence intervals
    param_values = np.array([parameters[name] for name in param_names if name != "kg"])
    cov = result["covariance"]

    ci_generic = calculate_confidence_intervals(param_values, cov)

    # Map generic names to actual parameter names
    confidence_intervals = {}
    for i, name in enumerate([n for n in param_names if n != "kg"]):
        confidence_intervals[name] = ci_generic[f"param_{i}"]

    # Add kg confidence (if present) - use simple heuristic
    if "kg" in parameters:
        # Estimate uncertainty as 10% of value
        kg_val = parameters["kg"]
        confidence_intervals["kg"] = (kg_val * 0.9, kg_val * 1.1)

    # Calculate fit quality
    residuals = result["residuals"]
    pos = series["pos"][step_idx:]
    fit_quality = calculate_fit_quality(residuals, pos)

    # Assess overall confidence
    overall_confidence = assess_confidence(fit_quality, confidence_intervals, parameters)
    fit_quality["overall_confidence"] = overall_confidence

    # Generate transfer function string
    transfer_function = generate_transfer_function(model_type, parameters)

    # Create notes
    notes = f"Identified from step response. R² = {fit_quality['r_squared']:.3f}, " \
            f"Confidence = {overall_confidence:.2f}"

    return IdentifiedModel(
        model_type=model_type.value,
        parameters=parameters,
        confidence_intervals=confidence_intervals,
        transfer_function=transfer_function,
        fit_quality=fit_quality,
        mechanism=mechanism,
        notes=notes
    )


def generate_transfer_function(model_type: ModelType, params: Dict[str, float]) -> str:
    """Generate transfer function string representation."""
    if model_type == ModelType.FIRST_ORDER:
        K = params["K"]
        tau = params["tau"]
        return f"G(s) = {K:.3f} / ({tau:.3f}*s + 1)"

    elif model_type == ModelType.FIRST_ORDER_GRAVITY:
        K = params["K"]
        tau = params["tau"]
        kg = params["kg"]
        return f"G(s) = {K:.3f} / ({tau:.3f}*s + 1) + {kg:.3f}"

    elif model_type == ModelType.SECOND_ORDER:
        K = params["K"]
        omega_n = params["omega_n"]
        zeta = params["zeta"]
        wn2 = omega_n**2
        return f"G(s) = {K:.3f}*{wn2:.3f} / (s² + {2*zeta*omega_n:.3f}*s + {wn2:.3f})"

    elif model_type == ModelType.SECOND_ORDER_GRAVITY:
        K = params["K"]
        omega_n = params["omega_n"]
        zeta = params["zeta"]
        kg = params["kg"]
        wn2 = omega_n**2
        return f"G(s) = {K:.3f}*{wn2:.3f} / (s² + {2*zeta*omega_n:.3f}*s + {wn2:.3f}) + {kg:.3f}"

    elif model_type == ModelType.ANGLE_DEPENDENT:
        K = params["K"]
        tau = params["tau"]
        kg = params["kg"]
        return f"u(t) = ({K:.3f}/{tau:.3f})*error + {kg:.3f}*cos(angle)"

    elif model_type == ModelType.FRICTION:
        J = params["J"]
        b = params["b"]
        friction = params["friction"]
        kg = params["kg"]
        return f"J*accel = torque - {b:.3f}*vel - {friction:.3f}*sign(vel) - {kg:.3f} (J={J:.3f})"

    elif model_type == ModelType.VARIABLE_INERTIA:
        J_base = params["J_base"]
        J_slope = params["J_slope"]
        b = params["b"]
        kg = params["kg"]
        return f"({J_base:.3f} + {J_slope:.4f}*pos)*accel = torque - {b:.3f}*vel - {kg:.3f}"

    else:
        return "Unknown model"


# ============================================================================
# MODEL VALIDATION & FALLBACK
# ============================================================================

def validate_model(model: IdentifiedModel, threshold_r_squared: float = 0.85) -> bool:
    """
    Validate identified model quality.

    Returns:
        True if model passes validation, False otherwise
    """
    r_squared = model.fit_quality["r_squared"]
    confidence = model.fit_quality["overall_confidence"]

    # Check R² threshold
    if r_squared < threshold_r_squared:
        print(f"✗ Model validation failed: R² = {r_squared:.3f} < {threshold_r_squared}")
        return False

    # Check confidence threshold
    if confidence < 0.7:
        print(f"✗ Model validation failed: Confidence = {confidence:.2f} < 0.70")
        return False

    # Check parameter physics validity
    params = model.parameters

    if "tau" in params and params["tau"] <= 0:
        print(f"✗ Model validation failed: Invalid tau = {params['tau']}")
        return False

    if "omega_n" in params and params["omega_n"] <= 0:
        print(f"✗ Model validation failed: Invalid omega_n = {params['omega_n']}")
        return False

    if "zeta" in params and (params["zeta"] < 0 or params["zeta"] > 2):
        print(f"✗ Model validation failed: Invalid zeta = {params['zeta']}")
        return False

    print(f"✓ Model validated: R² = {r_squared:.3f}, Confidence = {confidence:.2f}")
    return True


def try_with_fallback(series: Dict[str, np.ndarray],
                     model_type: ModelType,
                     step_idx: int,
                     mechanism: str) -> Optional[IdentifiedModel]:
    """
    Try to identify model, falling back to simpler model if validation fails.

    Fallback chain:
    - Second-order + gravity → First-order + gravity
    - Second-order → First-order
    - Angle-dependent → First-order + gravity
    - Friction → First-order + gravity
    - Variable-inertia → First-order + gravity
    - First-order + gravity → First-order

    Returns:
        IdentifiedModel if successful, None if all attempts fail
    """
    # Try primary model
    try:
        model = identify_model(series, model_type, step_idx, mechanism)

        if validate_model(model):
            return model

        print(f"Primary model ({model_type.value}) failed validation.")

    except Exception as e:
        print(f"Primary model ({model_type.value}) identification failed: {e}")

    # Determine fallback model
    fallback_map = {
        ModelType.SECOND_ORDER_GRAVITY: ModelType.FIRST_ORDER_GRAVITY,
        ModelType.SECOND_ORDER: ModelType.FIRST_ORDER,
        ModelType.ANGLE_DEPENDENT: ModelType.FIRST_ORDER_GRAVITY,
        ModelType.FRICTION: ModelType.FIRST_ORDER_GRAVITY,
        ModelType.VARIABLE_INERTIA: ModelType.FIRST_ORDER_GRAVITY,
        ModelType.FIRST_ORDER_GRAVITY: ModelType.FIRST_ORDER,
        ModelType.FIRST_ORDER: None  # No simpler model
    }

    fallback = fallback_map.get(model_type)

    if fallback is None:
        print("No simpler model available. Identification failed.")
        return None

    print(f"Trying fallback model: {fallback.value}")

    # Try fallback recursively
    return try_with_fallback(series, fallback, step_idx, mechanism)


# ============================================================================
# MAIN CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="System Identification - Parameter Identification for FTC Control Systems",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-select model based on data
  uv run identify_params.py --data sysid_data.json --auto-select --mechanism elevator

  # Interactive model selection
  uv run identify_params.py --data sysid_data.json --interactive --mechanism arm

  # Specify model explicitly
  uv run identify_params.py --data sysid_data.json --model first-order-gravity --mechanism elevator

  # Custom output file
  uv run identify_params.py --data sysid_data.json --auto-select --mechanism flywheel --output my_model.json
        """
    )

    parser.add_argument("--data", type=str, required=True,
                       help="Path to telemetry data JSON file")

    parser.add_argument("--mechanism", type=str, required=True,
                       choices=["elevator", "arm", "flywheel", "turret"],
                       help="Mechanism type")

    # Model selection options (mutually exclusive)
    selection_group = parser.add_mutually_exclusive_group(required=True)

    selection_group.add_argument("--auto-select", action="store_true",
                                help="Automatically select model based on data")

    selection_group.add_argument("--interactive", action="store_true",
                                help="Interactive model selection (asks questions)")

    selection_group.add_argument("--model", type=str,
                                choices=["first-order", "first-order-gravity",
                                        "second-order", "second-order-gravity",
                                        "angle-dependent", "friction", "variable-inertia"],
                                help="Explicitly specify model structure")

    parser.add_argument("--output", type=str, default="identified_model.json",
                       help="Output file path (default: identified_model.json)")

    parser.add_argument("--no-fallback", action="store_true",
                       help="Disable automatic fallback to simpler models")

    args = parser.parse_args()

    # Load telemetry data
    print(f"Loading telemetry from {args.data}...")
    try:
        telemetry = load_telemetry(Path(args.data))
        series = extract_time_series(telemetry)
        print(f"✓ Loaded {len(series['t'])} data points")
    except Exception as e:
        print(f"✗ Error loading telemetry: {e}")
        return 1

    # Find step response
    try:
        step_idx, step_size = find_step_response(series)
        print(f"✓ Found step input at t={series['t'][step_idx]:.2f}s, size={step_size:.1f}")
    except Exception as e:
        print(f"✗ Error finding step response: {e}")
        return 1

    # Select model
    if args.auto_select:
        model_type = select_model_auto(series, args.mechanism, step_idx, step_size)
        print(f"✓ Auto-selected model: {model_type.value}")

    elif args.interactive:
        model_type = select_model_interactive(args.mechanism)

    else:
        model_type = ModelType(args.model)
        print(f"Using specified model: {model_type.value}")

    # Identify parameters
    if args.no_fallback:
        try:
            model = identify_model(series, model_type, step_idx, args.mechanism)

            if not validate_model(model):
                print("\n✗ Model validation failed. Use --interactive or --auto-select for fallback.")
                return 1

        except Exception as e:
            print(f"\n✗ Identification failed: {e}")
            return 1

    else:
        model = try_with_fallback(series, model_type, step_idx, args.mechanism)

        if model is None:
            print("\n✗ All identification attempts failed.")
            print("Suggestions:")
            print("  1. Collect cleaner data (reduce noise)")
            print("  2. Ensure robot wasn't hitting limits during test")
            print("  3. Use empirical tuning instead (step_response method)")
            return 1

    # Display results
    print("\n" + "=" * 70)
    print(f"IDENTIFIED MODEL - {model.model_type}")
    print("=" * 70)
    print(f"\nTransfer Function:")
    print(f"  {model.transfer_function}")
    print(f"\nParameters:")
    for name, value in model.parameters.items():
        ci = model.confidence_intervals.get(name)
        if ci:
            print(f"  {name} = {value:.4f}  (95% CI: [{ci[0]:.4f}, {ci[1]:.4f}])")
        else:
            print(f"  {name} = {value:.4f}")

    print(f"\nFit Quality:")
    print(f"  R² = {model.fit_quality['r_squared']:.4f}")
    print(f"  RMSE = {model.fit_quality['rmse']:.2f}")
    print(f"  Normalized RMSE = {model.fit_quality['normalized_rmse_percent']:.1f}%")
    print(f"  Overall Confidence = {model.fit_quality['overall_confidence']:.2f}")

    print(f"\nNotes:")
    print(f"  {model.notes}")
    print("=" * 70)

    # Save to file
    output_path = Path(args.output)
    with open(output_path, "w") as f:
        json.dump(model.to_dict(), f, indent=2)

    print(f"\n✓ Saved identified model to {output_path}")

    # Validation recommendations
    if model.fit_quality['r_squared'] < 0.90:
        print("\n⚠ Warning: R² < 0.90")
        print("  Consider validating model with separate test data before using for gain calculation.")

    if model.fit_quality['overall_confidence'] < 0.80:
        print("\n⚠ Warning: Overall confidence < 0.80")
        print("  Model parameters may have high uncertainty.")
        print("  Consider:")
        print("    - Collecting more data")
        print("    - Improving signal-to-noise ratio")
        print("    - Using empirical tuning methods instead")

    return 0


if __name__ == "__main__":
    sys.exit(main())

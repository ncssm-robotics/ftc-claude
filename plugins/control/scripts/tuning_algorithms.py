#!/usr/bin/env python3
"""
PID Tuning Algorithms for FTC Controllers

Implements multiple tuning methods:
1. Step Response Analysis (basic, safe)
2. Ziegler-Nichols Tuning Rules
3. Relay Feedback Test (automated Ku/Tu finding)
4. Optimization (scipy-based numerical optimization)

Usage:
    uv run tuning_algorithms.py step_response telemetry.json --mechanism elevator
    uv run tuning_algorithms.py ziegler_nichols --ku 0.01 --tu 0.5
    uv run tuning_algorithms.py relay_feedback telemetry.json
    uv run tuning_algorithms.py optimize telemetry.json --mechanism elevator
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
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass

import numpy as np
from scipy import signal, optimize


@dataclass
class TuningResult:
    """Container for tuning results."""
    kP: float
    kI: float = 0.0
    kD: float = 0.0
    kG: float = 0.0  # Feedforward (gravity or velocity)
    method: str = ""
    confidence: str = ""  # LOW, MEDIUM, HIGH
    notes: str = ""


def load_telemetry(file_path: Path) -> Dict[str, Any]:
    """Load telemetry data from JSON file."""
    with open(file_path) as f:
        return json.load(f)


def extract_time_series(telemetry: Dict[str, Any]) -> Dict[str, np.ndarray]:
    """Extract numpy arrays from telemetry data."""
    data = telemetry.get("data", [])

    # Common fields
    t = np.array([d.get("t", 0) for d in data])
    pos = np.array([d.get("pos", 0) for d in data])
    vel = np.array([d.get("vel", 0) for d in data])
    target = np.array([d.get("target", 0) for d in data])
    error = np.array([d.get("error", 0) for d in data])
    power = np.array([d.get("power", 0) for d in data])

    return {
        "t": t,
        "pos": pos,
        "vel": vel,
        "target": target,
        "error": error,
        "power": power
    }


# ============================================================================
# STEP RESPONSE ANALYSIS (Basic, Safe)
# ============================================================================

def analyze_step_response(telemetry_file: Path, mechanism: str) -> TuningResult:
    """
    Analyze step response to calculate conservative PID gains.

    This method is SAFE and will not cause oscillation.
    It intentionally produces conservative (under-tuned) gains.

    Process:
    1. Identify step input (target change)
    2. Measure rise time, overshoot, settling time
    3. Calculate conservative gains based on response characteristics
    """
    telemetry = load_telemetry(telemetry_file)
    series = extract_time_series(telemetry)

    t = series["t"]
    pos = series["pos"]
    target = series["target"]
    error = series["error"]

    # Find step input (target change)
    target_changes = np.diff(target)
    step_idx = np.where(np.abs(target_changes) > 10)[0]

    if len(step_idx) == 0:
        return TuningResult(
            kP=0.001, kI=0.0, kD=0.0, kG=0.0,
            method="step_response",
            confidence="LOW",
            notes="No clear step input detected in telemetry"
        )

    # Use first major step
    step_start = step_idx[0]
    step_target = target[step_start + 1]
    step_initial = pos[step_start]

    # Extract response after step
    response_t = t[step_start:]
    response_pos = pos[step_start:]
    response_error = error[step_start:]

    # Calculate response characteristics
    final_value = response_pos[-1]
    step_size = step_target - step_initial

    # Rise time (10% to 90% of final value)
    rise_90_thresh = step_initial + 0.9 * step_size
    rise_10_thresh = step_initial + 0.1 * step_size

    rise_10_idx = np.where(response_pos >= rise_10_thresh)[0]
    rise_90_idx = np.where(response_pos >= rise_90_thresh)[0]

    if len(rise_10_idx) > 0 and len(rise_90_idx) > 0:
        rise_time = response_t[rise_90_idx[0]] - response_t[rise_10_idx[0]]
    else:
        rise_time = 1.0  # Default fallback

    # Overshoot
    if step_size > 0:
        max_pos = np.max(response_pos)
        overshoot_pct = (max_pos - final_value) / step_size * 100
    else:
        max_pos = np.min(response_pos)
        overshoot_pct = (final_value - max_pos) / abs(step_size) * 100

    # Steady-state error
    steady_state_error = abs(response_error[-10:].mean())

    # Calculate gains (conservative formulas)
    # kP: Based on rise time (slower rise time = lower kP)
    kP = 0.8 / (rise_time * abs(step_size))  # Conservative coefficient

    # kD: Add damping if there's overshoot
    if overshoot_pct > 5:
        kD = kP * rise_time / 10  # Add damping
    else:
        kD = 0.0

    # kG (feedforward): For mechanisms with gravity/velocity
    if mechanism in ["elevator", "arm"]:
        # Estimate gravity compensation from steady-state power
        avg_power = response_pos[-20:].mean() if len(response_pos) > 20 else 0
        kG = abs(avg_power) if abs(avg_power) > 0.01 else 0.0
    else:
        kG = 0.0

    # Confidence based on data quality
    if len(response_pos) > 50 and abs(overshoot_pct) < 20:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"

    notes = f"Rise time: {rise_time:.2f}s, Overshoot: {overshoot_pct:.1f}%, SS Error: {steady_state_error:.1f}"

    return TuningResult(
        kP=round(kP, 5),
        kI=0.0,  # Intentionally conservative (no I gain initially)
        kD=round(kD, 5),
        kG=round(kG, 3),
        method="step_response",
        confidence=confidence,
        notes=notes
    )


# ============================================================================
# ZIEGLER-NICHOLS TUNING RULES
# ============================================================================

def ziegler_nichols(ku: float, tu: float, rule: str = "classic") -> TuningResult:
    """
    Apply Ziegler-Nichols tuning rules given critical gain (Ku) and period (Tu).

    Rules:
    - classic: Original Z-N (can be aggressive)
    - no_overshoot: Reduced overshoot variant
    - pessen: Pessen integral rule (faster response)
    """
    rules = {
        "classic": {
            "kP": 0.6 * ku,
            "kI": 1.2 * ku / tu,
            "kD": 0.075 * ku * tu
        },
        "no_overshoot": {
            "kP": 0.2 * ku,
            "kI": 0.4 * ku / tu,
            "kD": 0.066 * ku * tu
        },
        "pessen": {
            "kP": 0.7 * ku,
            "kI": 1.75 * ku / tu,
            "kD": 0.105 * ku * tu
        }
    }

    if rule not in rules:
        raise ValueError(f"Unknown rule: {rule}. Use: classic, no_overshoot, pessen")

    gains = rules[rule]

    return TuningResult(
        kP=round(gains["kP"], 5),
        kI=round(gains["kI"], 5),
        kD=round(gains["kD"], 5),
        kG=0.0,  # Feedforward must be tuned separately
        method=f"ziegler_nichols_{rule}",
        confidence="MEDIUM",
        notes=f"Ku={ku}, Tu={tu}, Rule={rule}"
    )


# ============================================================================
# RELAY FEEDBACK TEST (Automated Ku/Tu Finding)
# ============================================================================

def relay_feedback_test(telemetry_file: Path) -> Tuple[float, float]:
    """
    Extract critical gain (Ku) and period (Tu) from relay feedback test data.

    Relay feedback: Bang-bang control until stable oscillation.
    Ku = (4 * relay_amplitude) / (π * oscillation_amplitude)
    Tu = oscillation_period
    """
    telemetry = load_telemetry(telemetry_file)
    series = extract_time_series(telemetry)

    t = series["t"]
    pos = series["pos"]
    power = series["power"]

    # Find oscillation peaks
    from scipy.signal import find_peaks

    peaks, _ = find_peaks(pos, distance=10)
    valleys, _ = find_peaks(-pos, distance=10)

    if len(peaks) < 2 or len(valleys) < 2:
        raise ValueError("Not enough oscillations detected in telemetry")

    # Calculate oscillation amplitude (peak-to-valley)
    peak_values = pos[peaks]
    valley_values = pos[valleys]
    oscillation_amplitude = (peak_values.mean() - valley_values.mean()) / 2

    # Calculate oscillation period (average time between peaks)
    peak_times = t[peaks]
    periods = np.diff(peak_times)
    Tu = periods.mean()

    # Calculate relay amplitude (bang-bang control output)
    relay_amplitude = abs(power.max() - power.min()) / 2

    # Calculate critical gain
    Ku = (4 * relay_amplitude) / (np.pi * oscillation_amplitude)

    print(f"Relay feedback results:")
    print(f"  Oscillation amplitude: {oscillation_amplitude:.1f} ticks")
    print(f"  Oscillation period (Tu): {Tu:.3f} seconds")
    print(f"  Critical gain (Ku): {Ku:.5f}")

    return Ku, Tu


def analyze_relay_feedback(telemetry_file: Path, rule: str = "no_overshoot") -> TuningResult:
    """Perform relay feedback test and apply Ziegler-Nichols."""
    try:
        Ku, Tu = relay_feedback_test(telemetry_file)
        result = ziegler_nichols(Ku, Tu, rule)
        result.method = "relay_feedback"
        result.confidence = "HIGH"
        return result
    except Exception as e:
        return TuningResult(
            kP=0.001, kI=0.0, kD=0.0, kG=0.0,
            method="relay_feedback",
            confidence="LOW",
            notes=f"Error: {e}"
        )


# ============================================================================
# OPTIMIZATION (scipy-based)
# ============================================================================

def simulate_pid_response(gains: Tuple[float, float, float],
                         target: float,
                         initial_pos: float,
                         dt: float = 0.02,
                         duration: float = 5.0) -> np.ndarray:
    """
    Simulate PID controller response.

    Simple discrete PID simulation for optimization.
    """
    kP, kI, kD = gains

    steps = int(duration / dt)
    pos = np.zeros(steps)
    pos[0] = initial_pos

    integral = 0
    prev_error = target - initial_pos

    for i in range(1, steps):
        error = target - pos[i-1]
        integral += error * dt
        derivative = (error - prev_error) / dt

        control = kP * error + kI * integral + kD * derivative

        # Simple motor model (first-order system)
        tau = 0.1  # Time constant
        pos[i] = pos[i-1] + (control - pos[i-1]) * dt / tau

        prev_error = error

    return pos


def optimize_gains(telemetry_file: Path, mechanism: str, metric: str = "iae") -> TuningResult:
    """
    Optimize PID gains using numerical optimization.

    Metrics:
    - iae: Integral of Absolute Error (balance speed and accuracy)
    - ise: Integral of Squared Error (penalize large errors)
    - itae: Integral of Time-weighted Absolute Error (penalize settling time)
    """
    telemetry = load_telemetry(telemetry_file)
    series = extract_time_series(telemetry)

    t = series["t"]
    pos = series["pos"]
    target = series["target"]
    error = series["error"]

    # Find step response
    target_changes = np.diff(target)
    step_idx = np.where(np.abs(target_changes) > 10)[0]

    if len(step_idx) == 0:
        return TuningResult(
            kP=0.001, kI=0.0, kD=0.0, kG=0.0,
            method="optimize",
            confidence="LOW",
            notes="No step input detected"
        )

    step_start = step_idx[0]
    step_target = target[step_start + 1]

    # Extract response
    response_t = t[step_start:]
    response_pos = pos[step_start:]
    response_error = error[step_start:]

    # Define cost function
    def cost_function(gains):
        kP, kD = gains
        kI = 0  # Start without I gain

        # Simulate response
        sim_pos = simulate_pid_response(
            (kP, kI, kD),
            step_target,
            response_pos[0],
            dt=0.02,
            duration=min(5.0, response_t[-1] - response_t[0])
        )

        # Calculate error metric
        sim_error = step_target - sim_pos

        if metric == "iae":
            cost = np.sum(np.abs(sim_error))
        elif metric == "ise":
            cost = np.sum(sim_error ** 2)
        elif metric == "itae":
            t_sim = np.arange(len(sim_error)) * 0.02
            cost = np.sum(t_sim * np.abs(sim_error))
        else:
            cost = np.sum(np.abs(sim_error))

        # Add penalty for overshoot
        overshoot = np.max(sim_pos) - step_target
        if overshoot > 0:
            cost += overshoot * 100

        return cost

    # Initial guess (from step response)
    step_result = analyze_step_response(telemetry_file, mechanism)
    initial_guess = [step_result.kP, step_result.kD]

    # Optimize
    print("Optimizing gains...")
    result = optimize.minimize(
        cost_function,
        initial_guess,
        method="Nelder-Mead",
        options={"maxiter": 100}
    )

    kP_opt, kD_opt = result.x

    return TuningResult(
        kP=round(kP_opt, 5),
        kI=0.0,
        kD=round(kD_opt, 5),
        kG=step_result.kG,  # Use feedforward from step response
        method="optimize",
        confidence="HIGH" if result.success else "MEDIUM",
        notes=f"Metric: {metric}, Iterations: {result.nit}"
    )


# ============================================================================
# MAIN CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="PID Tuning Algorithms for FTC Controllers"
    )
    subparsers = parser.add_subparsers(dest="algorithm", help="Tuning algorithm")

    # Step response
    step_parser = subparsers.add_parser("step_response", help="Step response analysis (safe, conservative)")
    step_parser.add_argument("telemetry", type=str, help="Telemetry JSON file")
    step_parser.add_argument("--mechanism", choices=["elevator", "arm", "flywheel", "turret"],
                            default="elevator", help="Mechanism type")

    # Ziegler-Nichols
    zn_parser = subparsers.add_parser("ziegler_nichols", help="Ziegler-Nichols tuning rules")
    zn_parser.add_argument("--ku", type=float, required=True, help="Critical gain (Ku)")
    zn_parser.add_argument("--tu", type=float, required=True, help="Critical period (Tu)")
    zn_parser.add_argument("--rule", choices=["classic", "no_overshoot", "pessen"],
                          default="no_overshoot", help="Z-N variant")

    # Relay feedback
    relay_parser = subparsers.add_parser("relay_feedback", help="Relay feedback test (automated Ku/Tu)")
    relay_parser.add_argument("telemetry", type=str, help="Telemetry JSON file from relay test")
    relay_parser.add_argument("--rule", choices=["classic", "no_overshoot", "pessen"],
                             default="no_overshoot", help="Z-N variant")

    # Optimization
    opt_parser = subparsers.add_parser("optimize", help="Numerical optimization (scipy)")
    opt_parser.add_argument("telemetry", type=str, help="Telemetry JSON file")
    opt_parser.add_argument("--mechanism", choices=["elevator", "arm", "flywheel", "turret"],
                           default="elevator", help="Mechanism type")
    opt_parser.add_argument("--metric", choices=["iae", "ise", "itae"],
                           default="iae", help="Error metric to minimize")

    args = parser.parse_args()

    if not args.algorithm:
        parser.print_help()
        return 1

    # Execute algorithm
    if args.algorithm == "step_response":
        result = analyze_step_response(Path(args.telemetry), args.mechanism)

    elif args.algorithm == "ziegler_nichols":
        result = ziegler_nichols(args.ku, args.tu, args.rule)

    elif args.algorithm == "relay_feedback":
        result = analyze_relay_feedback(Path(args.telemetry), args.rule)

    elif args.algorithm == "optimize":
        result = optimize_gains(Path(args.telemetry), args.mechanism, args.metric)

    else:
        print(f"Unknown algorithm: {args.algorithm}")
        return 1

    # Display results
    print()
    print("=" * 60)
    print(f"TUNING RESULTS - {result.method}")
    print("=" * 60)
    print(f"kP = {result.kP}")
    print(f"kI = {result.kI}")
    print(f"kD = {result.kD}")
    if result.kG > 0:
        print(f"kG = {result.kG} (feedforward)")
    print()
    print(f"Confidence: {result.confidence}")
    print(f"Notes: {result.notes}")
    print("=" * 60)

    # Save to file
    output = {
        "kP": result.kP,
        "kI": result.kI,
        "kD": result.kD,
        "kG": result.kG,
        "method": result.method,
        "confidence": result.confidence,
        "notes": result.notes
    }

    output_file = Path("tuning_result.json")
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n✓ Saved results to {output_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

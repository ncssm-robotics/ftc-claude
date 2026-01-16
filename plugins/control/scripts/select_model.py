#!/usr/bin/env python3
"""
Model Selection for System Identification

Intelligently selects the appropriate model structure for system identification
based on mechanism type and user knowledge. Supports 6 model structures from
simple first-order to complex variable-inertia models.

Model Library:
1. first-order: G(s) = K/(τs + 1) - Baseline for velocity control
2. first-order-gravity: u = K/τ * error + kg - FTC elevator/arm default
3. second-order: G(s) = K*ωn²/(s² + 2ζωn*s + ωn²) - Oscillatory systems
4. angle-dependent: u = K/τ * error + kg*cos(θ) - Arms with known angle
5. friction: J*a = τ - b*v - f*sign(v) - Sticking mechanisms
6. variable-inertia: J(pos)*a = τ - b*v - kg - Telescoping mechanisms

Usage:
    # Interactive mode (asks questions)
    uv run select_model.py --mechanism elevator

    # With known characteristics
    uv run select_model.py --mechanism elevator --cable-driven yes --load-varies no

    # Quick selection (no questions, use defaults)
    uv run select_model.py --mechanism flywheel --quick

    # Output to file
    uv run select_model.py --mechanism arm --output selected_model.json
"""

# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "numpy",
# ]
# ///

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum


class ModelType(Enum):
    """Available model structures."""
    FIRST_ORDER = "first-order"
    FIRST_ORDER_GRAVITY = "first-order-gravity"
    SECOND_ORDER = "second-order"
    ANGLE_DEPENDENT = "angle-dependent"
    FRICTION = "friction"
    VARIABLE_INERTIA = "variable-inertia"


@dataclass
class ModelStructure:
    """Model structure specification."""
    model_type: str
    parameters: List[str]
    equation: str
    transfer_function: Optional[str]
    num_parameters: int
    complexity: str  # "simple", "moderate", "complex"
    description: str
    use_cases: List[str]
    advantages: List[str]
    limitations: List[str]


# ============================================================================
# MODEL LIBRARY DEFINITIONS
# ============================================================================

MODEL_LIBRARY: Dict[str, ModelStructure] = {
    "first-order": ModelStructure(
        model_type="first-order",
        parameters=["K", "tau"],
        equation="G(s) = K / (τs + 1)",
        transfer_function="K / (tau*s + 1)",
        num_parameters=2,
        complexity="simple",
        description="First-order system with time constant",
        use_cases=[
            "Flywheel velocity control",
            "Turret position control (no oscillation)",
            "Initial baseline for any mechanism",
            "When no information available"
        ],
        advantages=[
            "Simplest to fit (only 2 parameters)",
            "Rarely fails validation",
            "Good baseline for comparison",
            "Robust to noisy data"
        ],
        limitations=[
            "No gravity compensation",
            "No resonance/overshoot prediction",
            "May underfit complex systems"
        ]
    ),

    "first-order-gravity": ModelStructure(
        model_type="first-order-gravity",
        parameters=["K", "tau", "kg"],
        equation="u(t) = (K/τ) * error + kg",
        transfer_function="K / (tau*s + 1) + kg",
        num_parameters=3,
        complexity="simple",
        description="First-order with constant gravity compensation",
        use_cases=[
            "Elevator with constant load",
            "Arm at fixed angle",
            "Any vertical mechanism",
            "Default for FTC mechanisms"
        ],
        advantages=[
            "Accounts for gravity (critical for FTC)",
            "Still simple (3 parameters)",
            "Works for 80% of FTC mechanisms",
            "Well-understood physics"
        ],
        limitations=[
            "Assumes constant gravity (not angle-dependent)",
            "No oscillation prediction"
        ]
    ),

    "second-order": ModelStructure(
        model_type="second-order",
        parameters=["K", "omega_n", "zeta", "kg"],
        equation="G(s) = K*ωn² / (s² + 2ζωn*s + ωn²)",
        transfer_function="K*omega_n^2 / (s^2 + 2*zeta*omega_n*s + omega_n^2)",
        num_parameters=4,
        complexity="moderate",
        description="Second-order system with damping",
        use_cases=[
            "Cable-driven mechanisms (compliance)",
            "Long arms (structural flex)",
            "Any mechanism showing overshoot",
            "Systems with resonances"
        ],
        advantages=[
            "Predicts overshoot accurately",
            "Captures resonances",
            "Good for compliance/flex",
            "Models oscillatory behavior"
        ],
        limitations=[
            "More parameters (requires cleaner data)",
            "Can overfit with noisy data",
            "Harder to tune"
        ]
    ),

    "angle-dependent": ModelStructure(
        model_type="angle-dependent",
        parameters=["K", "tau", "kg"],
        equation="u(t) = (K/τ) * error + kg * cos(angle)",
        transfer_function="K / (tau*s + 1) + kg*cos(angle)",
        num_parameters=3,
        complexity="moderate",
        description="Angle-dependent gravity compensation for arms",
        use_cases=[
            "Rotating arm mechanisms",
            "Pivoting mechanisms",
            "When encoder-to-angle known"
        ],
        advantages=[
            "Accurate across full range of motion",
            "One set of gains for all angles",
            "Physics-based gravity term",
            "Better than constant kg for arms"
        ],
        limitations=[
            "Requires angle calculation from encoder",
            "More complex data collection (multiple angles)",
            "Need accurate angle formula"
        ]
    ),

    "friction": ModelStructure(
        model_type="friction",
        parameters=["J", "b", "friction", "kg"],
        equation="J * accel = torque - b * vel - friction * sign(vel)",
        transfer_function=None,  # Nonlinear, no simple transfer function
        num_parameters=4,
        complexity="complex",
        description="Inertia-damping model with Coulomb friction",
        use_cases=[
            "Mechanisms with sticking/dead zones",
            "High-friction gearboxes",
            "Asymmetric response (up vs down)",
            "When dead zone evident"
        ],
        advantages=[
            "Most physically accurate",
            "Captures dead zones",
            "Models static/kinetic friction",
            "Handles asymmetry"
        ],
        limitations=[
            "Requires acceleration calculation",
            "4+ parameters (harder to fit)",
            "Needs very clean data",
            "Nonlinear (complex simulation)"
        ]
    ),

    "variable-inertia": ModelStructure(
        model_type="variable-inertia",
        parameters=["J_base", "J_slope", "b", "kg"],
        equation="J(pos) * accel = torque - b * vel - kg",
        transfer_function=None,  # Position-dependent, no simple transfer function
        num_parameters=4,
        complexity="complex",
        description="Variable inertia for extending mechanisms",
        use_cases=[
            "Telescoping elevators",
            "Extending intakes",
            "Load varies during motion",
            "Position-dependent dynamics"
        ],
        advantages=[
            "Handles changing mass/inertia",
            "Accurate for extending mechanisms",
            "Physics-based approach"
        ],
        limitations=[
            "Most complex (position-dependent)",
            "Requires extensive data at multiple positions",
            "Hard to validate",
            "May need per-position fitting"
        ]
    )
}


# ============================================================================
# DECISION TREE FOR MODEL SELECTION
# ============================================================================

def select_model_for_mechanism(
    mechanism: str,
    has_friction: Optional[str] = None,
    has_backlash: Optional[str] = None,
    load_varies: Optional[str] = None,
    cable_driven: Optional[str] = None,
    has_oscillation: Optional[str] = None,
    knows_angle: Optional[str] = None,
    interactive: bool = True
) -> ModelStructure:
    """
    Select appropriate model structure based on mechanism and characteristics.

    Args:
        mechanism: elevator, arm, flywheel, turret
        has_friction: yes/no/unknown - Does it stick or have dead zones?
        has_backlash: yes/no/unknown - Gearbox backlash evident?
        load_varies: yes/no/unknown - Does load change during motion?
        cable_driven: yes/no/unknown - Cable/belt transmission?
        has_oscillation: yes/no/unknown - Bounces or oscillates?
        knows_angle: yes/no/unknown - Can calculate angle from encoder? (arm only)
        interactive: If True, ask questions for unknown values

    Returns:
        ModelStructure object with selected model
    """

    # Interactive mode: ask questions if values unknown
    if interactive:
        if mechanism in ["elevator", "arm"]:
            if cable_driven is None:
                cable_driven = ask_yes_no_unknown(
                    "Is this mechanism cable-driven or belt-driven (vs direct drive)?"
                )

            if has_oscillation is None:
                has_oscillation = ask_yes_no_unknown(
                    "Have you noticed bouncing or oscillation in the motion?"
                )

            if has_friction is None:
                has_friction = ask_yes_no_unknown(
                    "Does it stick or have dead zones (especially near zero velocity)?"
                )

        if mechanism == "elevator":
            if load_varies is None:
                load_varies = ask_yes_no_unknown(
                    "Does the load vary during motion (e.g., telescoping stages)?"
                )

        if mechanism == "arm":
            if knows_angle is None:
                knows_angle = ask_yes_no_unknown(
                    "Can you calculate the arm angle from encoder ticks? (e.g., angle = encoder * 360 / 8192)"
                )

        if mechanism in ["flywheel", "turret"]:
            if has_oscillation is None:
                has_oscillation = ask_yes_no_unknown(
                    "Does it overshoot or oscillate around the target?"
                )

    # Decision tree logic

    # FLYWHEEL / TURRET
    if mechanism in ["flywheel", "turret"]:
        if has_oscillation == "yes":
            print(f"✓ Detected oscillation → Using second-order model")
            return MODEL_LIBRARY["second-order"]
        else:
            print(f"✓ Simple velocity control → Using first-order model")
            return MODEL_LIBRARY["first-order"]

    # ELEVATOR
    elif mechanism == "elevator":
        # Complex models first (most specific)
        if load_varies == "yes":
            print(f"✓ Variable load detected → Using variable-inertia model")
            print(f"  Note: This requires data at multiple positions")
            return MODEL_LIBRARY["variable-inertia"]

        if has_friction == "yes" or has_backlash == "yes":
            print(f"✓ Friction/sticking detected → Using friction model")
            return MODEL_LIBRARY["friction"]

        if cable_driven == "yes" or has_oscillation == "yes":
            print(f"✓ Cable-driven or oscillation detected → Using second-order with gravity")
            model = MODEL_LIBRARY["second-order"]
            return model

        # Default: first-order + gravity (safe for most FTC elevators)
        print(f"✓ Standard elevator → Using first-order-gravity model (safe default)")
        return MODEL_LIBRARY["first-order-gravity"]

    # ARM / PIVOT
    elif mechanism == "arm":
        # Check if user can provide angle calculation
        if knows_angle == "yes":
            print(f"✓ Angle calculation available → Using angle-dependent gravity model")
            print(f"  You will be asked for the encoder-to-angle formula during identification")
            return MODEL_LIBRARY["angle-dependent"]

        # Similar logic to elevator for other characteristics
        if has_friction == "yes" or has_backlash == "yes":
            print(f"✓ Friction/sticking detected → Using friction model")
            return MODEL_LIBRARY["friction"]

        if cable_driven == "yes" or has_oscillation == "yes":
            print(f"✓ Cable-driven or oscillation detected → Using second-order with gravity")
            return MODEL_LIBRARY["second-order"]

        # Default: first-order + gravity
        print(f"✓ Standard arm → Using first-order-gravity model (safe default)")
        print(f"  Consider using angle-dependent model if you can provide angle formula")
        return MODEL_LIBRARY["first-order-gravity"]

    else:
        # Unknown mechanism: use simplest model
        print(f"⚠ Unknown mechanism type '{mechanism}' → Using first-order model")
        return MODEL_LIBRARY["first-order"]


def ask_yes_no_unknown(question: str) -> str:
    """Ask a yes/no/unknown question interactively."""
    while True:
        print(f"\n{question}")
        print("  [y] Yes  [n] No  [u] Unknown/Skip")
        response = input("Your answer: ").strip().lower()

        if response in ["y", "yes"]:
            return "yes"
        elif response in ["n", "no"]:
            return "no"
        elif response in ["u", "unknown", "skip", ""]:
            return "unknown"
        else:
            print("Invalid response. Please enter y, n, or u.")


def validate_model_complexity(model: ModelStructure, data_quality: str = "unknown") -> bool:
    """
    Check if model complexity is appropriate for expected data quality.

    Returns:
        True if model is appropriate, False if should simplify
    """
    if data_quality == "noisy" and model.complexity == "complex":
        print(f"\n⚠ WARNING: {model.model_type} is complex ({model.num_parameters} params)")
        print(f"  Complex models may overfit with noisy data")
        print(f"  Recommendation: Collect clean data or use simpler model")
        return False

    return True


def suggest_simpler_model(current_model: ModelStructure) -> Optional[ModelStructure]:
    """Suggest a simpler fallback model."""
    simplification_map = {
        "variable-inertia": "first-order-gravity",
        "friction": "first-order-gravity",
        "second-order": "first-order-gravity",
        "angle-dependent": "first-order-gravity",
        "first-order-gravity": "first-order"
    }

    simpler_name = simplification_map.get(current_model.model_type)
    if simpler_name:
        return MODEL_LIBRARY[simpler_name]
    return None


# ============================================================================
# CUSTOM MODEL LOADING
# ============================================================================

def load_custom_model(model_file: Path) -> ModelStructure:
    """
    Load custom model definition from JSON file.

    Args:
        model_file: Path to custom model JSON file

    Returns:
        ModelStructure object representing the custom model

    Raises:
        ValueError: If JSON is invalid or missing required fields
    """
    try:
        with open(model_file) as f:
            custom = json.load(f)
    except FileNotFoundError:
        raise ValueError(f"Custom model file not found: {model_file}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in custom model file: {e}")

    # Validate required fields
    required = ["model_type", "description", "complexity", "parameters",
                "equation", "parameter_bounds", "initial_guess", "use_cases"]
    missing = [field for field in required if field not in custom]
    if missing:
        raise ValueError(f"Custom model missing required fields: {', '.join(missing)}")

    # Validate complexity
    if custom["complexity"] not in ["simple", "moderate", "complex"]:
        raise ValueError(f"Invalid complexity: {custom['complexity']} (must be simple/moderate/complex)")

    # Build ModelStructure
    return ModelStructure(
        model_type=custom["model_type"],
        parameters=custom["parameters"],
        equation=custom["equation"],
        transfer_function=custom.get("transfer_function"),
        num_parameters=len(custom["parameters"]),
        complexity=custom["complexity"],
        description=custom["description"],
        use_cases=custom["use_cases"],
        advantages=custom.get("advantages", []),
        limitations=custom.get("limitations", [])
    )


# ============================================================================
# OUTPUT GENERATION
# ============================================================================

def generate_model_output(
    model: ModelStructure,
    mechanism: str,
    characteristics: Dict[str, str]
) -> Dict[str, Any]:
    """Generate complete model selection output."""

    output = {
        "selected_model": {
            "model_type": model.model_type,
            "parameters": model.parameters,
            "num_parameters": model.num_parameters,
            "complexity": model.complexity,
            "equation": model.equation,
            "transfer_function": model.transfer_function
        },
        "mechanism": mechanism,
        "characteristics": characteristics,
        "description": model.description,
        "use_cases": model.use_cases,
        "advantages": model.advantages,
        "limitations": model.limitations,
        "validation_requirements": {
            "min_r_squared": 0.85,
            "min_confidence": 0.8,
            "physics_checks": ["all_parameters_positive", "reasonable_ranges"]
        },
        "fallback_model": None
    }

    # Add fallback recommendation
    simpler = suggest_simpler_model(model)
    if simpler:
        output["fallback_model"] = {
            "model_type": simpler.model_type,
            "reason": "Use if primary model fails validation (R² < 0.85)"
        }

    return output


def print_model_summary(model: ModelStructure):
    """Print human-readable model summary."""
    print("\n" + "=" * 70)
    print(f"SELECTED MODEL: {model.model_type}")
    print("=" * 70)
    print(f"\nDescription: {model.description}")
    print(f"Complexity: {model.complexity.upper()} ({model.num_parameters} parameters)")
    print(f"\nEquation: {model.equation}")
    if model.transfer_function:
        print(f"Transfer Function: {model.transfer_function}")

    print(f"\nParameters to identify: {', '.join(model.parameters)}")

    print(f"\n✓ Advantages:")
    for adv in model.advantages:
        print(f"  • {adv}")

    print(f"\n⚠ Limitations:")
    for lim in model.limitations:
        print(f"  • {lim}")

    print(f"\nUse Cases:")
    for use in model.use_cases:
        print(f"  • {use}")

    print("\n" + "=" * 70)


# ============================================================================
# MAIN CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Model Selection for System Identification",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (recommended)
  uv run select_model.py --mechanism elevator

  # With known characteristics
  uv run select_model.py --mechanism elevator --cable-driven yes --load-varies no

  # Quick mode (use defaults, no questions)
  uv run select_model.py --mechanism flywheel --quick

  # Output to file
  uv run select_model.py --mechanism arm --output model.json

Model Library:
  first-order          - Baseline (K, τ)
  first-order-gravity  - FTC default (K, τ, kg)
  second-order         - Oscillatory systems (K, ωn, ζ)
  angle-dependent      - Arms with known angle (K, τ, kg·cos(θ))
  friction             - Sticking mechanisms (J, b, friction)
  variable-inertia     - Telescoping (J(pos), b, kg)
        """
    )

    # Required arguments (unless --list-models)
    parser.add_argument(
        "--mechanism",
        choices=["elevator", "arm", "flywheel", "turret"],
        help="Mechanism type"
    )

    # Optional characteristics (skip interactive if provided)
    parser.add_argument("--has-friction", choices=["yes", "no", "unknown"],
                       help="Does it stick or have dead zones?")
    parser.add_argument("--has-backlash", choices=["yes", "no", "unknown"],
                       help="Gearbox backlash evident?")
    parser.add_argument("--load-varies", choices=["yes", "no", "unknown"],
                       help="Does load change during motion?")
    parser.add_argument("--cable-driven", choices=["yes", "no", "unknown"],
                       help="Cable/belt driven (vs direct)?")
    parser.add_argument("--has-oscillation", choices=["yes", "no", "unknown"],
                       help="Bounces or oscillates?")
    parser.add_argument("--knows-angle", choices=["yes", "no", "unknown"],
                       help="Can calculate angle from encoder? (arm only)")

    # Modes
    parser.add_argument("--quick", action="store_true",
                       help="Quick mode: use defaults, no interactive questions")
    parser.add_argument("--list-models", action="store_true",
                       help="List all available models and exit")
    parser.add_argument("--custom-model", type=str,
                       help="Load custom model from JSON file (bypasses built-in selection)")

    # Output
    parser.add_argument("--output", type=str,
                       help="Output JSON file (default: selected_model.json)")
    parser.add_argument("--quiet", action="store_true",
                       help="Suppress detailed output")

    args = parser.parse_args()

    # List models mode
    if args.list_models:
        print("\nAvailable Model Structures:\n")
        for name, model in MODEL_LIBRARY.items():
            print(f"{name:20s} ({model.complexity:8s}, {model.num_parameters} params)")
            print(f"  {model.description}")
            print()
        return 0

    # Custom model mode
    if args.custom_model:
        try:
            custom_path = Path(args.custom_model)
            selected_model = load_custom_model(custom_path)

            if not args.quiet:
                print("\n" + "=" * 70)
                print("CUSTOM MODEL LOADED")
                print("=" * 70)
                print_model_summary(selected_model)

            # Generate output
            mechanism = args.mechanism if args.mechanism else "custom"
            output = generate_model_output(selected_model, mechanism, {})

            # Save to file
            output_file = Path(args.output) if args.output else Path("selected_model.json")
            with open(output_file, "w") as f:
                json.dump(output, f, indent=2)

            if not args.quiet:
                print(f"\n✓ Custom model loaded and saved to {output_file}")
                print(f"\nNext step:")
                print(f"  uv run identify_params.py --data sysid_data.json \\")
                print(f"      --custom-model-spec {args.custom_model}")

            return 0

        except Exception as e:
            print(f"✗ Error loading custom model: {e}")
            return 1

    # Mechanism is required for all other operations
    if not args.mechanism:
        parser.error("--mechanism is required (unless using --list-models or --custom-model)")
        return 1

    # Interactive mode unless quick or characteristics provided
    # If user provided ANY characteristics, assume non-interactive (treat unknowns as defaults)
    has_any_characteristic = any([
        args.has_friction, args.has_backlash, args.load_varies,
        args.cable_driven, args.has_oscillation, args.knows_angle
    ])
    interactive = not args.quick and not has_any_characteristic

    if not args.quiet:
        print("\n" + "=" * 70)
        print("MODEL SELECTION FOR SYSTEM IDENTIFICATION")
        print("=" * 70)
        print(f"\nMechanism: {args.mechanism}")

        if args.quick:
            print("Mode: QUICK (using defaults)")
        elif has_any_characteristic:
            print("Mode: NON-INTERACTIVE (using provided characteristics + defaults)")
        else:
            print("Mode: INTERACTIVE (will ask questions for unknowns)")

    # Select model
    try:
        characteristics = {
            "has_friction": args.has_friction,
            "has_backlash": args.has_backlash,
            "load_varies": args.load_varies,
            "cable_driven": args.cable_driven,
            "has_oscillation": args.has_oscillation,
            "knows_angle": args.knows_angle
        }

        selected_model = select_model_for_mechanism(
            mechanism=args.mechanism,
            has_friction=args.has_friction,
            has_backlash=args.has_backlash,
            load_varies=args.load_varies,
            cable_driven=args.cable_driven,
            has_oscillation=args.has_oscillation,
            knows_angle=args.knows_angle,
            interactive=interactive
        )

        # Validate complexity
        validate_model_complexity(selected_model)

        # Print summary
        if not args.quiet:
            print_model_summary(selected_model)

            # Show fallback
            simpler = suggest_simpler_model(selected_model)
            if simpler:
                print(f"\n💡 Fallback: If validation fails (R² < 0.85), try '{simpler.model_type}'")

        # Generate output
        output = generate_model_output(selected_model, args.mechanism, characteristics)

        # Save to file
        output_file = Path(args.output) if args.output else Path("selected_model.json")
        with open(output_file, "w") as f:
            json.dump(output, f, indent=2)

        if not args.quiet:
            print(f"\n✓ Model selection saved to {output_file}")
            print(f"\nNext steps:")
            print(f"  1. Collect identification data: uv run collect_data.py --mechanism {args.mechanism}")
            print(f"  2. Identify parameters: uv run identify_params.py --data sysid_data.json --model {selected_model.model_type}")
            print(f"  3. Validate model: uv run validate_model.py --model identified_model.json")

        return 0

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

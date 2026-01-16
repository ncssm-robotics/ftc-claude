#!/usr/bin/env python3
"""
Autonomous Controller Tuning Orchestrator

Main workflow coordinator for autonomous PID tuning.
Orchestrates the entire tuning process from OpMode generation to parameter finalization.

Usage:
    uv run tuning_orchestrator.py
"""

# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "websocket-client",
# ]
# ///

import sys
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, Optional


class TuningOrchestrator:
    """Orchestrates the autonomous tuning workflow."""

    def __init__(self):
        self.mechanism_config: Optional[Dict[str, Any]] = None
        self.algorithm: str = ""
        self.iteration = 0
        self.max_iterations = 5
        self.current_gains: Dict[str, float] = {}
        self.telemetry_file = Path("telemetry.json")
        self.config_file = Path("mechanism_config.json")

    def run(self):
        """Main entry point for tuning workflow."""
        print("=" * 70)
        print("  FTC AUTONOMOUS CONTROLLER TUNING")
        print("=" * 70)
        print()

        # Phase 1: Setup
        if not self.setup_phase():
            return 1

        # Phase 2: Generate OpMode
        if not self.generate_opmode():
            return 1

        # Phase 3: Deploy
        if not self.deploy_phase():
            return 1

        # Phase 4: Safety checks
        if not self.safety_phase():
            return 1

        # Phase 5: Tuning loop
        if not self.tuning_loop():
            return 1

        # Phase 6: Finalization
        if not self.finalize():
            return 1

        print()
        print("✓ Tuning complete!")
        return 0

    def setup_phase(self) -> bool:
        """Interactive setup: mechanism type, limits, algorithm selection."""
        print("PHASE 1: SETUP")
        print("-" * 70)
        print()

        # Mechanism selection
        print("Select mechanism type:")
        print("  1. Elevator/Lift")
        print("  2. Arm/Pivot")
        print("  3. Flywheel/Shooter")
        print("  4. Turret")
        print()

        choice = input("Enter choice (1-4): ").strip()
        mechanism_map = {"1": "elevator", "2": "arm", "3": "flywheel", "4": "turret"}

        if choice not in mechanism_map:
            print("Invalid choice")
            return False

        mechanism = mechanism_map[choice]

        # Physical limits
        print()
        print(f"Enter physical limits for {mechanism}:")

        try:
            min_pos = int(input("  Min position (ticks): "))
            max_pos = int(input("  Max position (ticks): "))
            max_vel = int(input("  Max velocity (ticks/sec): "))
            max_accel = int(input("  Max acceleration (ticks/sec²): "))
        except ValueError:
            print("Invalid input")
            return False

        # Algorithm selection
        print()
        print("Select tuning algorithm:")
        print()
        print("  [1] Step Response (SAFE - Recommended)")
        print("      • Safe, conservative gains")
        print("      • 1-2 test runs")
        print("      • LOW risk of damage")
        print()
        print("  [2] Ziegler-Nichols (MEDIUM RISK)")
        print("      • Industry standard")
        print("      • Will oscillate during testing")
        print("      • MEDIUM risk - requires space")
        print()
        print("  [3] Relay Feedback (HIGHER RISK)")
        print("      • Automated oscillation test")
        print("      • Significant movement")
        print("      • MEDIUM-HIGH risk - ensure clearance")
        print()
        print("  [4] Optimization (MEDIUM RISK, TIME INTENSIVE)")
        print("      • Optimal gains via numerical methods")
        print("      • 5-20 test runs")
        print("      • MEDIUM risk - each run could be unstable")
        print()

        algo_choice = input("Enter choice (1-4): ").strip()
        algo_map = {
            "1": "step_response",
            "2": "ziegler_nichols",
            "3": "relay_feedback",
            "4": "optimize"
        }

        if algo_choice not in algo_map:
            print("Invalid choice")
            return False

        self.algorithm = algo_map[algo_choice]

        # Save configuration
        self.mechanism_config = {
            "name": mechanism.capitalize(),
            "type": mechanism,
            "min_position": min_pos,
            "max_position": max_pos,
            "max_velocity": max_vel,
            "max_acceleration": max_accel,
            "test_duration": 30,
            "motor_name": f"{mechanism}Motor",
            "ticks_per_radian": 1000.0,
            "tolerance": 10
        }

        # Save to file
        with open(self.config_file, "w") as f:
            json.dump(self.mechanism_config, f, indent=2)

        print()
        print("✓ Configuration saved")
        return True

    def generate_opmode(self) -> bool:
        """Generate NextFTC tuning OpMode."""
        print()
        print("PHASE 2: OPMODE GENERATION")
        print("-" * 70)
        print()

        mechanism = self.mechanism_config["type"]
        cmd = ["uv", "run", "opmode_generator.py", mechanism, str(self.config_file)]

        try:
            result = subprocess.run(cmd, cwd="plugins/robot-dev/scripts", capture_output=True, text=True)
            print(result.stdout)

            if result.returncode != 0:
                print(f"Error: {result.stderr}")
                return False

            print("✓ OpMode generated")
            return True
        except Exception as e:
            print(f"Error generating OpMode: {e}")
            return False

    def deploy_phase(self) -> bool:
        """Deploy OpMode to robot."""
        print()
        print("PHASE 3: DEPLOYMENT")
        print("-" * 70)
        print()
        print("NOTE: This step requires the robot-dev skill's /deploy command")
        print("      Claude should execute: /deploy")
        print()

        input("Press Enter once OpMode is deployed...")
        return True

    def safety_phase(self) -> bool:
        """Pre-run safety checks."""
        print()
        print("PHASE 4: SAFETY CHECKS")
        print("-" * 70)
        print()

        print("SAFETY CHECKLIST:")
        print("  ☐ Battery voltage >12V")
        print(f"  ☐ {self.mechanism_config['name']} at safe starting position")
        print("  ☐ No obstacles in mechanism's range of motion")
        print("  ☐ Emergency stop accessible")
        print("  ☐ Someone monitoring the robot")
        print()

        response = input("Ready to proceed? (yes/no): ").strip().lower()

        if response != "yes":
            print("Tuning aborted by user")
            return False

        return True

    def tuning_loop(self) -> bool:
        """Iterative tuning loop."""
        print()
        print("PHASE 5: TUNING ITERATIONS")
        print("-" * 70)
        print()

        for self.iteration in range(1, self.max_iterations + 1):
            print(f"\n{'=' * 70}")
            print(f"  TUNING RUN {self.iteration}/{self.max_iterations}")
            print(f"{'=' * 70}\n")

            # Initialize current gains (first iteration uses defaults from OpMode)
            if self.iteration == 1:
                self.current_gains = {
                    "kP": 0.001,
                    "kI": 0.0,
                    "kD": 0.0,
                    "kG": 0.0
                }

            print(f"Current gains: kP={self.current_gains['kP']}, kD={self.current_gains['kD']}, kG={self.current_gains['kG']}")
            print()

            # Prompt user to init/start OpMode
            print("ACTION REQUIRED:")
            print("  1. Init the tuning OpMode (use robot-dev /init command)")
            print("  2. Start the OpMode (use robot-dev /start command)")
            print()

            input("Press Enter when OpMode is running...")

            # Capture telemetry
            print("\nCapturing telemetry...")
            print("(Telemetry recorder would run here in full implementation)")
            print("For now, assuming telemetry is captured manually")
            print()

            input("Press Enter when test is complete...")

            # Stop OpMode
            print("\nACTION REQUIRED: Stop the OpMode (use robot-dev /stop command)")
            input("Press Enter when OpMode is stopped...")

            # Analyze telemetry (placeholder)
            print("\nAnalyzing telemetry...")
            print(f"(Would run tuning algorithm: {self.algorithm})")
            print()

            # Propose new gains (placeholder - in real implementation, call tuning_algorithms.py)
            proposed_gains = {
                "kP": self.current_gains["kP"] * 1.5,
                "kI": self.current_gains["kI"],
                "kD": self.current_gains["kD"] + 0.0001,
                "kG": self.current_gains["kG"] + 0.05
            }

            print(f"Proposed gains: kP={proposed_gains['kP']:.5f}, kD={proposed_gains['kD']:.5f}, kG={proposed_gains['kG']:.3f}")
            print()

            # User decision
            print("Options:")
            print("  c - Continue with proposed gains")
            print("  r - Revert to previous gains")
            print("  a - Accept current gains and finish")
            print("  q - Abort tuning")
            print()

            choice = input("Your choice (c/r/a/q): ").strip().lower()

            if choice == "a":
                print("\n✓ Gains accepted")
                return True
            elif choice == "q":
                print("\n✗ Tuning aborted")
                return False
            elif choice == "r":
                print("\n← Reverting to previous gains")
                continue
            elif choice == "c":
                print("\n→ Applying proposed gains")
                print("   (Would update via Panels or Sloth Load)")
                self.current_gains = proposed_gains
                continue
            else:
                print("Invalid choice, continuing with proposed gains")
                self.current_gains = proposed_gains

        print(f"\n✓ Completed {self.max_iterations} iterations")
        return True

    def finalize(self) -> bool:
        """Finalize and apply tuned parameters."""
        print()
        print("PHASE 6: FINALIZATION")
        print("-" * 70)
        print()

        print("FINAL TUNED PARAMETERS:")
        print(f"  kP = {self.current_gains['kP']:.5f}")
        print(f"  kI = {self.current_gains['kI']:.5f}")
        print(f"  kD = {self.current_gains['kD']:.5f}")
        if self.current_gains.get('kG', 0) > 0:
            print(f"  kG = {self.current_gains['kG']:.3f} (feedforward)")
        print()

        print("Detecting parameter application method...")
        print("  (Would check for Sloth Load and Panels)")
        print()

        print("Recommendation:")
        print("  1. If Sloth Load installed: Apply via code update + hot reload")
        print("  2. If Panels only: Update via configurables")
        print("  3. Otherwise: Manually update TuningConfig.kt")
        print()

        # Save results
        results_file = Path("tuning_results.json")
        with open(results_file, "w") as f:
            json.dump({
                "mechanism": self.mechanism_config,
                "algorithm": self.algorithm,
                "final_gains": self.current_gains,
                "iterations": self.iteration
            }, f, indent=2)

        print(f"✓ Results saved to {results_file}")
        return True


def main():
    orchestrator = TuningOrchestrator()
    return orchestrator.run()


if __name__ == "__main__":
    sys.exit(main())

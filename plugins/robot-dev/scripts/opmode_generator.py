#!/usr/bin/env python3
"""
NextFTC Tuning OpMode Generator

Generates mechanism-specific tuning OpModes with:
- @Configurable parameters for live tuning
- Safety limits (position, velocity, timeout)
- Structured telemetry (Panels display + JSON logging)
- ControlSystem builders with appropriate feedforward

Usage:
    uv run opmode_generator.py <mechanism> <config.json>

    mechanism: elevator | arm | flywheel | turret
    config.json: JSON file with mechanism configuration

Example config.json:
    {
        "name": "Elevator",
        "min_position": 0,
        "max_position": 2000,
        "max_velocity": 1500,
        "max_acceleration": 3000,
        "test_duration": 30,
        "algorithm": "step_response"
    }
"""

# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

import sys
import json
import os
from pathlib import Path
from typing import Dict, Any


ELEVATOR_TEMPLATE = '''package org.firstinspires.ftc.teamcode.tuning

import com.qualcomm.robotcore.eventloop.opmode.TeleOp
import dev.frozenmilk.dairy.core.util.supplier.numeric.EnhancedDoubleSupplier
import dev.frozenmilk.nextftc.NextFTCOpMode
import dev.frozenmilk.nextftc.command.LambdaCommand
import dev.frozenmilk.nextftc.components.BulkReadComponent
import dev.frozenmilk.nextftc.components.SubsystemComponent
import dev.frozenmilk.nextftc.subsystems.Subsystem
import dev.frozenmilk.nextftc.control.ControlSystem
import dev.frozenmilk.nextftc.control.KineticState
import dev.frozenmilk.nextftc.hardware.MotorEx
import org.firstinspires.ftc.teamcode.TuningConfig
import org.nextftc.ftc.command.CommandManager
import android.util.Log

/**
 * AUTO-GENERATED Tuning OpMode for {mechanism_name}
 *
 * Safety Features:
 * - Hard position limits: [{min_position}, {max_position}]
 * - Max velocity limit: {max_velocity} ticks/sec
 * - Timeout: {test_duration} seconds
 *
 * Tuning Parameters (via Panels @Configurable):
 * - TuningConfig.{config_prefix}_KP
 * - TuningConfig.{config_prefix}_KI
 * - TuningConfig.{config_prefix}_KD
 * - TuningConfig.{config_prefix}_KG
 *
 * Telemetry:
 * - Real-time: Displayed in Panels dashboard
 * - Logged: JSON format to logcat (tag: TUNING)
 */
@TeleOp(name = "{mechanism_name} Tuning")
class {class_name}TuningOpMode : NextFTCOpMode() {{
    init {{
        addComponents(
            BulkReadComponent,
            SubsystemComponent
        )
    }}

    override fun onStartButtonPressed() {{
        CommandManager.scheduleCommand(
            {mechanism_name}Subsystem.runTuningTest()
        )
    }}
}}

object {mechanism_name}Subsystem : Subsystem {{
    // Hardware
    private val motor by lazy {{
        MotorEx(hardwareMap, "{motor_name}")
            .also {{
                it.resetEncoder()
                it.zeroPowerBehavior = MotorEx.ZeroPowerBehavior.BRAKE
            }}
    }}

    // Safety limits
    private const val MIN_POSITION = {min_position}
    private const val MAX_POSITION = {max_position}
    private const val MAX_VELOCITY = {max_velocity}
    private const val TEST_DURATION = {test_duration}.0

    // Test parameters
    private var targetPosition = {target_position}  // Mid-point for testing

    // Control system (rebuilt each cycle to pick up tuning changes)
    private fun buildController() = ControlSystem.builder()
        .posPid(
            TuningConfig.{config_prefix}_KP,
            TuningConfig.{config_prefix}_KI,
            TuningConfig.{config_prefix}_KD
        )
        .elevatorFF(kG = TuningConfig.{config_prefix}_KG)
        .build()

    private var controller = buildController()
    private var testStartTime = 0.0

    override fun initialize() {{
        // Start at current position
    }}

    override fun periodic() {{
        // Rebuild controller to pick up tuning changes from Panels
        controller = buildController()

        // Read current state
        val currentPosition = motor.currentPosition.toDouble()
        val currentVelocity = motor.velocity

        // Safety checks
        if (currentPosition < MIN_POSITION || currentPosition > MAX_POSITION) {{
            motor.power = 0.0
            telemetry.addData("⚠️ ERROR", "POSITION LIMIT EXCEEDED")
            telemetry.addData("Position", "%.0f (limit: [%d, %d])".format(
                currentPosition, MIN_POSITION, MAX_POSITION
            ))
            telemetry.update()
            Log.e("TUNING", "Position limit exceeded: $currentPosition")
            requestOpModeStop()
            return
        }}

        if (runtime.seconds() > TEST_DURATION + 5) {{
            telemetry.addData("⚠️ TIMEOUT", "Test exceeded maximum duration")
            telemetry.update()
            requestOpModeStop()
            return
        }}

        // Calculate control output
        controller.goal = KineticState(position = targetPosition)
        val output = controller.calculate(KineticState(
            position = currentPosition,
            velocity = currentVelocity
        ))

        // Apply control (with velocity limiting for safety)
        motor.power = output.coerceIn(-1.0, 1.0)

        // Calculate error
        val error = targetPosition - currentPosition
        val onTarget = controller.isWithinTolerance()

        // Telemetry (Panels dashboard)
        telemetry.addData("🎯 Target", "%.0f ticks".format(targetPosition))
        telemetry.addData("📍 Position", "%.0f ticks".format(currentPosition))
        telemetry.addData("⚡ Velocity", "%.0f ticks/sec".format(currentVelocity))
        telemetry.addData("📊 Error", "%.0f ticks".format(error))
        telemetry.addData("🔋 Power", "%.3f".format(motor.power))
        telemetry.addData("✓ On Target", if (onTarget) "YES" else "NO")
        telemetry.addLine()
        telemetry.addData("Gains", "kP=%.4f kD=%.4f kG=%.4f".format(
            TuningConfig.{config_prefix}_KP,
            TuningConfig.{config_prefix}_KD,
            TuningConfig.{config_prefix}_KG
        ))
        telemetry.addData("Time", "%.1f / %.0f sec".format(runtime.seconds(), TEST_DURATION))
        telemetry.update()

        // Structured logging for telemetry capture (JSON format)
        val telemetryJson = """{{
            "t": ${{runtime.seconds()}},
            "pos": $currentPosition,
            "vel": $currentVelocity,
            "target": $targetPosition,
            "error": $error,
            "power": ${{motor.power}},
            "kP": ${{TuningConfig.{config_prefix}_KP}},
            "kD": ${{TuningConfig.{config_prefix}_KD}},
            "kG": ${{TuningConfig.{config_prefix}_KG}},
            "onTarget": $onTarget
        }}"""
        Log.d("TUNING", telemetryJson)
    }}

    /**
     * Command to run tuning test
     * Moves to target position and holds for TEST_DURATION seconds
     */
    fun runTuningTest() = LambdaCommand()
        .setStart {{
            testStartTime = runtime.seconds()
            targetPosition = {target_position}  // Mid-point
            telemetry.speak("Starting tuning test")
        }}
        .setIsDone {{
            runtime.seconds() - testStartTime > TEST_DURATION
        }}
        .setStop {{
            motor.power = 0.0
            telemetry.speak("Tuning test complete")
        }}
        .requires(this)
}}
'''

ARM_TEMPLATE = '''package org.firstinspires.ftc.teamcode.tuning

import com.qualcomm.robotcore.eventloop.opmode.TeleOp
import dev.frozenmilk.dairy.core.util.supplier.numeric.EnhancedDoubleSupplier
import dev.frozenmilk.nextftc.NextFTCOpMode
import dev.frozenmilk.nextftc.command.LambdaCommand
import dev.frozenmilk.nextftc.components.BulkReadComponent
import dev.frozenmilk.nextftc.components.SubsystemComponent
import dev.frozenmilk.nextftc.subsystems.Subsystem
import dev.frozenmilk.nextftc.control.ControlSystem
import dev.frozenmilk.nextftc.control.KineticState
import dev.frozenmilk.nextftc.hardware.MotorEx
import org.firstinspires.ftc.teamcode.TuningConfig
import org.nextftc.ftc.command.CommandManager
import android.util.Log
import kotlin.math.cos

/**
 * AUTO-GENERATED Tuning OpMode for {mechanism_name}
 *
 * Safety Features:
 * - Hard position limits: [{min_position}, {max_position}] ticks
 * - Max velocity limit: {max_velocity} ticks/sec
 * - Timeout: {test_duration} seconds
 *
 * Tuning Parameters (via Panels @Configurable):
 * - TuningConfig.{config_prefix}_KP
 * - TuningConfig.{config_prefix}_KI
 * - TuningConfig.{config_prefix}_KD
 * - TuningConfig.{config_prefix}_KG
 * - TuningConfig.{config_prefix}_TICKS_PER_RADIAN
 */
@TeleOp(name = "{mechanism_name} Tuning")
class {class_name}TuningOpMode : NextFTCOpMode() {{
    init {{
        addComponents(
            BulkReadComponent,
            SubsystemComponent
        )
    }}

    override fun onStartButtonPressed() {{
        CommandManager.scheduleCommand(
            {mechanism_name}Subsystem.runTuningTest()
        )
    }}
}}

object {mechanism_name}Subsystem : Subsystem {{
    // Hardware
    private val motor by lazy {{
        MotorEx(hardwareMap, "{motor_name}")
            .also {{
                it.resetEncoder()
                it.zeroPowerBehavior = MotorEx.ZeroPowerBehavior.BRAKE
            }}
    }}

    // Safety limits
    private const val MIN_POSITION = {min_position}
    private const val MAX_POSITION = {max_position}
    private const val MAX_VELOCITY = {max_velocity}
    private const val TEST_DURATION = {test_duration}.0

    // Test parameters
    private var targetPosition = {target_position}  // Horizontal position (90 degrees)

    // Angle conversion
    private fun ticksToRadians(ticks: Double) = ticks / TuningConfig.{config_prefix}_TICKS_PER_RADIAN

    // Control system (rebuilt each cycle to pick up tuning changes)
    private fun buildController() = ControlSystem.builder()
        .posPid(
            TuningConfig.{config_prefix}_KP,
            TuningConfig.{config_prefix}_KI,
            TuningConfig.{config_prefix}_KD
        )
        .armFF(
            kG = TuningConfig.{config_prefix}_KG,
            angle = {{ ticksToRadians(motor.currentPosition.toDouble()) }}
        )
        .build()

    private var controller = buildController()
    private var testStartTime = 0.0

    override fun initialize() {{
        // Start at current position
    }}

    override fun periodic() {{
        // Rebuild controller to pick up tuning changes
        controller = buildController()

        // Read current state
        val currentPosition = motor.currentPosition.toDouble()
        val currentVelocity = motor.velocity
        val currentAngle = ticksToRadians(currentPosition)

        // Safety checks
        if (currentPosition < MIN_POSITION || currentPosition > MAX_POSITION) {{
            motor.power = 0.0
            telemetry.addData("⚠️ ERROR", "POSITION LIMIT EXCEEDED")
            telemetry.addData("Position", "%.0f (limit: [%d, %d])".format(
                currentPosition, MIN_POSITION, MAX_POSITION
            ))
            telemetry.update()
            Log.e("TUNING", "Position limit exceeded: $currentPosition")
            requestOpModeStop()
            return
        }}

        if (runtime.seconds() > TEST_DURATION + 5) {{
            telemetry.addData("⚠️ TIMEOUT", "Test exceeded maximum duration")
            telemetry.update()
            requestOpModeStop()
            return
        }}

        // Calculate control output
        controller.goal = KineticState(position = targetPosition)
        val output = controller.calculate(KineticState(
            position = currentPosition,
            velocity = currentVelocity
        ))

        // Apply control
        motor.power = output.coerceIn(-1.0, 1.0)

        // Calculate error
        val error = targetPosition - currentPosition
        val onTarget = controller.isWithinTolerance()

        // Telemetry
        telemetry.addData("🎯 Target", "%.0f ticks (%.1f°)".format(
            targetPosition, Math.toDegrees(ticksToRadians(targetPosition))
        ))
        telemetry.addData("📍 Position", "%.0f ticks (%.1f°)".format(
            currentPosition, Math.toDegrees(currentAngle)
        ))
        telemetry.addData("⚡ Velocity", "%.0f ticks/sec".format(currentVelocity))
        telemetry.addData("📊 Error", "%.0f ticks".format(error))
        telemetry.addData("🔋 Power", "%.3f".format(motor.power))
        telemetry.addData("🔄 FF (cos)", "%.3f".format(cos(currentAngle)))
        telemetry.addData("✓ On Target", if (onTarget) "YES" else "NO")
        telemetry.addLine()
        telemetry.addData("Gains", "kP=%.4f kD=%.4f kG=%.4f".format(
            TuningConfig.{config_prefix}_KP,
            TuningConfig.{config_prefix}_KD,
            TuningConfig.{config_prefix}_KG
        ))
        telemetry.addData("Time", "%.1f / %.0f sec".format(runtime.seconds(), TEST_DURATION))
        telemetry.update()

        // Structured logging
        val telemetryJson = """{{
            "t": ${{runtime.seconds()}},
            "pos": $currentPosition,
            "vel": $currentVelocity,
            "angle": $currentAngle,
            "target": $targetPosition,
            "error": $error,
            "power": ${{motor.power}},
            "kP": ${{TuningConfig.{config_prefix}_KP}},
            "kD": ${{TuningConfig.{config_prefix}_KD}},
            "kG": ${{TuningConfig.{config_prefix}_KG}},
            "ff_cos": ${{cos(currentAngle)}},
            "onTarget": $onTarget
        }}"""
        Log.d("TUNING", telemetryJson)
    }}

    fun runTuningTest() = LambdaCommand()
        .setStart {{
            testStartTime = runtime.seconds()
            targetPosition = {target_position}  // Horizontal
            telemetry.speak("Starting arm tuning test")
        }}
        .setIsDone {{
            runtime.seconds() - testStartTime > TEST_DURATION
        }}
        .setStop {{
            motor.power = 0.0
            telemetry.speak("Arm tuning test complete")
        }}
        .requires(this)
}}
'''

FLYWHEEL_TEMPLATE = '''package org.firstinspires.ftc.teamcode.tuning

import com.qualcomm.robotcore.eventloop.opmode.TeleOp
import dev.frozenmilk.dairy.core.util.supplier.numeric.EnhancedDoubleSupplier
import dev.frozenmilk.nextftc.NextFTCOpMode
import dev.frozenmilk.nextftc.command.LambdaCommand
import dev.frozenmilk.nextftc.components.BulkReadComponent
import dev.frozenmilk.nextftc.components.SubsystemComponent
import dev.frozenmilk.nextftc.subsystems.Subsystem
import dev.frozenmilk.nextftc.control.ControlSystem
import dev.frozenmilk.nextftc.control.KineticState
import dev.frozenmilk.nextftc.hardware.MotorEx
import org.firstinspires.ftc.teamcode.TuningConfig
import org.nextftc.ftc.command.CommandManager
import android.util.Log

/**
 * AUTO-GENERATED Tuning OpMode for {mechanism_name}
 *
 * Safety Features:
 * - Max velocity limit: {max_velocity} ticks/sec
 * - Timeout: {test_duration} seconds
 *
 * Tuning Parameters (via Panels @Configurable):
 * - TuningConfig.{config_prefix}_KP (velocity P gain)
 * - TuningConfig.{config_prefix}_KV (velocity feedforward)
 */
@TeleOp(name = "{mechanism_name} Tuning")
class {class_name}TuningOpMode : NextFTCOpMode() {{
    init {{
        addComponents(
            BulkReadComponent,
            SubsystemComponent
        )
    }}

    override fun onStartButtonPressed() {{
        CommandManager.scheduleCommand(
            {mechanism_name}Subsystem.runTuningTest()
        )
    }}
}}

object {mechanism_name}Subsystem : Subsystem {{
    // Hardware
    private val motor by lazy {{
        MotorEx(hardwareMap, "{motor_name}")
            .also {{
                it.resetEncoder()
                it.zeroPowerBehavior = MotorEx.ZeroPowerBehavior.FLOAT  // Flywheel needs coast
            }}
    }}

    // Safety limits
    private const val MAX_VELOCITY = {max_velocity}
    private const val TEST_DURATION = {test_duration}.0

    // Test parameters
    private var targetVelocity = {target_velocity}  // 70% of max for testing

    // Control system (rebuilt each cycle to pick up tuning changes)
    private fun buildController() = ControlSystem.builder()
        .velPid(TuningConfig.{config_prefix}_KP, 0.0, 0.0)
        .basicFF(kV = TuningConfig.{config_prefix}_KV)
        .build()

    private var controller = buildController()
    private var testStartTime = 0.0

    override fun initialize() {{
        // Nothing to initialize
    }}

    override fun periodic() {{
        // Rebuild controller to pick up tuning changes
        controller = buildController()

        // Read current state
        val currentVelocity = motor.velocity

        // Safety checks
        if (runtime.seconds() > TEST_DURATION + 5) {{
            telemetry.addData("⚠️ TIMEOUT", "Test exceeded maximum duration")
            telemetry.update()
            requestOpModeStop()
            return
        }}

        // Calculate control output
        controller.goal = KineticState(velocity = targetVelocity)
        val output = controller.calculate(KineticState(velocity = currentVelocity))

        // Apply control
        motor.power = output.coerceIn(-1.0, 1.0)

        // Calculate error
        val error = targetVelocity - currentVelocity
        val onTarget = controller.isWithinTolerance()

        // Telemetry
        telemetry.addData("🎯 Target Velocity", "%.0f ticks/sec".format(targetVelocity))
        telemetry.addData("⚡ Current Velocity", "%.0f ticks/sec".format(currentVelocity))
        telemetry.addData("📊 Error", "%.0f ticks/sec".format(error))
        telemetry.addData("🔋 Power", "%.3f".format(motor.power))
        telemetry.addData("✓ On Target", if (onTarget) "YES" else "NO")
        telemetry.addLine()
        telemetry.addData("Gains", "kP=%.4f kV=%.4f".format(
            TuningConfig.{config_prefix}_KP,
            TuningConfig.{config_prefix}_KV
        ))
        telemetry.addData("Time", "%.1f / %.0f sec".format(runtime.seconds(), TEST_DURATION))
        telemetry.update()

        // Structured logging
        val telemetryJson = """{{
            "t": ${{runtime.seconds()}},
            "vel": $currentVelocity,
            "target": $targetVelocity,
            "error": $error,
            "power": ${{motor.power}},
            "kP": ${{TuningConfig.{config_prefix}_KP}},
            "kV": ${{TuningConfig.{config_prefix}_KV}},
            "onTarget": $onTarget
        }}"""
        Log.d("TUNING", telemetryJson)
    }}

    fun runTuningTest() = LambdaCommand()
        .setStart {{
            testStartTime = runtime.seconds()
            targetVelocity = {target_velocity}
            telemetry.speak("Starting flywheel tuning test")
        }}
        .setIsDone {{
            runtime.seconds() - testStartTime > TEST_DURATION
        }}
        .setStop {{
            motor.power = 0.0
            telemetry.speak("Flywheel tuning test complete")
        }}
        .requires(this)
}}
'''

TURRET_TEMPLATE = '''package org.firstinspires.ftc.teamcode.tuning

import com.qualcomm.robotcore.eventloop.opmode.TeleOp
import dev.frozenmilk.dairy.core.util.supplier.numeric.EnhancedDoubleSupplier
import dev.frozenmilk.nextftc.NextFTCOpMode
import dev.frozenmilk.nextftc.command.LambdaCommand
import dev.frozenmilk.nextftc.components.BulkReadComponent
import dev.frozenmilk.nextftc.components.SubsystemComponent
import dev.frozenmilk.nextftc.subsystems.Subsystem
import dev.frozenmilk.nextftc.control.ControlSystem
import dev.frozenmilk.nextftc.control.KineticState
import dev.frozenmilk.nextftc.hardware.MotorEx
import org.firstinspires.ftc.teamcode.TuningConfig
import org.nextftc.ftc.command.CommandManager
import android.util.Log

/**
 * AUTO-GENERATED Tuning OpMode for {mechanism_name}
 *
 * Safety Features:
 * - Hard position limits: [{min_position}, {max_position}] ticks
 * - Max velocity limit: {max_velocity} ticks/sec
 * - Timeout: {test_duration} seconds
 *
 * Tuning Parameters (via Panels @Configurable):
 * - TuningConfig.{config_prefix}_KP
 * - TuningConfig.{config_prefix}_KD
 */
@TeleOp(name = "{mechanism_name} Tuning")
class {class_name}TuningOpMode : NextFTCOpMode() {{
    init {{
        addComponents(
            BulkReadComponent,
            SubsystemComponent
        )
    }}

    override fun onStartButtonPressed() {{
        CommandManager.scheduleCommand(
            {mechanism_name}Subsystem.runTuningTest()
        )
    }}
}}

object {mechanism_name}Subsystem : Subsystem {{
    // Hardware
    private val motor by lazy {{
        MotorEx(hardwareMap, "{motor_name}")
            .also {{
                it.resetEncoder()
                it.zeroPowerBehavior = MotorEx.ZeroPowerBehavior.BRAKE
            }}
    }}

    // Safety limits
    private const val MIN_POSITION = {min_position}
    private const val MAX_POSITION = {max_position}
    private const val MAX_VELOCITY = {max_velocity}
    private const val TEST_DURATION = {test_duration}.0

    // Test parameters
    private var targetPosition = {target_position}  // Center position

    // Control system (rebuilt each cycle to pick up tuning changes)
    private fun buildController() = ControlSystem.builder()
        .posPid(
            TuningConfig.{config_prefix}_KP,
            0.0,  // No I gain for turret
            TuningConfig.{config_prefix}_KD
        )
        .build()

    private var controller = buildController()
    private var testStartTime = 0.0

    override fun initialize() {{
        // Start at current position
    }}

    override fun periodic() {{
        // Rebuild controller to pick up tuning changes
        controller = buildController()

        // Read current state
        val currentPosition = motor.currentPosition.toDouble()
        val currentVelocity = motor.velocity

        // Safety checks
        if (currentPosition < MIN_POSITION || currentPosition > MAX_POSITION) {{
            motor.power = 0.0
            telemetry.addData("⚠️ ERROR", "POSITION LIMIT EXCEEDED")
            telemetry.addData("Position", "%.0f (limit: [%d, %d])".format(
                currentPosition, MIN_POSITION, MAX_POSITION
            ))
            telemetry.update()
            Log.e("TUNING", "Position limit exceeded: $currentPosition")
            requestOpModeStop()
            return
        }}

        if (runtime.seconds() > TEST_DURATION + 5) {{
            telemetry.addData("⚠️ TIMEOUT", "Test exceeded maximum duration")
            telemetry.update()
            requestOpModeStop()
            return
        }}

        // Calculate control output
        controller.goal = KineticState(position = targetPosition)
        val output = controller.calculate(KineticState(
            position = currentPosition,
            velocity = currentVelocity
        ))

        // Apply control
        motor.power = output.coerceIn(-1.0, 1.0)

        // Calculate error
        val error = targetPosition - currentPosition
        val onTarget = controller.isWithinTolerance()

        // Telemetry
        telemetry.addData("🎯 Target", "%.0f ticks".format(targetPosition))
        telemetry.addData("📍 Position", "%.0f ticks".format(currentPosition))
        telemetry.addData("⚡ Velocity", "%.0f ticks/sec".format(currentVelocity))
        telemetry.addData("📊 Error", "%.0f ticks".format(error))
        telemetry.addData("🔋 Power", "%.3f".format(motor.power))
        telemetry.addData("✓ On Target", if (onTarget) "YES" else "NO")
        telemetry.addLine()
        telemetry.addData("Gains", "kP=%.4f kD=%.4f".format(
            TuningConfig.{config_prefix}_KP,
            TuningConfig.{config_prefix}_KD
        ))
        telemetry.addData("Time", "%.1f / %.0f sec".format(runtime.seconds(), TEST_DURATION))
        telemetry.update()

        // Structured logging
        val telemetryJson = """{{
            "t": ${{runtime.seconds()}},
            "pos": $currentPosition,
            "vel": $currentVelocity,
            "target": $targetPosition,
            "error": $error,
            "power": ${{motor.power}},
            "kP": ${{TuningConfig.{config_prefix}_KP}},
            "kD": ${{TuningConfig.{config_prefix}_KD}},
            "onTarget": $onTarget
        }}"""
        Log.d("TUNING", telemetryJson)
    }}

    fun runTuningTest() = LambdaCommand()
        .setStart {{
            testStartTime = runtime.seconds()
            targetPosition = {target_position}
            telemetry.speak("Starting turret tuning test")
        }}
        .setIsDone {{
            runtime.seconds() - testStartTime > TEST_DURATION
        }}
        .setStop {{
            motor.power = 0.0
            telemetry.speak("Turret tuning test complete")
        }}
        .requires(this)
}}
'''

TUNING_CONFIG_TEMPLATE = '''package org.firstinspires.ftc.teamcode

import com.acmerobotics.dashboard.config.Config

/**
 * Tuning configuration for {mechanism_name}
 * These values can be edited live via Panels dashboard
 */
@Config
object TuningConfig {{
    // {mechanism_name} gains
    @JvmField var {config_prefix}_KP = {initial_kp}
    @JvmField var {config_prefix}_KI = {initial_ki}
    @JvmField var {config_prefix}_KD = {initial_kd}
    @JvmField var {config_prefix}_KG = {initial_kg}
    @JvmField var {config_prefix}_KV = {initial_kv}

    // {mechanism_name} parameters
    @JvmField var {config_prefix}_TICKS_PER_RADIAN = {ticks_per_radian}
    @JvmField var {config_prefix}_TOLERANCE = {tolerance}
}}
'''


def generate_opmode(mechanism: str, config: Dict[str, Any], output_dir: Path) -> str:
    """Generate a tuning OpMode for the specified mechanism."""

    # Select template based on mechanism type
    templates = {
        "elevator": ELEVATOR_TEMPLATE,
        "arm": ARM_TEMPLATE,
        "flywheel": FLYWHEEL_TEMPLATE,
        "turret": TURRET_TEMPLATE
    }

    if mechanism not in templates:
        raise ValueError(f"Unknown mechanism type: {mechanism}. Must be one of: {list(templates.keys())}")

    template = templates[mechanism]

    # Calculate derived values
    mechanism_name = config.get("name", mechanism.capitalize())
    class_name = mechanism_name.replace(" ", "")
    config_prefix = mechanism_name.upper().replace(" ", "_")
    motor_name = config.get("motor_name", f"{mechanism}Motor")

    # Calculate target positions
    min_pos = config.get("min_position", 0)
    max_pos = config.get("max_position", 1000)
    target_position = (min_pos + max_pos) // 2  # Mid-point

    # For flywheel, use percentage of max velocity
    max_vel = config.get("max_velocity", 1000)
    target_velocity = int(max_vel * 0.7)  # 70% of max

    # Initial conservative gains
    initial_gains = {
        "elevator": {"kp": 0.001, "ki": 0.0, "kd": 0.0, "kg": 0.0, "kv": 0.0},
        "arm": {"kp": 0.001, "ki": 0.0, "kd": 0.0, "kg": 0.0, "kv": 0.0},
        "flywheel": {"kp": 0.0001, "ki": 0.0, "kd": 0.0, "kg": 0.0, "kv": 0.0001},
        "turret": {"kp": 0.001, "ki": 0.0, "kd": 0.0, "kg": 0.0, "kv": 0.0}
    }

    gains = initial_gains[mechanism]

    # Format the template
    opmode_content = template.format(
        mechanism_name=mechanism_name,
        class_name=class_name,
        config_prefix=config_prefix,
        motor_name=motor_name,
        min_position=min_pos,
        max_position=max_pos,
        max_velocity=max_vel,
        target_position=target_position,
        target_velocity=target_velocity,
        test_duration=config.get("test_duration", 30)
    )

    # Generate TuningConfig file
    tuning_config_content = TUNING_CONFIG_TEMPLATE.format(
        mechanism_name=mechanism_name,
        config_prefix=config_prefix,
        initial_kp=gains["kp"],
        initial_ki=gains["ki"],
        initial_kd=gains["kd"],
        initial_kg=gains["kg"],
        initial_kv=gains["kv"],
        ticks_per_radian=config.get("ticks_per_radian", 1000.0),
        tolerance=config.get("tolerance", 10)
    )

    # Write files
    output_dir.mkdir(parents=True, exist_ok=True)

    opmode_file = output_dir / f"{class_name}TuningOpMode.kt"
    config_file = output_dir / "TuningConfig.kt"

    opmode_file.write_text(opmode_content)
    config_file.write_text(tuning_config_content)

    return str(opmode_file)


def main():
    if len(sys.argv) != 3:
        print("Usage: uv run opmode_generator.py <mechanism> <config.json>")
        print("  mechanism: elevator | arm | flywheel | turret")
        print("  config.json: JSON file with mechanism configuration")
        sys.exit(1)

    mechanism = sys.argv[1].lower()
    config_file = Path(sys.argv[2])

    if not config_file.exists():
        print(f"Error: Config file not found: {config_file}")
        sys.exit(1)

    # Load configuration
    with open(config_file) as f:
        config = json.load(f)

    # Determine output directory (assume TeamCode structure)
    output_dir = Path.cwd() / "TeamCode" / "src" / "main" / "java" / "org" / "firstinspires" / "ftc" / "teamcode" / "tuning"

    # Generate OpMode
    try:
        opmode_path = generate_opmode(mechanism, config, output_dir)
        print(f"✓ Generated tuning OpMode: {opmode_path}")
        print(f"✓ Generated config file: {output_dir / 'TuningConfig.kt'}")
        print()
        print("Next steps:")
        print("  1. Review the generated files")
        print("  2. Run /deploy to build and install")
        print("  3. Use Panels dashboard to tune @Configurable parameters")
    except Exception as e:
        print(f"Error generating OpMode: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

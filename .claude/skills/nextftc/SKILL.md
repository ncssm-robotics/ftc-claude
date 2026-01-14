---
name: nextftc
description: Helps write FTC robot code using the NextFTC command-based framework. Use when creating OpModes, commands, subsystems, gamepad bindings, or integrating with Pedro Pathing.
---

# NextFTC

NextFTC is a command-based framework for FTC robotics written in Kotlin. It provides structured patterns for commands, subsystems, and gamepad bindings.

## Quick Start

### Dependencies (build.dependencies.gradle)

```gradle
implementation 'dev.nextftc:ftc:1.0.1'
implementation 'dev.nextftc:hardware:1.0.1'      // Optional: hardware wrappers
implementation 'dev.nextftc:bindings:1.0.1'     // Gamepad bindings
implementation 'dev.nextftc:control:1.0.0'      // PID/feedforward
implementation 'dev.nextftc.extensions:pedro:1.0.0'  // Pedro Pathing
```

### Key Imports

```kotlin
// Core OpMode
import dev.nextftc.ftc.NextFTCOpMode
import dev.nextftc.ftc.Gamepads
import dev.nextftc.ftc.ActiveOpMode
import dev.nextftc.ftc.components.BulkReadComponent

// Commands
import dev.nextftc.core.commands.Command
import dev.nextftc.core.commands.utility.LambdaCommand
import dev.nextftc.core.commands.utility.InstantCommand
import dev.nextftc.core.commands.groups.SequentialGroup
import dev.nextftc.core.commands.groups.ParallelGroup
import dev.nextftc.core.commands.delays.Delay

// Components & Subsystems
import dev.nextftc.core.components.Component
import dev.nextftc.core.components.SubsystemComponent
import dev.nextftc.core.components.BindingsComponent
import dev.nextftc.core.subsystems.Subsystem

// Pedro Extension
import dev.nextftc.extensions.pedro.PedroComponent
import dev.nextftc.extensions.pedro.PedroDriverControlled
import dev.nextftc.extensions.pedro.FollowPath
```

### Basic TeleOp

```kotlin
@TeleOp(name = "My TeleOp")
class MyTeleOp : NextFTCOpMode() {
    init {
        addComponents(
            BulkReadComponent,
            BindingsComponent,
            PedroComponent(Constants::createFollower)
        )
    }

    override fun onStartButtonPressed() {
        // Field-centric driving
        PedroDriverControlled(
            Gamepads.gamepad1.leftStickY,
            Gamepads.gamepad1.leftStickX,
            Gamepads.gamepad1.rightStickX,
            false  // field-centric
        )()

        // Button bindings
        Gamepads.gamepad2.a whenBecomesTrue LiftCommand()
    }
}
```

### Basic Autonomous

```kotlin
@Autonomous(name = "My Auto")
class MyAuto : NextFTCOpMode() {
    init {
        addComponents(
            BulkReadComponent,
            PedroComponent(Constants::createFollower)
        )
    }

    override fun onStartButtonPressed() {
        SequentialGroup(
            FollowPath(path1, holdEnd = true),
            Delay(0.5.seconds),
            FollowPath(path2, holdEnd = true)
        )()
    }
}
```

## Core Concepts

| Concept | Description |
|---------|-------------|
| **Commands** | Units of code that execute (start, update, stop, isDone) |
| **Subsystems** | Collections of hardware + commands for a mechanism |
| **Components** | Modular lifecycle hooks added to OpModes |
| **Command Groups** | Sequential or parallel execution of commands |

## Components

Components are modular lifecycle hooks with pre/post methods for **all** OpMode phases:

| OpMode Phase | Component Methods |
|--------------|-------------------|
| `onInit()` | `preInit()` / `postInit()` |
| `onWaitForStart()` | `preWaitForStart()` / `postWaitForStart()` |
| `onStartButtonPressed()` | `preStartButtonPressed()` / `postStartButtonPressed()` |
| `onUpdate()` | `preUpdate()` / `postUpdate()` |
| `onStop()` | `preStop()` / `postStop()` |

Add to OpModes via `addComponents()`:

| Component | Purpose |
|-----------|---------|
| `BulkReadComponent` | Efficient hardware reads |
| `BindingsComponent` | Enable gamepad bindings |
| `SubsystemComponent(...)` | Register subsystems |
| `PedroComponent(factory)` | Pedro Pathing integration |

See [COMPONENTS.md](COMPONENTS.md) for full lifecycle details.

## Command Scheduling

```kotlin
// Schedule a command
myCommand()                           // Shorthand
CommandManager.scheduleCommand(cmd)   // Explicit

// Command groups
SequentialGroup(cmd1, cmd2, cmd3)()   // Run in order
ParallelGroup(cmd1, cmd2)()           // Run simultaneously

// Delays (inside SequentialGroup)
Delay(0.5.seconds)
```

## Reference Documentation

- [COMPONENTS.md](COMPONENTS.md) - Component lifecycle (pre/post hooks for all phases)
- [COMMANDS.md](COMMANDS.md) - Command lifecycle and creation
- [SUBSYSTEMS.md](SUBSYSTEMS.md) - Subsystem patterns
- [BINDINGS.md](BINDINGS.md) - Gamepad binding syntax
- [PEDRO_EXTENSION.md](PEDRO_EXTENSION.md) - Path following
- [HARDWARE.md](HARDWARE.md) - Motor/servo wrappers
- [CONTROL.md](CONTROL.md) - PID and feedforward

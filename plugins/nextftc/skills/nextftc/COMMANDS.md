# NextFTC Commands

Commands are units of code that execute with a defined lifecycle.

## Imports

```kotlin
import dev.nextftc.core.commands.Command
import dev.nextftc.core.commands.utility.LambdaCommand
import dev.nextftc.core.commands.utility.InstantCommand
import dev.nextftc.core.commands.groups.SequentialGroup
import dev.nextftc.core.commands.groups.ParallelGroup
import dev.nextftc.core.commands.delays.Delay
```

## Command Lifecycle

```
schedule() → start() → update() (repeats) → isDone=true → stop()
```

| Method | When Called | Purpose |
|--------|-------------|---------|
| `start()` | Once when scheduled | Initialize state |
| `update()` | Every loop iteration | Main logic (keep fast!) |
| `isDone` | Every loop | Return true to end command |
| `stop(interrupted)` | Once when ending | Cleanup; `interrupted=true` if cancelled |

## Creating Commands

### Lambda Commands (Preferred for simple commands)

```kotlin
val myCommand = LambdaCommand()
    .setStart { /* initialization */ }
    .setUpdate { /* loop logic */ }
    .setStop { interrupted -> /* cleanup */ }
    .setIsDone { someCondition }
    .requires(mySubsystem)
    .setInterruptible(true)
    .named("My Command")
```

All methods are optional. Call in any order.

### Class-Based Commands (For reusable commands)

```kotlin
class MyCommand : Command() {
    init {
        requires(MySubsystem)
        setInterruptible(true)
    }

    override val isDone: Boolean
        get() = false  // Never ends until interrupted

    override fun start() {
        // Initialize
    }

    override fun update() {
        // Loop logic - keep this fast!
    }

    override fun stop(interrupted: Boolean) {
        // Cleanup
    }
}
```

## Command Properties

| Property | Default | Description |
|----------|---------|-------------|
| `interruptible` | true | Can another command interrupt this one? |
| `requirements` | empty | Subsystems this command uses |
| `name` | class name | For debugging/telemetry |

## Scheduling Commands

```kotlin
// Shorthand - calls CommandManager.scheduleCommand()
myCommand()

// Explicit scheduling
CommandManager.scheduleCommand(myCommand)
```

## Command Groups

### SequentialGroup

Runs commands one after another:

```kotlin
SequentialGroup(
    FirstCommand(),
    SecondCommand(),
    ThirdCommand()
)()
```

### ParallelGroup

Runs commands simultaneously:

```kotlin
ParallelGroup(
    LiftToHigh(),
    OpenClaw()
)()
```

### Combining Groups

```kotlin
SequentialGroup(
    FollowPath(path1),
    ParallelGroup(
        LiftToHigh(),
        OpenClaw()
    ),
    Delay(0.5.seconds),
    CloseClaw()
)()
```

## Delays

**Important**: Delays should almost always be inside SequentialGroups.

```kotlin
import kotlin.time.Duration.Companion.seconds

SequentialGroup(
    SomeCommand(),
    Delay(0.5.seconds),  // Wait 500ms
    NextCommand()
)()
```

## Debugging

```kotlin
// Name commands for telemetry
myCommand.named("Descriptive Name")

// Access telemetry in commands
override fun update() {
    ActiveOpMode.telemetry.addData("State", currentState)
    ActiveOpMode.telemetry.update()  // REQUIRED after adding telemetry
}

// View active commands
CommandManager.snapshot  // Returns list of active command names
```

## Requirements Pattern

Commands with requirements prevent conflicts:

```kotlin
class LiftUp : Command() {
    init {
        requires(LiftSubsystem)  // Only one lift command at a time
    }
}

class LiftDown : Command() {
    init {
        requires(LiftSubsystem)  // Will cancel LiftUp if scheduled
    }
}
```

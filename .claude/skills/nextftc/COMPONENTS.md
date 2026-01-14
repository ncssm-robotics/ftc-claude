# NextFTC Components

Components are modular lifecycle hooks that integrate with OpModes. They provide pre- and post- hooks for **all** OpMode phases.

## Component Lifecycle

Components have 10 override methods - pre and post for each OpMode phase:

| OpMode Phase | Pre Method | Post Method |
|--------------|------------|-------------|
| `onInit()` | `preInit()` | `postInit()` |
| `onWaitForStart()` | `preWaitForStart()` | `postWaitForStart()` |
| `onStartButtonPressed()` | `preStartButtonPressed()` | `postStartButtonPressed()` |
| `onUpdate()` | `preUpdate()` | `postUpdate()` |
| `onStop()` | `preStop()` | `postStop()` |

**Execution Order:**
- Pre-functions are called in the order components are added
- Post-functions are called in reverse order

## Creating a Component

```kotlin
object MyComponent : Component {

    override fun preInit() {
        // Called before onInit()
    }

    override fun postInit() {
        // Called after onInit() - initialize hardware here
    }

    override fun preWaitForStart() {
        // Called before each onWaitForStart() iteration
    }

    override fun postWaitForStart() {
        // Called after each onWaitForStart() iteration
        // Use this for init loop updates (vision, sensors, etc.)
    }

    override fun preStartButtonPressed() {
        // Called before onStartButtonPressed()
    }

    override fun postStartButtonPressed() {
        // Called after onStartButtonPressed()
    }

    override fun preUpdate() {
        // Called before each onUpdate() loop
    }

    override fun postUpdate() {
        // Called after each onUpdate() loop
    }

    override fun preStop() {
        // Called before onStop()
    }

    override fun postStop() {
        // Called after onStop() - cleanup here
    }
}
```

## Registering Components

Add components in the OpMode's `init` block:

```kotlin
@TeleOp(name = "My TeleOp")
class MyTeleOp : NextFTCOpMode() {
    init {
        addComponents(
            BulkReadComponent,      // Efficient hardware reads
            BindingsComponent,       // Enable gamepad bindings
            MyCustomComponent,       // Your custom component
            PedroComponent(...)      // Pedro Pathing
        )
    }
}
```

## Built-in Components

| Component | Purpose |
|-----------|---------|
| `BulkReadComponent` | Efficient bulk hardware reads |
| `BindingsComponent` | Enable Gamepads bindings |
| `SubsystemComponent(...)` | Register subsystems |
| `PedroComponent(factory)` | Pedro Pathing integration |

## Common Patterns

### Init Loop Processing

Use `postWaitForStart()` for processing during the init loop:

```kotlin
object VisionComponent : Component {
    override fun postInit() {
        // Initialize camera
        camera = hardwareMap.get(...)
    }

    override fun postWaitForStart() {
        // Update detection during init loop
        latestResult = camera.getLatestResult()
    }

    override fun postUpdate() {
        // Update during main loop
        latestResult = camera.getLatestResult()
    }
}
```

### Hardware Access

Use `ActiveOpMode` to access hardware and telemetry:

```kotlin
override fun postInit() {
    val motor = ActiveOpMode.hardwareMap.get(DcMotor::class.java, "motor")
    ActiveOpMode.telemetry.addData("Status", "Initialized")
    ActiveOpMode.telemetry.update()  // REQUIRED after adding telemetry
}
```

## Important Notes

- Components are registered at OpMode creation time
- All 10 lifecycle methods run automatically - no manual calls needed
- `postWaitForStart()` runs every iteration of the init loop (before start is pressed)
- Gamepad bindings set up in `onInit()` or `onStartButtonPressed()` work in both phases

---
description: List available OpModes on the robot
argument-hint: [--auto | --teleop]
allowed-tools: Bash(uv:*), Bash(adb:*)
---

# OpModes Command

Lists all available OpModes on the connected robot.

## Usage

```
/opmodes            # List all OpModes
/opmodes --auto     # List Autonomous only
/opmodes --teleop   # List TeleOp only
```

## Arguments

| Argument | Description |
|----------|-------------|
| `--auto` | Show only Autonomous OpModes |
| `--teleop` | Show only TeleOp OpModes |

## Process

When this command runs:

1. **Check connection:**
   ```bash
   adb devices
   ```

2. **Query Panels via websocket:**
   ```bash
   uv run scripts/panels_client.py list
   ```

   The script connects to `ws://192.168.43.1:8001/ws` and requests the OpMode list.

3. **Parse and display results**

## Expected Output

```
Available OpModes
──────────────────────────────────────────────

Autonomous:
  1. Auto Left
  2. Auto Right
  3. Auto Center

TeleOp:
  4. TeleOp Main
  5. TeleOp Practice
  6. PID Tuner

To run an OpMode:
  /init "TeleOp Main"
  /start
```

## Filtered Output

### Autonomous Only

```
/opmodes --auto

Autonomous OpModes
──────────────────────────────────────────────

  1. Auto Left
  2. Auto Right
  3. Auto Center
```

### TeleOp Only

```
/opmodes --teleop

TeleOp OpModes
──────────────────────────────────────────────

  1. TeleOp Main
  2. TeleOp Practice
  3. PID Tuner
```

## Error Handling

### Not Connected

```
/opmodes

  ✗ Robot not connected

  Run /connect first, then try again.
```

### Dashboard Not Available

```
/opmodes

  ✗ Cannot reach dashboard

  The OpMode list requires a dashboard connection.

  Check:
  1. Robot Controller app is running
  2. Panels (port 8001) or FTC Dashboard (port 8080) is enabled

  Alternative: View OpModes on the Driver Station app
```

### No OpModes Found

```
/opmodes

  No OpModes found.

  This could mean:
  1. No code has been deployed yet (/deploy)
  2. OpModes are missing @TeleOp or @Autonomous annotations
  3. Build errors prevented OpMode registration
```

## Tips

### OpMode Naming

Good OpMode names:
- `Auto Left` - Clear starting position
- `TeleOp Main` - Primary teleop
- `PID Tuner` - Specific purpose

### Finding OpModes in Code

OpModes need annotations:
```java
@Autonomous(name = "Auto Left", group = "Competition")
public class AutoLeft extends LinearOpMode { }

@TeleOp(name = "TeleOp Main", group = "Competition")
public class TeleOpMain extends LinearOpMode { }
```

### After Listing

To run an OpMode:
1. `/init "OpMode Name"` - Initialize it
2. `/start` - Start running
3. `/stop` - Stop when done

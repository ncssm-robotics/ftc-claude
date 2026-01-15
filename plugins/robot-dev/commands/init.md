---
description: Initialize an OpMode on the robot
argument-hint: <opmode-name>
allowed-tools: Bash(uv:*), Bash(adb:*)
---

# Init Command

Selects and initializes an OpMode on the robot.

## Usage

```
/init "TeleOp Main"      # Initialize by exact name
/init TeleOp             # Initialize by partial match
/init 3                  # Initialize by number (from /opmodes list)
```

## Arguments

| Argument | Description |
|----------|-------------|
| `<opmode-name>` | Name of OpMode to initialize (full or partial) |

## Process

When this command runs:

1. **Check connection:**
   ```bash
   adb devices
   ```

2. **Find OpMode:**
   - If number given, look up from recent `/opmodes` list
   - If name given, find matching OpMode (partial match OK)
   - If multiple matches, prompt user to choose

3. **Send init command via websocket:**
   ```bash
   uv run scripts/panels_client.py init "TeleOp Main"
   ```

   This sends the `initOpMode` message with the OpMode name.

4. **Update HUD:**
   ```
   🤖 Connected (12.4V) │ TeleOp Main [INIT] │ 192.168.43.1
   ```

## Expected Output

```
Initializing OpMode...

  ✓ Found: "TeleOp Main"
  ✓ Initialized

  Status: TeleOp Main [INIT]

  Next: /start to begin running
```

## Partial Matching

The command supports partial name matching:

```
/init teleop

  Found multiple matches:
    1. TeleOp Main
    2. TeleOp Practice
    3. TeleOp Debug

  Which one? (enter number): 1

  ✓ Initialized "TeleOp Main"
```

## Error Handling

### Not Connected

```
/init TeleOp

  ✗ Robot not connected

  Run /connect first, then try again.
```

### OpMode Not Found

```
/init MyOpMode

  ✗ OpMode "MyOpMode" not found

  Available OpModes:
    - TeleOp Main
    - TeleOp Practice
    - Auto Left

  Try: /opmodes to see full list
```

### Dashboard Not Available

```
/init TeleOp

  ✗ Cannot reach dashboard

  OpMode control requires Panels or FTC Dashboard.

  Alternative: Use the Driver Station app to init the OpMode.
```

### Already Running

```
/init TeleOp

  ⚠ OpMode "Auto Left" is currently running

  Stop it first:
    /stop

  Then init the new OpMode.
```

## OpMode States

After `/init`, the OpMode is in **INIT** state:
- Robot hardware is initialized
- `init()` method has run
- Waiting for start signal

State flow:
```
(none) → /init → [INIT] → /start → [RUNNING] → /stop → [STOPPED]
```

## Tips

### Quick Init by Number

After running `/opmodes`, you can init by number:
```
/opmodes
  1. Auto Left
  2. TeleOp Main

/init 2    # Inits "TeleOp Main"
```

### Re-initializing

To restart an OpMode from the beginning:
```
/stop
/init "Same OpMode"
/start
```

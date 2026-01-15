---
description: Start the initialized OpMode
allowed-tools: Bash(uv:*), Bash(adb:*)
---

# Start Command

Starts the currently initialized OpMode.

## Usage

```
/start
```

## Process

When this command runs:

1. **Check OpMode is initialized:**
   - Query dashboard for current state
   - Must be in `INIT` state

2. **Send start command via websocket:**
   ```bash
   uv run scripts/panels_client.py start
   ```

   This sends the `startActiveOpMode` message.

3. **Update HUD:**
   ```
   🤖 Connected (12.4V) │ TeleOp Main [RUNNING] │ 192.168.43.1
   ```

## Expected Output

```
Starting OpMode...

  OpMode: TeleOp Main
  ✓ Started

  Status: TeleOp Main [RUNNING]

  Use /stop to stop the OpMode
```

## Error Handling

### No OpMode Initialized

```
/start

  ✗ No OpMode initialized

  Initialize an OpMode first:
    /opmodes         # List available OpModes
    /init "TeleOp"   # Initialize one
    /start           # Then start it
```

### Already Running

```
/start

  ⚠ OpMode already running

  Current: TeleOp Main [RUNNING]

  To restart:
    /stop
    /init "TeleOp Main"
    /start
```

### Not Connected

```
/start

  ✗ Robot not connected

  Run /connect first, then try again.
```

### Dashboard Not Available

```
/start

  ✗ Cannot reach dashboard

  OpMode control requires Panels or FTC Dashboard.

  Alternative: Press the Start button on the Driver Station.
```

## State Transitions

```
[INIT] → /start → [RUNNING]
```

The OpMode's `start()` method is called, then `loop()` begins executing.

## Tips

### Autonomous vs TeleOp

For **Autonomous** OpModes:
- The OpMode runs until completion or `/stop`
- Timer starts when you run `/start`

For **TeleOp** OpModes:
- Gamepad input is active after `/start`
- Runs until `/stop` or 2-minute timer

### Quick Start Sequence

```
/init Auto Left
/start
```

Or with safety check:
```
/opmodes                  # See what's available
/init "Auto Left"         # Initialize
/start                    # Go!
```

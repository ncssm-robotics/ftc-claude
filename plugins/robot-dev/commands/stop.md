---
description: Stop the running OpMode
allowed-tools: Bash(uv:*), Bash(adb:*)
---

# Stop Command

Stops the currently running OpMode.

## Usage

```
/stop
```

## Process

When this command runs:

1. **Check OpMode is running:**
   - Query dashboard for current state
   - Should be in `RUNNING` state

2. **Send stop command via websocket:**
   ```bash
   uv run scripts/panels_client.py stop
   ```

   This sends the `stopActiveOpMode` message.

3. **Update HUD:**
   ```
   🤖 Connected (12.4V) │ TeleOp Main [STOPPED] │ 192.168.43.1
   ```

## Expected Output

```
Stopping OpMode...

  OpMode: TeleOp Main
  ✓ Stopped

  Status: TeleOp Main [STOPPED]

  To run again:
    /init "TeleOp Main"
    /start
```

## Error Handling

### No OpMode Running

```
/stop

  ⚠ No OpMode currently running

  Nothing to stop.
```

### Not Connected

```
/stop

  ✗ Robot not connected

  Run /connect first, then try again.
```

### Dashboard Not Available

```
/stop

  ✗ Cannot reach dashboard

  OpMode control requires Panels or FTC Dashboard.

  Alternative: Press the Stop button on the Driver Station.
```

## State Transitions

```
[RUNNING] → /stop → [STOPPED]
```

The OpMode's `stop()` method is called:
- Motors are stopped
- Resources are cleaned up
- OpMode becomes inactive

## After Stopping

After `/stop`, you can:

1. **Run the same OpMode again:**
   ```
   /init "Same OpMode"
   /start
   ```

2. **Switch to a different OpMode:**
   ```
   /init "Different OpMode"
   /start
   ```

3. **Check logs for issues:**
   ```
   /log --errors
   ```

## Tips

### Emergency Stop

If the robot is behaving unexpectedly, `/stop` immediately stops the OpMode.

For a hardware emergency:
- Press the physical E-Stop button on the robot
- Or power off the robot

### Graceful Shutdown

Your OpMode's `stop()` method is called when `/stop` runs. Use it to:
```java
@Override
public void stop() {
    // Set motors to zero
    leftMotor.setPower(0);
    rightMotor.setPower(0);

    // Close any resources
    camera.close();
}
```

### Viewing What Happened

After stopping, check the logs:
```
/log --errors
```

This shows any errors or crashes that occurred during the run.

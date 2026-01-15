---
description: View filtered robot logs (logcat)
argument-hint: [--filter <tag>] [--errors] [-f] [--clear]
allowed-tools: Bash(adb:*)
---

# Log Command

View robot logs with FTC-relevant filtering.

## Usage

```
/log                    # View recent logs
/log -f                 # Follow logs in real-time
/log --errors           # Show only errors
/log --filter TeamCode  # Filter by tag
/log --clear            # Clear log buffer first
```

## Arguments

| Argument | Description |
|----------|-------------|
| `-f`, `--follow` | Continuous output (like tail -f) |
| `--errors` | Show only errors and exceptions |
| `--filter <tag>` | Filter to specific tag (e.g., TeamCode, RobotCore) |
| `--clear` | Clear log buffer before reading |
| `--since <time>` | Show logs from last N minutes (e.g., `--since 5m`) |

## Process

When this command runs:

1. **Check connection:**
   ```bash
   adb devices
   ```

2. **Clear buffer** (if `--clear`):
   ```bash
   adb logcat -c
   ```

3. **Run logcat with filters:**

   Default (FTC-relevant):
   ```bash
   adb logcat -v time RobotCore:* FtcRobotController:* TeamCode:* AndroidRuntime:E *:S
   ```

   Errors only:
   ```bash
   adb logcat -v time *:E
   ```

   Custom filter:
   ```bash
   adb logcat -v time <TAG>:* *:S
   ```

4. **Format and colorize output:**
   - Errors: Red
   - Warnings: Yellow
   - Info: Default
   - Debug: Gray

## Output Format

```
Robot Logs (Ctrl+C to exit)
──────────────────────────────────────────────

12:34:56.789 [INFO]  RobotCore: OpMode 'TeleOp Test' initialized
12:34:56.823 [INFO]  TeamCode: Motor initialized
12:34:57.001 [WARN]  RobotCore: Battery voltage: 11.8V
12:34:57.234 [INFO]  TeamCode: Position: x=12.5, y=24.3
12:35:01.456 [ERROR] AndroidRuntime: FATAL EXCEPTION
                     java.lang.NullPointerException
                       at MyOpMode.loop(MyOpMode.java:45)
```

## Common Filters

### Your Code Only
```
/log --filter TeamCode
```

### Hardware Issues
```
/log --filter RobotCore
```

### Vision/Camera
```
/log --filter Limelight
/log --filter OpenCV
```

### Crashes Only
```
/log --filter AndroidRuntime --errors
```

## Error Handling

### Not Connected

```
/log

  ✗ Robot not connected

  Run /connect first, then try again.
```

### No Logs Available

```
/log

  No logs matching filter.

  Try:
  - Run your OpMode to generate logs
  - Use a different filter: /log --filter RobotCore
  - Clear and retry: /log --clear
```

## Tips

### Finding Crashes

When your OpMode crashes, look for:
```
/log --errors
```

The crash shows:
- Exception type (NullPointerException, etc.)
- File and line number
- Stack trace

### Adding Your Own Logs

In your OpMode code:
```java
// These show up in /log --filter TeamCode
telemetry.addData("Debug", "Motor power: " + power);
telemetry.update();
```

Or use Android logging:
```java
import android.util.Log;

Log.d("TeamCode", "Debug message");
Log.w("TeamCode", "Warning message");
Log.e("TeamCode", "Error message");
```

### Saving Logs

To save logs to a file:
```bash
adb logcat -d > robot_logs.txt
```

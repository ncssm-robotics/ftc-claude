---
description: Check FTC development environment setup (ADB, uv, connection, Gradle)
argument-hint: [--fix]
allowed-tools: Bash(adb:*), Bash(uv:*), Bash(which:*), Bash(command:*), Bash(brew:*), Bash(curl:*), Bash(ping:*), Read, Glob
---

# Doctor Command

Diagnoses your FTC development environment and helps fix issues.

## Usage

```
/doctor          # Check environment
/doctor --fix    # Attempt automatic fixes
```

## What It Checks

1. **ADB Installation**
   - Is `adb` command available?
   - What version is installed?

2. **uv (Python runner)**
   - Is `uv` command available?
   - Required for OpMode control and future plugins

3. **Robot Reachability**
   - Can we ping the robot (192.168.43.1)?
   - Is the robot's ADB port accessible?

4. **Gradle Setup**
   - Does `gradlew` exist in the project?
   - Is it executable?

5. **Project Structure**
   - Is this an FTC project (has TeamCode)?
   - Is local.properties configured?

## Process

When this command runs:

1. **Detect platform** (macOS, Linux, Windows)

2. **Check ADB:**
   ```bash
   command -v adb
   adb version
   ```

   If missing, show platform-specific install instructions:
   - macOS: `brew install android-platform-tools`
   - Linux: `sudo apt install android-tools-adb`
   - Windows: Download from developer.android.com

3. **Check uv:**
   ```bash
   command -v uv
   uv --version
   ```

   If missing, show platform-specific install instructions:
   - macOS/Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - Windows: `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`

4. **Check robot connection:**
   ```bash
   ping -c 1 -W 2 192.168.43.1
   adb devices
   ```

5. **Check Gradle:**
   ```bash
   ls -la gradlew
   ./gradlew --version
   ```

6. **Check project:**
   - Look for `TeamCode/` directory
   - Check `local.properties` exists

## Output Format

```
FTC Development Environment Check

  Platform: macOS 14.0

  ADB:
    ✓ Installed (version 35.0.1)
    ✓ In PATH

  uv (Python runner):
    ✓ Installed (version 0.4.x)
    ✓ In PATH

  Robot Connection:
    ✓ Network reachable (192.168.43.1)
    ✓ ADB connected

  Gradle:
    ✓ gradlew found
    ✓ Executable

  Project:
    ✓ TeamCode directory found
    ✓ local.properties configured

  Summary: 10/10 checks passed
```

## Error Messages

### ADB Not Installed

```
ADB:
  ✗ Not installed

  ADB (Android Debug Bridge) lets your computer talk to the robot.

  To install on macOS:
    brew install android-platform-tools

  Or run: /doctor --fix
```

### uv Not Installed

```
uv (Python runner):
  ✗ Not installed

  uv is needed for OpMode control (/init, /start, /stop) and
  other advanced features like PID tuning.

  To install on macOS/Linux:
    curl -LsSf https://astral.sh/uv/install.sh | sh

  To install on Windows:
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

  Or run: /doctor --fix
```

### Robot Not Reachable

```
Robot Connection:
  ✗ Cannot reach 192.168.43.1

  Checklist:
    [ ] Robot is powered on
    [ ] You're on the robot's WiFi (usually "TEAMNUMBER-RC")
    [ ] Robot WiFi is enabled

  Try: /connect --usb (use USB cable)
```

## --fix Flag

When `--fix` is provided, attempt automatic fixes:

1. **macOS - Install ADB:**
   ```bash
   brew install android-platform-tools
   ```

2. **Linux - Install ADB:**
   ```bash
   sudo apt update && sudo apt install -y android-tools-adb
   ```

3. **macOS/Linux - Install uv:**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

4. **Windows - Install uv:**
   ```powershell
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

5. **Make gradlew executable:**
   ```bash
   chmod +x gradlew
   ```

6. **Windows ADB:** Show manual instructions (can't auto-install)

Always confirm before making system changes.

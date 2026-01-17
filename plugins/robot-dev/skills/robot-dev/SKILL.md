---
name: robot-dev
description: >-
  Helps with FTC robot development workflow including building, deploying, and debugging.
  Use when connecting to robot, troubleshooting ADB, building code, deploying to Control Hub,
  viewing logs, or controlling OpModes from the command line.
license: MIT
compatibility: Claude Code, Codex CLI, VS Code Copilot, Cursor
metadata:
  author: ncssm-robotics
  version: "1.1.0"
  category: tools
---

# FTC Robot Development Tools

Commands and guidance for the FTC robot development workflow. Designed to help rookies get up and running quickly.

## Quick Start

### 1. Check Your Setup

```
/doctor
```

This checks if ADB is installed and helps you install it if needed.

### 2. Connect to Robot

```
/connect
```

Connects to your robot via WiFi (default) or USB.

### 3. Build and Deploy

```
/build    # Compile your code
/deploy   # Build and install to robot
```

### 4. Debug

```
/log              # View robot logs
/log --errors     # View only errors
```

### 5. Control OpModes

```
/opmodes          # List available OpModes
/init TeleOp      # Initialize an OpMode
/start            # Start the OpMode
/stop             # Stop the OpMode
```

## Available Commands

| Command | Description |
|---------|-------------|
| `/doctor` | Check environment setup (ADB, connection) |
| `/connect` | Connect to robot via WiFi or USB |
| `/build` | Compile robot code |
| `/deploy` | Build and deploy to robot |
| `/log` | View filtered robot logs |
| `/opmodes` | List available OpModes |
| `/init` | Initialize an OpMode |
| `/start` | Start the initialized OpMode |
| `/stop` | Stop the running OpMode |

## Connection Basics

### WiFi Connection (Recommended)

1. Power on your robot
2. Connect your computer to the robot's WiFi network (usually `TEAMNUMBER-RC`)
3. Run `/connect`

### USB Connection

1. Connect USB cable from computer to Control Hub
2. Run `/connect --usb`

### Common Issues

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for solutions to:
- "ADB not found"
- "Cannot connect to robot"
- "Deploy failed"

## Environment Setup

See [ADB_SETUP.md](ADB_SETUP.md) for platform-specific ADB installation instructions.

## Status HUD

When connected, the status line shows:
```
🤖 Connected (12.4V) │ TeleOp Test [INIT] │ 192.168.43.1
```

See [HUD.md](HUD.md) for configuration options.

## Anti-Patterns

### Don't: Skip /doctor on a new machine

```
# BAD - Jump straight to connecting
/connect  # "ADB not found" error

# GOOD - Check environment first
/doctor   # Identifies missing dependencies
/connect  # Now it works
```

### Don't: Ignore build errors and deploy anyway

```
# BAD - Deploy after build fails
/build    # Shows errors, you ignore them
/deploy   # Deploys old working code, not your changes!

# GOOD - Fix errors before deploying
/build    # Fix any errors shown
/build    # Verify clean build
/deploy   # Now your changes are deployed
```

### Don't: Forget to connect before deploying

```
# BAD - Deploy fails silently
/deploy   # "No device connected" error

# GOOD - Ensure connection first
/connect  # Establish connection
/deploy   # Deploy succeeds
```

### Don't: Debug without filtering logs

```
# BAD - Overwhelmed by system noise
/log      # Thousands of unrelated messages

# GOOD - Filter to what matters
/log --errors     # Only error messages
/log --tag=MyOp   # Only your OpMode's logs
```

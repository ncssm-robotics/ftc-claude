---
description: Build and deploy FTC code to the robot
argument-hint: [--no-build] [--wifi | --usb]
allowed-tools: Bash(./gradlew:*), Bash(gradlew.bat:*), Bash(adb:*), Bash(chmod:*), Read, Glob
---

# Deploy Command

Builds your code and installs it on the robot.

## Usage

```
/deploy              # Build and deploy
/deploy --no-build   # Deploy existing APK (skip build)
/deploy --usb        # Force USB connection
```

## Arguments

| Argument | Description |
|----------|-------------|
| `--no-build` | Skip building, deploy existing APK |
| `--wifi` | Force WiFi deployment |
| `--usb` | Force USB deployment |

## Process

When this command runs:

1. **Check connection:**
   ```bash
   adb devices
   ```
   If not connected, prompt to run `/connect`

2. **Build code** (unless `--no-build`):
   ```bash
   ./gradlew assembleDebug
   ```

3. **Install APK:**
   ```bash
   adb install -r TeamCode/build/outputs/apk/debug/TeamCode-debug.apk
   ```

4. **Restart Robot Controller:**
   ```bash
   adb shell am force-stop com.qualcomm.ftcrobotcontroller
   adb shell am start -n com.qualcomm.ftcrobotcontroller/.FtcRobotControllerActivity
   ```

5. **Verify installation:**
   - Check APK installed successfully
   - Confirm Robot Controller restarted

## Expected Output (Success)

```
Deploying to robot...

  ✓ Robot connected (192.168.43.1:5555)

  Building code...
  ✓ Build successful (12.3s)

  Installing APK...
  ✓ TeamCode-debug.apk installed

  Restarting Robot Controller...
  ✓ Robot Controller restarted

  Deploy complete!

  Open Driver Station to see your OpModes.
```

## Error Handling

### Not Connected

```
Deploying to robot...

  ✗ Robot not connected

  Run /connect first to establish a connection.

  Quick options:
    /connect        Connect via WiFi
    /connect --usb  Connect via USB cable
```

### Build Failed

```
Deploying to robot...

  ✓ Robot connected

  Building code...
  ✗ Build failed

  Error in TeleOpMode.java:45
    Cannot find symbol: variable 'motor'

  Fix the error and try again.
```

### Install Failed - Incompatible

```
Deploying to robot...

  ✓ Robot connected
  ✓ Build successful

  Installing APK...
  ✗ INSTALL_FAILED_UPDATE_INCOMPATIBLE

  The robot has a different version installed.

  Fix: Uninstall the old version first:
    adb uninstall com.qualcomm.ftcrobotcontroller

  Then run /deploy again.
```

### Install Failed - Storage

```
Deploying to robot...

  ✓ Robot connected
  ✓ Build successful

  Installing APK...
  ✗ INSTALL_FAILED_INSUFFICIENT_STORAGE

  The robot is out of storage space.

  Try:
  1. Clear app cache:
     adb shell pm trim-caches 100M

  2. Remove old builds:
     adb shell rm -rf /sdcard/FIRST/

  3. Factory reset the Control Hub (last resort)
```

### Connection Lost During Deploy

```
Deploying to robot...

  ✓ Robot connected
  ✓ Build successful

  Installing APK...
  ✗ error: device offline

  Connection lost during deployment.

  Try:
  1. Check if robot is still powered on
  2. Run /connect to reconnect
  3. Run /deploy --no-build to retry install
```

## Tips

### Faster Deploys

Use `--no-build` if you've already built and just want to re-deploy:
```
/deploy --no-build
```

### Deploy Over USB (More Reliable)

WiFi can be flaky. For important matches, deploy over USB:
```
/deploy --usb
```

### Check What's Installed

See what version is on the robot:
```bash
adb shell dumpsys package com.qualcomm.ftcrobotcontroller | grep versionName
```

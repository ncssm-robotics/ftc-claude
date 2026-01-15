---
description: Connect to FTC robot via WiFi or USB
argument-hint: [--wifi | --usb] [--ip <address>]
allowed-tools: Bash(adb:*), Bash(ping:*)
---

# Connect Command

Establishes a connection to your FTC robot.

## Usage

```
/connect              # Connect via WiFi (default)
/connect --usb        # Connect via USB cable
/connect --ip 10.0.0.1   # Connect to custom IP
```

## Arguments

| Argument | Description |
|----------|-------------|
| `--wifi` | Connect via WiFi (default) |
| `--usb` | Connect via USB cable |
| `--ip <address>` | Custom robot IP (default: 192.168.43.1) |
| `--port <port>` | Custom ADB port (default: 5555) |

## WiFi Connection (Default)

When connecting via WiFi:

1. **Check network:**
   - Verify computer is on robot's WiFi network
   - Robot network is usually `TEAMNUMBER-RC`

2. **Connect ADB:**
   ```bash
   adb connect 192.168.43.1:5555
   ```

3. **Verify:**
   ```bash
   adb devices
   ```

### Expected Output

```
Connecting to robot via WiFi...

  Connecting to 192.168.43.1:5555...
  ✓ Connected!

  Device: Control Hub
  Serial: 1234567890ABCDEF

  Run /deploy to upload your code
```

## USB Connection

When connecting via USB:

1. **Check USB:**
   ```bash
   adb devices
   ```

2. **If device found, enable wireless:**
   ```bash
   adb tcpip 5555
   ```

3. **Get device IP and connect:**
   ```bash
   adb shell ip route | grep wlan0
   adb connect <ip>:5555
   ```

### Expected Output

```
Connecting to robot via USB...

  ✓ USB device found
  ✓ Enabled TCP/IP mode
  ✓ Connected wirelessly

  You can now unplug the USB cable.
  Robot IP: 192.168.43.1

  Run /deploy to upload your code
```

## Error Handling

### No Robot Found

```
Connecting to robot via WiFi...

  ✗ Cannot reach 192.168.43.1

  Troubleshooting:
  1. Is the robot powered on?
  2. Are you on the robot's WiFi network?
     - Look for a network named "TEAMNUMBER-RC"
     - Your current network: "Home-WiFi" ← wrong network!
  3. Is the robot's WiFi enabled?
     - Check Driver Station settings

  Try: /connect --usb (use a USB cable instead)
```

### USB Device Not Found

```
Connecting to robot via USB...

  ✗ No USB device found

  Troubleshooting:
  1. Connect a USB cable from your computer to the Control Hub
  2. Use the USB-C port on the Control Hub (not the phone port)
  3. Try a different cable (some cables are charge-only)
  4. On Windows: Install USB drivers (see /doctor)

  After connecting, run /connect --usb again
```

### Device Unauthorized

```
Connecting to robot via USB...

  ✗ Device unauthorized

  The robot needs to trust your computer:
  1. Look at the robot's screen
  2. Tap "Allow" on the USB debugging prompt
  3. Check "Always allow from this computer"
  4. Run /connect --usb again

  If no prompt appears:
  1. Go to Settings > Developer Options
  2. Tap "Revoke USB debugging authorizations"
  3. Unplug and replug the USB cable
```

### Multiple Devices

```
Connecting to robot...

  ⚠ Multiple devices found:
    1. 192.168.43.1:5555 (Control Hub)
    2. emulator-5554 (Android Emulator)

  Disconnecting emulator...
  ✓ Connected to Control Hub
```

## After Connecting

Once connected, you can:

- `/build` - Compile your code
- `/deploy` - Upload code to robot
- `/log` - View robot logs
- `/opmodes` - List available OpModes

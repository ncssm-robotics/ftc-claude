# ADB Setup Guide

ADB (Android Debug Bridge) is required to communicate with your FTC robot. This guide helps you install it on any platform.

## Quick Check

Run `/doctor` to check if ADB is already installed.

## Installation by Platform

### macOS

**Option 1: Homebrew (Recommended)**
```bash
brew install android-platform-tools
```

**Option 2: Manual Download**
1. Download from https://developer.android.com/studio/releases/platform-tools
2. Extract to a folder (e.g., `~/platform-tools`)
3. Add to PATH:
   ```bash
   echo 'export PATH="$HOME/platform-tools:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```

### Linux (Ubuntu/Debian)

**Option 1: Package Manager (Recommended)**
```bash
sudo apt update
sudo apt install android-tools-adb
```

**Option 2: Manual Download**
1. Download from https://developer.android.com/studio/releases/platform-tools
2. Extract to a folder (e.g., `~/platform-tools`)
3. Add to PATH:
   ```bash
   echo 'export PATH="$HOME/platform-tools:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```

### Windows

**Manual Download (Only Option)**
1. Download from https://developer.android.com/studio/releases/platform-tools
2. Extract to `C:\platform-tools`
3. Add to PATH:
   - Press `Win + X`, select "System"
   - Click "Advanced system settings"
   - Click "Environment Variables"
   - Under "System variables", find "Path" and click "Edit"
   - Click "New" and add `C:\platform-tools`
   - Click "OK" on all windows
4. Restart your terminal

## Verify Installation

After installing, verify ADB works:

```bash
adb version
```

You should see output like:
```
Android Debug Bridge version 1.0.41
Version 35.0.1-11580240
```

## USB Drivers (Windows Only)

Windows may need USB drivers to detect the Control Hub:

1. Download from https://developer.android.com/studio/run/win-usb
2. Or install via Device Manager when you connect the Control Hub

## Troubleshooting

### "adb: command not found"

ADB is not in your PATH. Either:
- Restart your terminal after adding to PATH
- Use the full path to adb (e.g., `~/platform-tools/adb`)

### "no permissions" (Linux)

Add udev rules:
```bash
sudo usermod -aG plugdev $USER
echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="18d1", MODE="0666", GROUP="plugdev"' | sudo tee /etc/udev/rules.d/51-android.rules
sudo udevadm control --reload-rules
```

Then log out and back in.

### "device unauthorized"

1. Disconnect USB
2. On the robot, go to Settings > Developer Options > Revoke USB debugging authorizations
3. Reconnect USB
4. Accept the authorization prompt on the robot

## Next Steps

After installing ADB, run `/doctor` to verify your setup, then `/connect` to connect to your robot.

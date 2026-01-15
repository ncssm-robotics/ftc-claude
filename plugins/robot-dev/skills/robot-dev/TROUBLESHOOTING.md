# Troubleshooting Guide

Common issues and solutions for FTC robot development.

## Connection Issues

### "Cannot connect to robot"

**Checklist:**
- [ ] Robot is powered on (check if lights are on)
- [ ] You're connected to the robot's WiFi network (usually `TEAMNUMBER-RC`)
- [ ] Robot WiFi is enabled in Driver Station settings
- [ ] No other devices are connected via ADB

**Solutions:**

1. **Check WiFi network:**
   - On your computer, verify you're on the robot's network
   - The network name is usually your team number followed by `-RC`

2. **Restart robot WiFi:**
   - On Driver Station, go to Settings > WiFi > Restart

3. **Try USB instead:**
   ```
   /connect --usb
   ```

4. **Restart ADB server:**
   ```bash
   adb kill-server
   adb start-server
   ```

### "ADB not found"

ADB is not installed or not in your PATH.

**Solution:** Run `/doctor --fix` or see [ADB_SETUP.md](ADB_SETUP.md)

### "device unauthorized"

The robot hasn't authorized your computer.

**Solution:**
1. Disconnect USB cable
2. On robot, go to Settings > Developer Options
3. Tap "Revoke USB debugging authorizations"
4. Reconnect USB cable
5. Accept the authorization prompt on the robot screen

### "multiple devices/emulators"

Multiple Android devices are connected.

**Solution:**
1. Disconnect other Android devices
2. Or specify the device: `adb -s <device-id> <command>`
3. List devices with: `adb devices`

## Build Issues

### "Could not find or load main class org.gradle.wrapper.GradleWrapperMain"

Gradle wrapper files are missing or corrupted.

**Solution:**
```bash
# Delete existing wrapper
rm -rf gradle/wrapper

# Re-download (requires Gradle installed globally)
gradle wrapper
```

### "SDK location not found"

Android SDK path is not configured.

**Solution:**
1. Create `local.properties` in project root
2. Add: `sdk.dir=/path/to/android/sdk`
   - macOS: `sdk.dir=/Users/USERNAME/Library/Android/sdk`
   - Linux: `sdk.dir=/home/USERNAME/Android/Sdk`
   - Windows: `sdk.dir=C:\\Users\\USERNAME\\AppData\\Local\\Android\\Sdk`

### "Cannot find symbol" errors

Usually a typo or missing import.

**Solutions:**
1. Check spelling of variable/method names
2. Add missing imports (Android Studio can auto-import with Alt+Enter)
3. Clean and rebuild: `/build --clean`

## Deploy Issues

### "INSTALL_FAILED_UPDATE_INCOMPATIBLE"

The installed app was signed with a different key.

**Solution:**
```bash
adb uninstall com.qualcomm.ftcrobotcontroller
/deploy
```

### "INSTALL_FAILED_INSUFFICIENT_STORAGE"

Robot is out of storage space.

**Solution:**
1. Clear old APKs: `adb shell pm clear com.qualcomm.ftcrobotcontroller`
2. Remove unused apps from the Control Hub
3. Clear cache: `adb shell pm trim-caches 100M`

### "error: device offline"

USB connection dropped or robot restarted.

**Solution:**
1. Unplug and replug USB cable
2. Run `adb kill-server && adb start-server`
3. Try `/connect` again

## OpMode Issues

### "OpMode not showing up"

The OpMode isn't registered correctly.

**Checklist:**
- [ ] OpMode has `@TeleOp` or `@Autonomous` annotation
- [ ] OpMode extends `LinearOpMode` or `OpMode`
- [ ] File is in the `TeamCode` module
- [ ] No compilation errors

**Solution:**
1. Rebuild: `/build --clean`
2. Redeploy: `/deploy`
3. Restart Robot Controller app

### "NullPointerException in init()"

Usually forgetting to initialize hardware.

**Common causes:**
```java
// Wrong - motor is null
DcMotor motor;
motor.setPower(0);  // NullPointerException!

// Correct - initialize from hardwareMap
DcMotor motor;
motor = hardwareMap.get(DcMotor.class, "motor");
motor.setPower(0);
```

## Log Issues

### "logcat shows nothing"

Log buffer may be full or filtered incorrectly.

**Solutions:**
1. Clear log buffer: `/log --clear`
2. Remove filters: `adb logcat`
3. Check connection: `/connect`

### "Too much log output"

Default logcat shows everything.

**Solution:**
Use filters:
```
/log --errors          # Only errors
/log --filter TeamCode # Only your code
```

## Dashboard Issues

### "Cannot reach dashboard"

Panels or FTC Dashboard not accessible.

**Checklist:**
- [ ] Robot is connected
- [ ] Dashboard dependency is in build.gradle
- [ ] Robot Controller app is running

**Solution:**
1. Verify connection: `/connect`
2. Try direct URL in browser: `http://192.168.43.1:8001` (Panels) or `http://192.168.43.1:8080` (FTC Dashboard)
3. Restart Robot Controller app

## Still Stuck?

1. Run `/doctor` to diagnose your setup
2. Check the FTC Discord or forums
3. Ask your mentor or team lead

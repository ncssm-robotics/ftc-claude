---
description: Build FTC robot code using Gradle
argument-hint: [--clean] [--sync] [--release]
allowed-tools: Bash(./gradlew:*), Bash(gradlew.bat:*), Bash(chmod:*), Read, Glob
---

# Build Command

Compiles your FTC robot code using Gradle.

## Usage

```
/build           # Standard build (auto-syncs if needed)
/build --clean   # Clean build (fixes stale cache issues)
/build --sync    # Force dependency sync before building
/build --release # Build release variant (rarely needed)
```

## Arguments

| Argument | Description |
|----------|-------------|
| `--clean` | Run `clean` before building (fixes stale cache issues) |
| `--sync` | Force refresh dependencies before building |
| `--release` | Build release variant instead of debug |

## Process

When this command runs:

1. **Find project root:**
   - Look for `build.gradle` with FTC SDK dependency
   - Look for `TeamCode/` directory

2. **Check Gradle wrapper:**
   ```bash
   ls gradlew  # or gradlew.bat on Windows
   ```

   If not executable (Unix):
   ```bash
   chmod +x gradlew
   ```

3. **Run build:**

   Standard build (auto-syncs missing dependencies):
   ```bash
   ./gradlew assembleDebug
   ```

   With `--clean`:
   ```bash
   ./gradlew clean assembleDebug
   ```

   With `--sync` (force dependency refresh):
   ```bash
   ./gradlew --refresh-dependencies assembleDebug
   ```

   Combined `--clean --sync`:
   ```bash
   ./gradlew clean --refresh-dependencies assembleDebug
   ```

4. **Auto-detect sync needed:**
   - If build fails with dependency errors, suggest `--sync`
   - If `build.gradle` was recently modified, offer to sync

5. **Parse output:**
   - Look for errors and warnings
   - Extract file:line information
   - Provide helpful suggestions

## Expected Output (Success)

```
Building robot code...

  Compiling TeamCode...
  ✓ Build successful (14.2s)

  Output: TeamCode/build/outputs/apk/debug/TeamCode-debug.apk

  Next: /deploy to upload to robot
```

## Error Handling

### Compilation Error

```
Building robot code...

  ✗ Build failed

  Error in TeleOpMode.java:45
  ┌─────────────────────────────────────────────
  │ 43:     public void init() {
  │ 44:         motor = hardwareMap.get(DcMotor.class, "motor");
  │ 45:         motor.setPower(speed);
  │                           ^^^^^
  │ 46:     }
  └─────────────────────────────────────────────
  Cannot find symbol: variable 'speed'

  Suggestions:
  - Did you mean to define 'speed' as a variable?
  - Or use a literal value like motor.setPower(0.5)?
```

### Missing Import

```
Building robot code...

  ✗ Build failed

  Error in TeleOpMode.java:12
  ┌─────────────────────────────────────────────
  │ 12:     DcMotorEx motor;
  │         ^^^^^^^^^
  └─────────────────────────────────────────────
  Cannot find symbol: class DcMotorEx

  Suggestion: Add this import at the top of your file:
    import com.qualcomm.robotcore.hardware.DcMotorEx;
```

### Gradle Not Found

```
Building robot code...

  ✗ Gradle wrapper not found

  This doesn't look like an FTC project directory.

  Make sure you're in the right folder:
  - Should contain gradlew (or gradlew.bat)
  - Should have a TeamCode/ directory

  Current directory: /Users/you/Documents

  Try: cd /path/to/your/ftc/project
```

### SDK Not Configured

```
Building robot code...

  ✗ Android SDK not found

  The project doesn't know where your Android SDK is.

  Create local.properties in the project root with:
    sdk.dir=/Users/YOU/Library/Android/sdk

  Or run Android Studio once - it creates this automatically.
```

## Tips

### First Build is Slow

The first build downloads dependencies and can take 2-5 minutes. Subsequent builds are much faster (10-30 seconds).

### "Build successful" but old code runs

Try a clean build:
```
/build --clean
```

### When to Use --sync

Use `/build --sync` when:
- You changed dependencies in `build.gradle`
- Getting "Could not resolve" or "Failed to resolve" errors
- Gradle cache seems corrupted
- Switching between FTC SDK versions

```
/build --sync
```

### Gradle daemon issues

If builds hang or fail mysteriously:
```bash
./gradlew --stop
/build
```

### Dependency Conflicts

If you see version conflict errors:
```
/build --clean --sync
```

This clears all caches and re-downloads everything.

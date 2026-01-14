# Pedro Pathing Tuning Process

Five sequential steps required before operational use.

## Prerequisites

- Omnidirectional drive (mecanum, x-drive, or swerve)
- Localization system (Pinpoint, dead wheels, OTOS, or drive encoders)
- Android Studio (not compatible with OnBot Java/Blocks)

## The Five Steps

### 1. Setup
Configure basic constants in `Constants.java`:
- Robot mass (kg)
- Motor names matching hardware configuration
- Motor directions (typically one side reversed)
- Localizer selection

### 2. Localization
Tune your chosen localizer. Test with:
1. Run `Tuning` OpMode > `Localization Test`
2. Connect to dashboard at `192.168.43.1:8001`
3. Verify: forward = +X, left strafe = +Y

### 3. Automatic Tuners
Run four OpModes to determine robot-specific constants:
- Forward zero power acceleration
- Lateral zero power acceleration
- X velocity
- Y velocity

### 4. PID Tuners
Tune 3-6 PID controllers:
- **Translational PID**: Corrects lateral path deviation
- **Heading PID**: Maintains robot orientation
- **Drive PID**: Controls acceleration/braking along path

### 5. Centripetal Force Tuner
Tune constant that compensates for centripetal force during curves.

## Tuning OpMode

Located at `edu.ncssm.aperture.pedro.Tuning.java` - provides menus for:
- Localization testing (Forward/Lateral/Turn)
- Automatic velocity tuning
- Manual PIDF adjustment
- Path testing (Line, Triangle, Circle)

## Dashboard

Access at `192.168.43.1:8001` when connected to robot WiFi for:
- Real-time position visualization
- Telemetry graphs
- Parameter adjustment

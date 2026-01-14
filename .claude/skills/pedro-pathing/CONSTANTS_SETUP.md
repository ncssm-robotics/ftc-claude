# Constants Setup

Configuration in `edu.ncssm.aperture.pedro.Constants.java`

## FollowerConstants

```java
public static FollowerConstants followerConstants = new FollowerConstants()
    .mass(6.8)  // Robot mass in kg
    .forwardZeroPowerAcceleration(-43.74)   // From automatic tuners
    .lateralZeroPowerAcceleration(-56.56)   // From automatic tuners
    .translationalPIDFCoefficients(new PIDFCoefficients(0.15, 0.001, 0.01, 0))
    .headingPIDFCoefficients(new PIDFCoefficients(2.0, 0.0, 0.01, 0.01));
```

## MecanumConstants

```java
public static MecanumConstants driveConstants = new MecanumConstants()
    .maxPower(1)                    // 0-1 power limit
    .rightFrontMotorName("rf")      // Hardware map names
    .rightRearMotorName("rr")
    .leftRearMotorName("lr")
    .leftFrontMotorName("lf")
    .leftFrontMotorDirection(DcMotorSimple.Direction.REVERSE)
    .leftRearMotorDirection(DcMotorSimple.Direction.REVERSE)
    .rightFrontMotorDirection(DcMotorSimple.Direction.FORWARD)
    .rightRearMotorDirection(DcMotorSimple.Direction.FORWARD)
    .xVelocity(81.55)               // From velocity tuning
    .yVelocity(55.6);               // From velocity tuning
```

## Pinpoint Localizer (Current Setup)

```java
public static PinpointConstants localizerConstants = new PinpointConstants()
    .forwardPodY(0)                 // Forward pod Y offset from center
    .strafePodX(-4)                 // Strafe pod X offset from center
    .hardwareMapName("pinpoint")
    .encoderResolution(GoBildaPinpointDriver.GoBildaOdometryPods.goBILDA_4_BAR_POD)
    .forwardEncoderDirection(GoBildaPinpointDriver.EncoderDirection.REVERSED)
    .strafeEncoderDirection(GoBildaPinpointDriver.EncoderDirection.FORWARD)
    .yawScalar(Math.PI / 3.16744 * Math.PI / 3.10675);
```

## Creating Follower

```java
public static Follower createFollower(HardwareMap hardwareMap) {
    return new FollowerBuilder(followerConstants, hardwareMap)
        .pathConstraints(pathConstraints)
        .mecanumDrivetrain(driveConstants)
        .pinpointLocalizer(localizerConstants)
        .build();
}
```

## Other Localizer Options

- `.driveEncoderLocalizer()` - Uses drive motor encoders
- `.twoWheelLocalizer()` - Two dead wheels
- `.threeWheelLocalizer()` - Three dead wheels
- `.threeWheelIMULocalizer()` - Three wheels + IMU
- `.otosLocalizer()` - SparkFun OTOS sensor

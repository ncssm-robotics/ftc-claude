# DECODE Strategy Guide

## Autonomous Priorities

### Phase 1: Preload Score (0-10s)
1. Drive to scoring position
2. Score preloaded artifacts
3. Maximum points for minimal risk

### Phase 2: Cycle (10-25s)
1. Collect nearby artifacts (up to 3)
2. Drive to scoring zone
3. Score all collected artifacts

### Phase 3: Positioning (25-30s)
1. End in advantageous position for teleop
2. Face scoring zone if possible
3. Clear of alliance partner path

## Autonomous Path Example

```kotlin
// Score preload and 2 additional artifacts
SequentialGroup(
    // Drive to first scoring position
    FollowPath(scorePreload, holdEnd = true),

    // Score preloaded artifacts
    ParallelGroup(
        ShooterSubsystem.spinUpHigh,
        ShooterSubsystem.aimAtTarget(VisionComponent.tx)
    ),
    IndexerSubsystem.kickAll,

    // Grab more artifacts
    FollowPath(grabPickup1, holdEnd = true),
    IntakeSubsystem.intake,  // While stationary
    Delay(1.seconds),

    // Score second batch
    FollowPath(scorePickup1, holdEnd = true),
    IndexerSubsystem.kickAll,

    // End in position
    FollowPath(parkPath, holdEnd = true)
)()
```

## Teleop Strategy

### Driver Controls (Gamepad 1)
- Left stick: Strafe/drive
- Right stick: Rotation
- Field-centric recommended

### Operator Controls (Gamepad 2)
- A: Intake
- B: Outtake
- X: Low goal shot
- Y: High goal shot
- LB/RB: Hood adjust
- LT/RT: Turret manual override

### Cycle Flow

```
1. INTAKE
   - Drive toward artifacts
   - Hold intake button
   - Collect up to 3

2. DRIVE TO GOAL
   - Use vision auto-aim
   - Spin up flywheel during transit

3. SCORE
   - Wait for flywheel ready
   - Kick artifacts sequentially
   - Verify shots landed

4. REPEAT
   - Return for next cycle
   - Coordinate with partner
```

## End Game Strategy

### Last 30 Seconds
- Complete current cycle
- Don't start new cycle after ~15s remaining
- Focus on parking bonus
- Avoid penalties

### Risk Management
- Don't exceed 3-artifact limit
- Clear scoring zone for partner
- Watch for clock

## Vision Integration

### Auto-Aim Flow

```kotlin
// Continuous aiming during teleop
fun aimLoop() {
    if (VisionComponent.hasTarget) {
        val tx = VisionComponent.tx
        ShooterSubsystem.aimAtTarget(tx)()

        // Calculate distance for hood
        val ty = VisionComponent.ty
        val distance = calculateDistance(ty)
        ShooterSubsystem.setHoodPosition(distanceToHood(distance))()
    }
}
```

### Localization Correction

```kotlin
// Correct odometry drift periodically
fun correctPose() {
    val visionPose = VisionComponent.botPose?.let {
        CoordinateConversion.botposeToPedro(it)
    }

    visionPose?.let { vision ->
        val odometry = PedroComponent.follower.pose

        // Only correct if we have good vision data
        if (VisionComponent.fiducials.size >= 2) {
            // Weighted average
            val correctedX = odometry.x * 0.7 + vision.x * 0.3
            val correctedY = odometry.y * 0.7 + vision.y * 0.3

            PedroComponent.follower.pose = Pose(
                correctedX, correctedY, odometry.heading
            )
        }
    }
}
```

## Alliance Coordination

### Communication
- Call out when shooting
- Announce intake position
- Signal end game parking

### Field Division
- Typically split field in half
- One robot near, one robot far
- Switch if one is more efficient

### Avoid Interference
- Don't block partner's shots
- Coordinate artifact pickup
- Stagger scoring windows

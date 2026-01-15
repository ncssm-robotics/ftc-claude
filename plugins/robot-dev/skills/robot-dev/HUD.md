# Robot Status HUD

The robot-dev plugin includes a status HUD that shows real-time robot information in your terminal.

## HUD Format

```
🤖 Connected (12.4V) │ TeleOp Test [INIT] │ 192.168.43.1
```

### Components

| Component | Description |
|-----------|-------------|
| Connection icon | 🤖 = connected, 🔴 = disconnected |
| Battery voltage | Current battery level with color indicator |
| OpMode name | Currently selected/running OpMode |
| OpMode state | `[INIT]`, `[RUNNING]`, or `[STOPPED]` |
| IP address | Robot's IP address |

### Examples

```
🤖 Connected (12.4V) │ TeleOp Test [INIT] │ 192.168.43.1
🤖 Connected (11.8V) │ Auto Left [RUNNING] │ 192.168.43.1
🤖 Connected (11.2V) │ TeleOp Test [STOPPED] │ 192.168.43.1
🔴 Disconnected │ -- │ --
```

## Color Indicators

### Battery Colors

| Voltage | Color | Meaning |
|---------|-------|---------|
| > 12.0V | Green | Good charge |
| 11.0V - 12.0V | Yellow | Getting low |
| < 11.0V | Red | Needs charging |

### OpMode State Colors

| State | Color | Meaning |
|-------|-------|---------|
| `[INIT]` | Yellow | OpMode initialized, waiting to start |
| `[RUNNING]` | Green | OpMode is running |
| `[STOPPED]` | Gray | OpMode has stopped |

## When HUD Updates

The HUD updates automatically when:

- `/connect` or `/disconnect` runs
- `/init`, `/start`, or `/stop` changes OpMode state
- Every 5 seconds when connected (polls battery and status)

## Configuration

The HUD integrates with Claude Code's statusline system. To configure:

### Enable/Disable

The HUD is enabled by default when robot-dev is installed. To disable:

```
/robot-dev:hud off
```

To re-enable:

```
/robot-dev:hud on
```

### Custom Format

You can customize the HUD format in your Claude Code settings:

```json
{
  "robot-dev": {
    "hud": {
      "showBattery": true,
      "showOpMode": true,
      "showIP": true,
      "pollInterval": 5000
    }
  }
}
```

## Troubleshooting

### HUD shows "Disconnected" but robot is on

1. Check WiFi connection
2. Run `/connect` to re-establish connection
3. Run `/doctor` to diagnose issues

### Battery voltage not updating

The dashboard may not be reachable. Check:
1. Panels is running (port 8001)
2. Or FTC Dashboard is running (port 8080)

### OpMode state not updating

The HUD polls the dashboard for state. If not updating:
1. Verify dashboard is accessible
2. Try `/opmodes` to test dashboard connectivity

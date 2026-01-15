# FTC Claude Skills Marketplace

A marketplace for AI coding agent skills designed to help FTC (FIRST Tech Challenge) robotics teams with programming. Install only the skills your team needs.

**Compatible with:** Claude Code, OpenAI Codex CLI, VS Code Copilot, Cursor, and other [Agent Skills](https://agentskills.io) compatible tools.

## Available Skills

### FTC Skills

| Skill | Category | Description |
|-------|----------|-------------|
| **decode** | Game | DECODE 2025-2026 game reference - field layout, scoring, coordinates |
| **pedro-pathing** | Library | Pedro Pathing autonomous library - Bezier curves, path building |
| **roadrunner** | Library | RoadRunner path planning - trajectories, motion profiles, coordinate conversion |
| **pinpoint** | Hardware | GoBilda Pinpoint odometry - setup, tuning, LED status codes |
| **limelight** | Hardware | Limelight 3A vision - AprilTags, MegaTag2, color tracking |
| **nextftc** | Framework | NextFTC command-based framework - commands, subsystems, bindings |
| **panels** | Tools | Panels dashboard - telemetry graphs, live configuration |
| **ftc-dashboard** | Tools | FTC Dashboard - telemetry visualization, @Config variables, field overlay |
| **robot-dev** | Tools | Development commands - /build, /deploy, /connect, /log, OpMode control |

### Contributor Tools

| Skill | Description |
|-------|-------------|
| **contributor** | Skill-builder tools for managing FTC skills - includes `/create-skill`, `/validate-skill`, and `/version` commands |

## Installation

### Option 1: Claude Code Plugin Marketplace (Recommended)

```bash
# Register the marketplace
/plugin marketplace add ncssm-robotics/ftc-claude

# Install individual skills
/plugin install pedro-pathing@ncssm-robotics/ftc-claude
/plugin install pinpoint@ncssm-robotics/ftc-claude
/plugin install decode@ncssm-robotics/ftc-claude
```

### Option 2: Install Script (Cross-Platform)

```bash
# Clone the repository
git clone https://github.com/ncssm-robotics/ftc-claude.git
cd ftc-claude

# Install specific skills (auto-detects your coding agent)
./install.sh pedro-pathing pinpoint

# Or install all skills
./install.sh --all

# Install to a specific agent
./install.sh --agent codex pedro-pathing

# Install to current project only
./install.sh --project pedro-pathing pinpoint
```

### Option 3: Manual Copy

Copy skill folders directly to your agent's skills directory:

| Agent | Skills Directory |
|-------|------------------|
| Claude Code | `~/.claude/skills/` or `.claude/skills/` |
| Codex CLI | `~/.codex/skills/` or `.codex/skills/` |
| Cursor | `~/.cursor/skills/` |
| VS Code Copilot | Configure in settings |

```bash
# Example: Copy pedro-pathing to Claude Code
cp -r plugins/pedro-pathing/skills/pedro-pathing ~/.claude/skills/
```

## Usage

Once installed, skills activate automatically when relevant. Just ask Claude (or your coding agent) to help with FTC tasks:

```
"Help me write an autonomous routine using Pedro Pathing"
"Set up the Pinpoint odometry computer"
"Create a NextFTC command for the lift subsystem"
"What are the DECODE game scoring rules?"
```

## Repository Structure

```
ftc-claude/
├── .claude-plugin/
│   └── marketplace.json      # Plugin registry with versions
├── .github/workflows/
│   └── validate-skills.yml   # CI/CD validation including version checks
├── plugins/
│   ├── decode/
│   │   ├── plugin.json       # Plugin metadata with version
│   │   ├── CHANGELOG.md      # Version history
│   │   └── skills/decode/
│   ├── pedro-pathing/
│   ├── roadrunner/
│   ├── pinpoint/
│   ├── limelight/
│   ├── nextftc/
│   ├── panels/
│   ├── ftc-dashboard/
│   ├── robot-dev/           # Build, deploy, OpMode commands
│   │   ├── commands/
│   │   └── scripts/
│   └── contributor/         # Skill-builder tools
│       ├── skills/skill-builder/
│       └── commands/
├── template/                 # Template for new skills
├── install.sh                # Cross-platform installer
├── VERSIONING.md             # Semantic versioning guidelines
├── CONTRIBUTING.md           # Contribution guide
└── README.md
```

## Contributing

We welcome contributions from the FTC community! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### AI-Assisted Contribution (Recommended)

The easiest way to contribute is to let Claude help you build the skill:

```bash
# 1. Install the contributor tools
/plugin install contributor@ncssm-robotics/ftc-claude

# 2. Create a new skill (Claude guides you through it)
/create-skill roadrunner library

# 3. Validate before submitting
/validate-skill roadrunner
```

Or just ask Claude: *"Help me create a new FTC skill for RoadRunner"* - the skill-builder skill activates automatically and guides you through the process.

### Manual Contribution

1. Fork this repository
2. Copy `template/` to `plugins/your-skill-name/`
3. Update `plugin.json` and `SKILL.md`
4. Submit a pull request

### Skill Ideas We'd Love to See

- **ftclib** - FTCLib library patterns
- **rev-hub** - REV Control Hub configuration
- **spark-mini** - REV Spark Mini motor controller
- **photonvision** - PhotonVision integration
- **meepmeep** - MeepMeep path visualization
- **easyopencv** - EasyOpenCV pipelines

## About Agent Skills

This marketplace follows the [Agent Skills](https://agentskills.io) open standard, originally developed by Anthropic. Skills you install here work across multiple AI coding agents.

### How Skills Work

1. **Discovery** - Your coding agent reads skill metadata at startup
2. **Activation** - When you ask a relevant question, the agent loads the skill
3. **Context** - The skill provides specialized knowledge and examples
4. **Assistance** - The agent uses this knowledge to help you more effectively

## License

MIT License - see [LICENSE](LICENSE)

## Resources

- [Agent Skills Specification](https://agentskills.io/specification)
- [Anthropic Skills Repository](https://github.com/anthropics/skills)
- [FIRST Tech Challenge](https://www.firstinspires.org/robotics/ftc)
- [Pedro Pathing Documentation](https://pedropathing.com)
- [NextFTC GitHub](https://github.com/AnyiLin/NextFTC)

---

Made with ❤️ by the FTC community

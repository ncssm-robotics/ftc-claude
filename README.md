# FTC Claude Skills Marketplace

A marketplace for Claude Code skills designed to help FTC (FIRST Tech Challenge) robotics teams with programming.

## What are Claude Skills?

Claude Skills are knowledge packs that give Claude Code specialized expertise. When you add a skill to your project, Claude automatically gains deep knowledge about that topic - APIs, best practices, coordinate systems, and more.

## Available Skills

| Skill | Description |
|-------|-------------|
| **decode** | DECODE 2025-2026 FTC game reference - field layout, scoring, coordinates, autonomous strategies |
| **pinpoint** | GoBilda Pinpoint odometry computer - setup, pod offsets, tuning, LED status codes |
| **limelight** | Limelight 3A vision system - AprilTags, MegaTag2 localization, color tracking, auto-aim |
| **pedro-pathing** | Pedro Pathing library - Bezier curves, path building, heading interpolation, autonomous routines |
| **nextftc** | NextFTC command-based framework - OpModes, commands, subsystems, gamepad bindings |
| **panels** | Panels dashboard - telemetry graphs, live configuration, debugging |

## Installation

### Option 1: Copy individual skills

Copy the skill folders you need from `.claude/skills/` into your FTC project's `.claude/skills/` directory.

```bash
# Example: Copy just pedro-pathing and pinpoint
mkdir -p your-ftc-project/.claude/skills
cp -r ftc-claude/.claude/skills/pedro-pathing your-ftc-project/.claude/skills/
cp -r ftc-claude/.claude/skills/pinpoint your-ftc-project/.claude/skills/
```

### Option 2: Clone the entire marketplace

```bash
git clone https://github.com/ncssm-robotics/ftc-claude.git
```

Then copy skills as needed to your project.

## Skill Structure

Each skill follows this structure:

```
.claude/skills/<skill-name>/
├── SKILL.md              # Main skill file with frontmatter
├── *.md                  # Additional documentation
└── scripts/              # Optional utility scripts (Python)
```

### SKILL.md Format

```yaml
---
name: skill-name
description: When Claude should use this skill...
---

# Skill Title

Main content that Claude learns from...
```

## Creating Your Own Skills

1. Create a folder in `.claude/skills/` with your skill name
2. Add a `SKILL.md` file with YAML frontmatter (`name` and `description`)
3. Add supporting documentation as additional `.md` files
4. Optionally add utility scripts in a `scripts/` subdirectory

### Contributing

We welcome contributions! To add a skill to the marketplace:

1. Fork this repository
2. Create your skill in `.claude/skills/your-skill-name/`
3. Submit a pull request with:
   - Clear description of what the skill provides
   - Example use cases
   - Any dependencies or requirements

## Utility Scripts

Some skills include Python utility scripts for coordinate conversions and calculations. Run them with `uv`:

```bash
# DECODE coordinate conversions
uv run .claude/skills/decode/scripts/convert.py ftc-to-pedro 0 0 90
uv run .claude/skills/decode/scripts/convert.py mirror-blue 7 6.75 0

# Limelight calculations
uv run .claude/skills/limelight/scripts/convert.py botpose-to-pedro 0.5 1.2 45
uv run .claude/skills/limelight/scripts/convert.py distance 15 12 20 36
```

## Permissions

The included `settings.local.json` grants Claude permission to:
- Run Gradle builds (`./gradlew build`, `./gradlew assembleDebug`)
- Fetch documentation from approved sites (pedropathing.com, panels.bylazar.com, github.com)

## FTC Resources

- [FIRST Tech Challenge](https://www.firstinspires.org/robotics/ftc)
- [Pedro Pathing Documentation](https://pedropathing.com)
- [Panels Dashboard](https://panels.bylazar.com)
- [NextFTC GitHub](https://github.com/AnyiLin/NextFTC)

## License

MIT License - see [LICENSE](LICENSE)

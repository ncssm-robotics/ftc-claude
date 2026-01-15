# Claude Code Project Context

This is the FTC Claude Skills Marketplace - a collection of AI coding agent skills for FIRST Tech Challenge robotics teams.

## Repository Structure

- `plugins/` - Individual skill plugins, each with `plugin.json` and `skills/<name>/SKILL.md`
- `.claude-plugin/marketplace.json` - Registry of all available plugins
- `README.md` - Public documentation with skill table
- `.github/workflows/` - CI/CD including skill validation and code review

## Code Review Guidelines

When reviewing PRs, check for these common issues:

### New Skills
- [ ] `plugin.json` exists and has valid JSON with correct schema
- [ ] `SKILL.md` has YAML frontmatter with `name`, `description`, `license`, `metadata`
- [ ] `description` includes WHAT the skill does AND WHEN to use it (trigger words)
- [ ] Folder name matches `name` field in SKILL.md frontmatter
- [ ] Skill is added to `.claude-plugin/marketplace.json`
- [ ] Skill is added to `README.md` skill table
- [ ] SKILL.md is under 500 lines
- [ ] Has Quick Start section with code examples
- [ ] Has Anti-Patterns section

### Skill Updates
- [ ] Version bumped in `plugin.json` if functionality changed
- [ ] Description still accurate after changes

### Documentation
- [ ] README.md skill table matches marketplace.json
- [ ] Repository structure section is current
- [ ] "Skills We'd Love to See" doesn't list implemented skills

## Skill Categories

- **Game** - Season-specific game rules and strategies (e.g., decode)
- **Library** - Path planning and motion libraries (e.g., pedro-pathing, roadrunner)
- **Hardware** - Sensors and hardware configuration (e.g., pinpoint, limelight)
- **Framework** - Programming frameworks (e.g., nextftc)
- **Tools** - Development and debugging tools (e.g., panels, ftc-dashboard, robot-dev)

## Commands (robot-dev plugin)

The robot-dev plugin provides development commands:
- `/build` - Compile robot code
- `/deploy` - Build and install to robot
- `/connect` - Connect via WiFi or USB
- `/log` - View filtered logcat
- `/opmodes` - List available OpModes
- `/init`, `/start`, `/stop` - OpMode lifecycle control

## Contributing

Contributors should use `/create-skill` and `/validate-skill` commands from the contributor plugin to ensure consistency.

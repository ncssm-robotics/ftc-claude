# Claude Code Project Context

This is the FTC Claude Skills Marketplace - a collection of AI coding agent skills for FIRST Tech Challenge robotics teams.

## Repository Structure

- `plugins/` - Individual skill plugins, each with `plugin.json`, `CHANGELOG.md`, and `skills/<name>/SKILL.md`
- `.claude-plugin/marketplace.json` - Registry of all available plugins with versions
- `VERSIONING.md` - Semantic versioning guidelines for plugins
- `template/` - Templates for new plugins including `CHANGELOG.md`
- `README.md` - Public documentation with skill table
- `.github/workflows/` - CI/CD including skill validation and version checking

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
- [ ] Version bumped appropriately (see [VERSIONING.md](VERSIONING.md) for guidelines)
  - MAJOR bump: Breaking changes (removed features, changed formats, renamed commands)
  - MINOR bump: New features or significant additions (backward compatible)
  - PATCH bump: Bug fixes, typos, clarifications
- [ ] Version synchronized in all three locations:
  - `plugin.json` version field
  - `SKILL.md` frontmatter `metadata.version`
  - `.claude-plugin/marketplace.json` version field
- [ ] `CHANGELOG.md` updated with new version entry
- [ ] Description still accurate after changes

### Script Simplicity
- [ ] If SKILL.md uses `uv run scripts/*.py`, check if script only needs Python stdlib
- [ ] Scripts with only stdlib imports (sys, math, json, etc.) should use `python` not `uv run`
- [ ] Reserve `uv run` for scripts that actually need external packages (numpy, requests, pandas, etc.)
- [ ] Rationale: Simpler and more accessible - everyone has Python, not everyone has uv

### Versioning
- [ ] Version format is valid semantic version (X.Y.Z or X.Y.Z-prerelease)
- [ ] Version change appropriate for the type of changes made
- [ ] CHANGELOG.md entry exists for new version with:
  - Added, Changed, Deprecated, Removed, Fixed, Security sections as needed
  - Date in YYYY-MM-DD format
- [ ] No version skipping (e.g., 1.0.0 -> 1.5.0 is invalid)

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

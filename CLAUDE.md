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
- [ ] Changes added to `## [Unreleased]` section in `CHANGELOG.md`
- [ ] Correct changelog category used:
  - `### Added` - New features (→ MINOR bump)
  - `### Changed` - Behavior changes/breaking (→ MAJOR bump)
  - `### Fixed` - Bug fixes (→ PATCH bump)
  - `### Removed` - Deleted features/breaking (→ MAJOR bump)
  - `### Deprecated` - Future removal warning (→ MINOR bump)
  - `### Security` - Security fixes (→ PATCH bump)
- [ ] Change descriptions are clear and user-facing (they appear in release notes)
- [ ] **NOT** manually bumping version numbers (automated during release)
- [ ] Description still accurate after changes
- [ ] PR targets `develop` branch (not `main`)

### Script Simplicity
- [ ] If SKILL.md uses `uv run scripts/*.py`, check if script only needs Python stdlib
- [ ] Scripts with only stdlib imports (sys, math, json, etc.) should use `python` not `uv run`
- [ ] Reserve `uv run` for scripts that actually need external packages (numpy, requests, pandas, etc.)
- [ ] Rationale: Simpler and more accessible - everyone has Python, not everyone has uv

### Versioning & Changelog
- [ ] PR does **NOT** include manual version bumps (automated during release)
- [ ] Changes documented in `## [Unreleased]` section (not versioned sections)
- [ ] Changelog categories match the actual changes:
  - Breaking changes use `### Changed` or `### Removed`
  - New features use `### Added`
  - Bug fixes use `### Fixed`
- [ ] No empty or generic changelog entries ("various improvements" is not helpful)
- [ ] CHANGELOG.md format is valid (proper markdown headers)

### Documentation Sync
- [ ] README.md skill table matches marketplace.json
- [ ] README.md contributor commands match actual commands in `plugins/contributor/commands/`
- [ ] README.md "AI-Assisted Contribution" section lists all contributor commands
- [ ] Repository structure section is current
- [ ] "Skills We'd Love to See" doesn't list implemented skills

### Contributor Plugin Changes
When the contributor plugin is modified:
- [ ] New commands are documented in README.md "AI-Assisted Contribution" section
- [ ] New commands are documented in skill-builder SKILL.md "Available Commands" table
- [ ] Command descriptions in marketplace.json match actual functionality
- [ ] CONTRIBUTING.md references new commands where appropriate

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

Contributors should use commands from the contributor plugin to ensure consistency:
- `/contributor:create-skill` - Create new plugin from template
- `/contributor:validate-skill` - Validate plugin structure before PR

**Version Management:** Version bumps are automated during the release process. Contributors only add changes to `## [Unreleased]` sections in `CHANGELOG.md`. See [RELEASES.md](RELEASES.md) for the release process (maintainers only).

See [VERSIONING.md](VERSIONING.md) for changelog category guidelines and [CONTRIBUTING.md](CONTRIBUTING.md) for full contribution guide.

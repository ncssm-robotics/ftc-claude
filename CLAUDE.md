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

Run local code review with the same checks as the PR bot:

```bash
/contributor:review <skill-name>
```

| Review Type | Skill | Purpose |
|-------------|-------|---------|
| `code` | `contributor:code-review` | Structure, content quality, marketplace |
| `security` | `contributor:security-review` | Credentials, file safety, injection |
| `youth` | `contributor:youth-safety-review` | Content appropriateness for students |

The review skills auto-activate when relevant. For full check definitions, see `plugins/contributor/skills/*/SKILL.md`.

### Quick Reference

**New Skills:**
- Start at version 1.0.0 (correct, not a violation)
- Must have plugin.json, CHANGELOG.md, SKILL.md
- Add to marketplace.json and README.md skill table

**Skill Updates:**
- Add changes to `## [Unreleased]` in CHANGELOG.md
- Use correct categories: Added/Changed/Fixed/Removed/Deprecated/Security
- Do NOT manually bump versions (release process handles this)
- Target `develop` branch (not `main`)

**Script Simplicity:**
- Use `python` for stdlib-only scripts
- Use `uv run` only when external packages needed

### Documentation Sync
- [ ] README.md skill table matches marketplace.json
- [ ] README.md contributor commands match actual commands
- [ ] Repository structure section is current

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

Contributors should use commands from the contributor plugin:

| Command | Purpose |
|---------|---------|
| `/contributor:create-skill <name>` | Create new plugin from template |
| `/contributor:validate-skill <name>` | Validate plugin structure before PR |
| `/contributor:update-skill <name>` | Generate changelog entries from git diff |
| `/contributor:review <name>` | Run local code review checks |

## Versioning

**Never manually bump versions.** The `contributor:versioning` skill will remind you of the correct process:

1. Add changes to `## [Unreleased]` in CHANGELOG.md
2. Use `/contributor:update-skill <name>` to generate entries from git diff
3. Submit PR to `develop` branch
4. Versions are bumped automatically by the release process

See [RELEASES.md](RELEASES.md) for release process (maintainers only) and [CONTRIBUTING.md](CONTRIBUTING.md) for full contribution guide.

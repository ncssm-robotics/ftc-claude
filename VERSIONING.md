# Plugin Versioning Guide

This document defines the versioning system for FTC Claude Skills Marketplace plugins. All plugins follow [Semantic Versioning 2.0.0](https://semver.org/) with adaptations specific to AI agent skills.

## Version Format

```
MAJOR.MINOR.PATCH
```

- **MAJOR**: Breaking changes to skill behavior or instructions
- **MINOR**: New features or significant content additions (backward compatible)
- **PATCH**: Bug fixes, typos, clarifications (backward compatible)

## When to Bump Versions

### MAJOR Version (X.0.0)

Increment MAJOR when changes could break existing workflows or require user adaptation:

- Removing or renaming skill commands (e.g., `/decode` → `/game-ref`)
- Changing required parameters or their formats
- Removing documented features or API references
- Restructuring SKILL.md in ways that change skill behavior
- Changing coordinate systems, units, or data formats
- Removing support for previously documented hardware/software

**Examples:**
- Removing the specimen scoring section from decode skill
- Changing Pedro Pathing coordinate system from inches to meters
- Removing backward compatibility for RoadRunner 0.5

### MINOR Version (x.Y.0)

Increment MINOR when adding new capabilities without breaking existing usage:

- Adding new sections or documentation
- Adding new code examples or templates
- Supporting additional hardware or software versions
- Adding new API references or troubleshooting guides
- Expanding existing features with new options

**Examples:**
- Adding teleop strategies to decode skill
- Adding support for new Pinpoint firmware version
- Adding RoadRunner 1.1 migration guide

### PATCH Version (x.y.Z)

Increment PATCH for fixes that don't change functionality:

- Fixing typos, grammar, or formatting
- Correcting inaccurate information
- Clarifying ambiguous instructions
- Updating broken links
- Minor code example fixes

**Examples:**
- Fixing coordinate typo (120 → 12 inches)
- Correcting method signature in example
- Updating deprecated import statement

## Version Tracking Locations

Each plugin has **two version fields** that must stay synchronized:

1. **`plugin.json`** - Primary source of truth
   ```json
   {
     "name": "decode",
     "version": "1.2.0",
     ...
   }
   ```

2. **`SKILL.md` frontmatter** - Skill metadata
   ```yaml
   ---
   name: decode
   metadata:
     version: "1.2.0"
   ---
   ```

The CI workflow validates that these versions match.

## Version Bump Process

**Important:** Version bumps are **fully automated** during the release process. Contributors do not manually bump version numbers.

### Contributor Workflow

When making changes to a plugin, add your changes to the `## [Unreleased]` section of `CHANGELOG.md`:

```markdown
## [Unreleased]

### Added
- New teleop strategies section with defensive positioning

### Fixed
- Corrected ascent zone coordinates
```

### Changelog Categories

Use these categories to document your changes. The release automation will use these to determine the version bump type:

| Category | Version Impact | Use When |
|----------|----------------|----------|
| `### Added` | MINOR | New features, sections, examples |
| `### Changed` | MAJOR | Behavior changes (breaking) |
| `### Fixed` | PATCH | Bug fixes, corrections |
| `### Removed` | MAJOR | Deleted features (breaking) |
| `### Deprecated` | MINOR | Marking features for future removal |
| `### Security` | PATCH | Security-related fixes |

### How Version Calculation Works

During the release process, an automated script:

1. **Analyzes** each plugin's `## [Unreleased]` section
2. **Determines** version bump type based on categories present:
   - If `### Removed` OR `### Changed` present → **MAJOR** bump
   - Else if `### Added` OR `### Deprecated` present → **MINOR** bump
   - Else if `### Fixed` OR `### Security` present → **PATCH** bump
3. **Applies highest severity** if multiple categories exist
4. **Updates** version in all three locations automatically
5. **Moves** `## [Unreleased]` content → `## [X.Y.Z] - YYYY-MM-DD`
6. **Creates** fresh `## [Unreleased]` section for next cycle

### Example: Multiple Categories

```markdown
## [Unreleased]

### Added
- New section on autonomous paths

### Removed
- Deprecated specimen scoring (use new API)
```

**Result:** MAJOR bump (because `### Removed` is present, even though `### Added` is also there)

### For Maintainers

See [RELEASES.md](RELEASES.md) for the complete release process documentation.

## Pre-release Versions

For work-in-progress or beta features, use pre-release identifiers:

```
1.2.0-alpha.1    # Early development
1.2.0-beta.1     # Feature complete, testing
1.2.0-rc.1       # Release candidate
```

## Version 0.x.x

Versions starting with 0 (e.g., `0.1.0`) indicate initial development where the API is unstable. During 0.x development:
- MINOR bumps may include breaking changes
- Use this for new skills still being refined

Bump to 1.0.0 when the skill is stable and ready for production use.

## Changelog Format

Each plugin should have a `CHANGELOG.md` following [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
# Changelog

All notable changes to this plugin will be documented in this file.

## [Unreleased]

## [1.1.0] - 2025-01-15

### Added
- New feature description

### Changed
- Modified behavior description

### Deprecated
- Feature that will be removed

### Removed
- Feature that was removed

### Fixed
- Bug fix description

### Security
- Security-related fix
```

## CI Validation

The validation workflow enforces:

1. **Version format**: Must match `X.Y.Z` or `X.Y.Z-prerelease`
2. **Version sync**: `plugin.json` and `SKILL.md` versions must match
3. **Version bump on changes**: If skill content changed, version must increase
4. **Changelog entry**: New versions must have corresponding changelog entries

## Version in Marketplace

The marketplace registry (`marketplace.json`) tracks the current version of each plugin:

```json
{
  "name": "decode",
  "version": "1.2.0",
  "description": "...",
  "source": "./plugins/decode",
  "skills": ["./skills/decode"]
}
```

This enables version-aware plugin installation and updates.

## Best Practices

1. **Atomic version bumps**: One version bump per PR, covering all related changes
2. **Descriptive changelogs**: Help users understand what changed and why
3. **Don't skip versions**: Go from 1.0.0 → 1.1.0, never 1.0.0 → 1.5.0
4. **Document breaking changes**: Include migration guides for MAJOR bumps
5. **Test before release**: Verify skill works as documented before bumping

## FAQ

**Q: Do I need to bump version for README changes?**
A: No, only bump versions for changes to `SKILL.md`, scripts, or `plugin.json`.

**Q: What if I make multiple changes in one PR?**
A: Use the highest applicable version bump (MAJOR > MINOR > PATCH).

**Q: Should marketplace.json version match individual plugin versions?**
A: No, `metadata.version` in marketplace.json is the registry version, separate from plugin versions.

**Q: Can I use date-based versions?**
A: No, stick to semantic versioning for consistency with the skills ecosystem.

## References

- [Semantic Versioning 2.0.0](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Anthropic Agent Skills](https://github.com/anthropics/skills)

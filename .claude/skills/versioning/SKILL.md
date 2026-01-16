---
name: versioning
description: >-
  FTC marketplace versioning guardrail. Activates when considering version bumps,
  changing version numbers, or modifying plugin.json versions. Redirects to the
  correct automated release process. Use this to understand the versioning workflow.
license: MIT
compatibility: Claude Code, Codex CLI, VS Code Copilot, Cursor
metadata:
  author: ncssm-robotics
  category: tools
allowed-tools: Read
---

# FTC Versioning Guardrail

## STOP: Do Not Manually Change Version Numbers!

This repository uses an **automated release process**. Contributors should NEVER manually change version numbers in any file.

## Files You Should NOT Edit (Version Fields)

| File | Field | Why Not |
|------|-------|---------|
| `plugins/<name>/plugin.json` | `version` | Release script updates this |
| `plugins/<name>/skills/<name>/SKILL.md` | `metadata.version` | Release script updates this |
| `.claude-plugin/marketplace.json` | plugin `version` | Release script updates this |

## The Correct Workflow

### For Contributors

1. **Make your changes** to the skill (SKILL.md, scripts, etc.)

2. **Add changelog entries** to `## [Unreleased]` section in CHANGELOG.md:
   ```markdown
   ## [Unreleased]

   ### Added
   - New calibration script for pod offset calculation

   ### Fixed
   - Corrected coordinate transformation formula
   ```

3. **Use the update-skill command** to help generate entries:
   ```
   /update-skill <skill-name>
   ```

4. **Submit PR** to the `develop` branch

5. **Done!** - Versions are bumped automatically during the release process

### For Maintainers (Release Process)

1. Go to GitHub Actions
2. Run "Prepare Release" workflow
3. Script automatically:
   - Parses changelog categories (Added → MINOR, Fixed → PATCH, etc.)
   - Calculates new version numbers
   - Updates all three version locations atomically
   - Creates release PR

## Why This Matters

### Deterministic Versioning

Version bumps are calculated from changelog categories:

| Changelog Category | Version Bump |
|-------------------|--------------|
| `### Removed` | MAJOR (X.0.0) |
| `### Changed` | MAJOR (X.0.0) |
| `### Added` | MINOR (0.Y.0) |
| `### Deprecated` | MINOR (0.Y.0) |
| `### Fixed` | PATCH (0.0.Z) |
| `### Security` | PATCH (0.0.Z) |

### Consistency Guarantee

The release script ensures:
- All three version locations match
- Changelog is properly formatted
- Release notes are generated
- Git tags are created

### Avoiding Merge Conflicts

Manual version bumps cause:
- Merge conflicts when multiple PRs touch versions
- Inconsistency between files
- Confusion about which version is correct

## Exception: New Skills (1.0.0)

When creating a new skill with `/create-skill`, the version IS set to 1.0.0. This is the only time a version is "manually" set, and it's done by the create-skill command.

New skills should:
- Start at version 1.0.0
- Have this in plugin.json, SKILL.md, and marketplace.json
- Have initial 1.0.0 entry in CHANGELOG.md

## If You're Tempted to Bump a Version

Ask yourself:
1. Did I add entries to the `## [Unreleased]` section? (Do this instead!)
2. Am I running the release process? (Only maintainers do this)
3. Is this a new skill? (Let create-skill handle it)

If none of these apply, you probably shouldn't be changing version numbers.

## Commands Reference

| Command | Purpose |
|---------|---------|
| `/create-skill` | Creates new skill at 1.0.0 |
| `/update-skill` | Generates changelog entries (NO version bump) |
| `/validate-skill` | Validates structure (NO version bump) |
| `/review` | Runs code review (NO version bump) |

None of these commands change version numbers after initial creation.

## See Also

- `RELEASES.md` - Full release process documentation
- `.github/scripts/prepare-release.sh` - The release automation script
- `.github/workflows/prepare-release.yml` - The release workflow

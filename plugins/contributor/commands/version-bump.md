---
description: Bump plugin version with guided changelog entry
argument-hint: <plugin-name>
allowed-tools: Read, Write, Edit, Glob, Grep, AskUserQuestion
---

# Version Bump Command

Interactively bumps a plugin's version across all required locations and creates a changelog entry.

## Usage

```
/contributor:version <plugin-name>
```

**Arguments:**
- `plugin-name`: Name of the plugin to version bump (e.g., `decode`, `pinpoint`)

## Examples

```
/contributor:version decode
/contributor:version pedro-pathing
/contributor:version pinpoint
```

## Process

When this command is invoked:

### 1. Validate the Plugin Exists

Check that the plugin exists at `plugins/<plugin-name>/`:
- `plugin.json` exists and is valid JSON
- `CHANGELOG.md` exists (create if missing)
- At least one skill directory exists under `skills/`

### 2. Read Current Version

Extract the current version from `plugins/<plugin-name>/plugin.json`:
```json
{
  "version": "1.0.0"
}
```

Display current version to user.

### 3. Ask About Change Type (Use AskUserQuestion)

Use the AskUserQuestion tool to ask the contributor:

**Question 1: What type of change is this?**

Options:
- **PATCH (x.y.Z)** - Bug fixes, typos, clarifications, broken links
- **MINOR (x.Y.0)** - New features, documentation additions, new firmware/version support
- **MAJOR (X.0.0)** - Breaking changes, removed features, changed formats/coordinates

### 4. Ask About Changes Made (Use AskUserQuestion)

**Question 2: What categories of changes were made?** (multi-select)

Options:
- **Added** - New features or documentation
- **Changed** - Modifications to existing functionality
- **Fixed** - Bug fixes or corrections
- **Removed** - Removed features or deprecated content

### 5. Collect Change Descriptions

For each selected category, ask for a brief description of the changes.

Alternatively, prompt the user to describe the changes in a single response and parse them into categories.

### 6. Calculate New Version

Based on the change type selected:
- PATCH: `1.0.0` → `1.0.1`
- MINOR: `1.0.0` → `1.1.0`
- MAJOR: `1.0.0` → `2.0.0`

Confirm the new version with the user.

### 7. Update All Version Locations

Update version in these three files:

**a. `plugins/<plugin-name>/plugin.json`:**
```json
{
  "version": "1.1.0"
}
```

**b. `plugins/<plugin-name>/skills/<skill-name>/SKILL.md` frontmatter:**
```yaml
metadata:
  version: "1.1.0"
```

**c. `.claude-plugin/marketplace.json`:**
```json
{
  "name": "<plugin-name>",
  "version": "1.1.0",
  ...
}
```

### 8. Update CHANGELOG.md

Prepend a new version entry to `plugins/<plugin-name>/CHANGELOG.md`:

```markdown
## [1.1.0] - YYYY-MM-DD

### Added
- [User's description of added features]

### Changed
- [User's description of changes]

### Fixed
- [User's description of fixes]
```

Use today's date in YYYY-MM-DD format.

### 9. Summary

Display a summary to the user:

```
Version bump complete for <plugin-name>!

  Old version: 1.0.0
  New version: 1.1.0

Updated files:
  - plugins/<plugin-name>/plugin.json
  - plugins/<plugin-name>/skills/<skill-name>/SKILL.md
  - .claude-plugin/marketplace.json
  - plugins/<plugin-name>/CHANGELOG.md

Suggested commit message:
  feat(<plugin-name>): [brief description]

Run validation:
  /contributor:validate-skill <plugin-name>
```

## Error Handling

- **Plugin not found:** List available plugins and ask user to try again
- **Invalid version format:** Show error and current version, ask to fix manually
- **Missing CHANGELOG.md:** Create it with initial entry before proceeding
- **Version mismatch detected:** Show all current versions and ask which to use as base

## Version Format Rules

- Must be valid semantic version: `X.Y.Z` or `X.Y.Z-prerelease`
- No version skipping (e.g., `1.0.0` → `1.5.0` is invalid)
- Pre-release tags: `alpha.N`, `beta.N`, `rc.N`

## Quick Reference

| Change Type | Examples | Version Bump |
|-------------|----------|--------------|
| PATCH | Fix typo, correct coordinates, update link | 1.0.0 → 1.0.1 |
| MINOR | Add new section, support new firmware | 1.0.0 → 1.1.0 |
| MAJOR | Remove feature, change coordinate system | 1.0.0 → 2.0.0 |

## Related

- [VERSIONING.md](../../../VERSIONING.md) - Full versioning guidelines
- `/contributor:validate-skill` - Validate plugin structure
- `/contributor:create-skill` - Create new plugin

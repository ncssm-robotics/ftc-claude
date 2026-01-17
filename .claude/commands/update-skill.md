---
description: Generate changelog entries from git diff for a skill
argument-hint: <skill-name>
allowed-tools: Read, Write, Edit, Bash(git:*), Glob, Grep
---

# Update Skill Command

Analyzes git changes and generates properly formatted changelog entries for a skill.

**Important:** This command only creates changelog entries. Version bumping is handled automatically by the release process when the PR is merged.

## Usage

```
/update-skill <skill-name>
```

**Arguments:**
- `skill-name`: Name of the skill to update (must exist in `plugins/`)

## Examples

```
/update-skill pinpoint
/update-skill pedro-pathing
/update-skill decode
```

## Process

When this command is invoked:

1. **Validate the skill exists**
   - Check `plugins/<skill-name>/` directory exists
   - Check `CHANGELOG.md` exists in the plugin directory
   - Check `## [Unreleased]` section exists in CHANGELOG.md

2. **Analyze git changes**
   - Run `git status plugins/<skill-name>/` to see modified files
   - Run `git diff plugins/<skill-name>/` to see specific changes
   - Identify new files, modified files, and deleted files

3. **Categorize changes** into changelog categories:
   - **Added** - New files, new features, new sections
   - **Changed** - Modified behavior, updated documentation
   - **Fixed** - Bug fixes, corrections
   - **Removed** - Deleted features, removed sections
   - **Deprecated** - Features marked for removal
   - **Security** - Security-related fixes

4. **Generate proposed entries**
   - Create concise, descriptive entries for each change
   - Use imperative mood ("Add X" not "Added X")
   - Group related changes together

5. **Present to user for confirmation**
   - Show proposed entries
   - Allow user to edit, add, or remove entries
   - Confirm before writing

6. **Update CHANGELOG.md**
   - Append entries to `## [Unreleased]` section
   - Preserve existing unreleased entries
   - Maintain proper formatting

## Output Example

```
Analyzing changes for skill: pinpoint

Git status shows:
  modified: skills/pinpoint/SKILL.md (47 lines changed)
  new file: skills/pinpoint/scripts/calibrate.py

Proposed changelog entries:

### Added
- Calibration script for automated pod offset calculation

### Changed
- Updated Quick Start section with calibration workflow
- Added troubleshooting section for IMU drift issues

Confirm these entries? [Y/n/edit]
```

## Categorization Guidelines

| Change Type | Changelog Category |
|-------------|-------------------|
| New file | `### Added` |
| New feature/section | `### Added` |
| Modified existing feature | `### Changed` |
| Bug fix | `### Fixed` |
| Typo correction | `### Fixed` |
| Removed file/feature | `### Removed` |
| Marked as deprecated | `### Deprecated` |
| Security fix | `### Security` |

## Entry Writing Guidelines

**Good entries:**
- "Add calibration script for automated pod offset calculation"
- "Update Quick Start with step-by-step hardware setup"
- "Fix coordinate transformation for rotated odometry pods"

**Bad entries:**
- "Updated SKILL.md" (too vague)
- "Fixed bug" (what bug?)
- "Added stuff" (what stuff?)

## What This Command Does NOT Do

- Does NOT bump version numbers
- Does NOT modify `plugin.json`
- Does NOT modify `marketplace.json`
- Does NOT modify SKILL.md frontmatter version

Version bumping is handled automatically by the release process based on changelog categories.

## After Updating

The workflow continues:

1. Review the changelog entries added
2. Run `/validate-skill <skill-name>` to check everything
3. Run `/review <skill-name>` for full code review
4. Commit changes and submit PR to develop branch
5. Release process will handle version bumps

## Checklist

Before completing, verify:
- [ ] Git changes analyzed for the skill
- [ ] Proposed entries are descriptive and accurate
- [ ] User confirmed the entries
- [ ] Entries added to `## [Unreleased]` section
- [ ] NO version numbers were changed

# Release Process

This document describes the automated release process for the FTC Claude Skills Marketplace. The process is designed to be deterministic, requiring minimal manual intervention from maintainers.

## Table of Contents

- [Overview](#overview)
- [Branch Workflow](#branch-workflow)
- [Contributor Workflow](#contributor-workflow)
- [Maintainer Release Process](#maintainer-release-process)
- [Version Calculation Logic](#version-calculation-logic)
- [Troubleshooting](#troubleshooting)
- [Emergency Procedures](#emergency-procedures)

---

## Overview

The release process follows these principles:

1. **Contributors don't manage versions** - They only add categorized changes to `## [Unreleased]` sections in CHANGELOG.md files
2. **Automated version calculation** - Scripts determine version bumps based on changelog categories
3. **Single-button release** - Maintainers trigger releases via GitHub Actions workflow
4. **Develop branch workflow** - All development happens on `develop`, releases merge to `main`
5. **Deterministic and auditable** - Every version bump is calculated using documented rules

### Key Components

- **`develop` branch**: Integration branch for all development work
- **`main` branch**: Production branch, contains only released code
- **Release scripts**: Bash scripts that analyze changelogs and calculate versions
- **GitHub Actions**: Workflows that automate the entire release process

---

## Branch Workflow

```
main (production, releases only)
  ↑
  │ [Release PR with version bumps]
  │
develop (active development)
  ↑
  │ [Feature PRs]
  │
feature/bug branches
```

### Branch Descriptions

**`develop`** - Default branch for development
- All PRs merge here
- No version bumps required in PRs
- Contributors add changes to `## [Unreleased]` sections
- Stays ahead of `main` with unreleased work

**`main`** - Production branch
- Contains only released, versioned code
- All files have bumped versions (no Unreleased sections)
- GitHub releases are created from commits on main
- Automatically syncs back to `develop` after releases

---

## Contributor Workflow

Contributors working on plugins follow this simple process:

### 1. Create Feature Branch

```bash
git checkout develop
git pull origin develop
git checkout -b feature/my-feature
```

### 2. Make Changes

Edit plugin files as needed (SKILL.md, scripts, etc.)

### 3. Update CHANGELOG.md

Add your changes to the `## [Unreleased]` section using the appropriate category:

```markdown
## [Unreleased]

### Added
- New feature X that helps with Y
- Support for Z hardware configuration

### Fixed
- Corrected calculation bug in coordinate transformation
```

### 4. Submit PR to develop

```bash
git add -A
git commit -m "feat(decode): add teleop strategy examples"
git push origin feature/my-feature
```

Create PR targeting `develop` branch. **No version bump required!**

### Changelog Categories

Choose the category that matches your change:

| Category | When to Use | Version Impact |
|----------|-------------|----------------|
| `### Added` | New features, sections, examples | MINOR bump |
| `### Changed` | Modified behavior (breaking) | MAJOR bump |
| `### Fixed` | Bug fixes, corrections | PATCH bump |
| `### Removed` | Deleted features (breaking) | MAJOR bump |
| `### Deprecated` | Features marked for future removal | MINOR bump |
| `### Security` | Security-related fixes | PATCH bump |

**Rule of thumb:**
- Breaking changes (users must change their code) → `### Changed` or `### Removed`
- New capabilities (users can do more) → `### Added`
- Fixes (things work correctly now) → `### Fixed`

---

## Maintainer Release Process

Maintainers use a simple workflow to create releases:

### Step 1: Decide to Release

Triggers for creating a release:
- Regular schedule (weekly, bi-weekly, monthly)
- Accumulation of significant changes
- Urgent bug fixes merged
- User requests for new features in `develop`

### Step 2: Run Prepare Release Workflow

1. Go to **Actions** → **Prepare Release** in GitHub
2. Click **"Run workflow"**
3. Options:
   - **dry_run**: Check this to preview changes without creating PR
   - **target_branch**: Leave as `main` (default)
4. Click **"Run workflow"** button

### Step 3: Review the Release PR

The script automatically:
- Analyzes all plugin changelogs
- Determines version bumps (MAJOR/MINOR/PATCH)
- Calculates marketplace version
- Moves `## [Unreleased]` → `## [X.Y.Z] - YYYY-MM-DD`
- Creates release branch `release/vX.Y.Z`
- Opens PR to `main` with release notes

**What to review:**
- ✓ Version bumps are correct for each plugin
- ✓ Changelog categories match actual changes
- ✓ Release notes are clear and accurate
- ✓ Breaking changes are called out prominently
- ✓ No sensitive information in changelogs

### Step 4: Merge the PR

Once satisfied, click **"Merge pull request"**.

### Step 5: Automatic Post-Merge Actions

GitHub Actions automatically:
1. **Creates GitHub Release** (publish-release.yml)
   - Tag: `vX.Y.Z`
   - Title: "FTC Claude Skills Marketplace vX.Y.Z"
   - Notes: Aggregated changelogs from all changed plugins
2. **Creates per-plugin tags** (optional)
   - Format: `decode-v1.2.3`, `pinpoint-v2.0.1`
3. **Syncs develop** (sync-develop.yml)
   - Merges `main` → `develop`
   - Ensures branches stay in sync

**Total time: ~5 minutes** (mostly review)

---

## Version Calculation Logic

The release script uses deterministic rules to calculate version bumps.

### Plugin Version Calculation

For each plugin, the script:

1. **Extracts** the `## [Unreleased]` section from `CHANGELOG.md`
2. **Detects** changelog categories present:
   - `### Removed` or `### Changed` → **MAJOR** bump
   - `### Added` or `### Deprecated` → **MINOR** bump
   - `### Fixed` or `### Security` → **PATCH** bump
3. **Applies highest severity** if multiple categories exist:
   - Priority: MAJOR > MINOR > PATCH

**Examples:**

```markdown
## [Unreleased]
### Added
- New feature
```
→ MINOR bump (1.2.3 → 1.3.0)

```markdown
## [Unreleased]
### Fixed
- Bug fix
```
→ PATCH bump (1.2.3 → 1.2.4)

```markdown
## [Unreleased]
### Added
- New feature
### Removed
- Old deprecated feature
```
→ MAJOR bump (1.2.3 → 2.0.0) — Removed takes priority

### Marketplace Version Calculation

The marketplace version aggregates all plugin bumps:

1. Collect bump types for all changed plugins
2. Apply highest severity across all plugins
3. Bump marketplace version accordingly

**Examples:**

- Plugin A: MINOR, Plugin B: PATCH → Marketplace gets MINOR bump
- Plugin A: MAJOR, Plugin B: MINOR → Marketplace gets MAJOR bump
- Plugin A: PATCH, Plugin B: PATCH → Marketplace gets PATCH bump

### Version Update Locations

The script updates versions in **three synchronized locations** for each plugin:

1. `plugins/<name>/plugin.json`
2. `plugins/<name>/skills/<name>/SKILL.md` (frontmatter `metadata.version`)
3. `.claude-plugin/marketplace.json` (plugin entry)

Plus the marketplace version in:
4. `.claude-plugin/marketplace.json` (metadata.version)

All updates are atomic and verified for consistency.

---

## Troubleshooting

### Release PR Creation Failed

**Symptom:** Workflow runs but no PR is created

**Causes:**
1. No plugins have unreleased changes
2. Unreleased sections exist but have no recognized categories
3. CHANGELOG.md format is invalid

**Solution:**
```bash
# Check for unreleased changes
git checkout develop
grep -r "## \[Unreleased\]" plugins/*/CHANGELOG.md

# Run script locally in dry-run mode
DRY_RUN=true .github/scripts/prepare-release.sh
```

### Version Inconsistency Errors

**Symptom:** Script fails with "Version mismatch" error

**Cause:** Version fields in plugin.json, SKILL.md, or marketplace.json don't match

**Solution:**
```bash
# Manually sync versions for plugin "decode"
cd plugins/decode

# Check current versions
jq -r '.version' plugin.json
grep "version:" skills/decode/SKILL.md

# Fix SKILL.md version
sed -i 's/version: ".*"/version: "1.2.3"/' skills/decode/SKILL.md
```

### Merge Conflicts During develop Sync

**Symptom:** Issue created: "Failed to sync develop with main"

**Cause:** Changes were committed directly to main (bypassing develop)

**Solution:**
```bash
git checkout develop
git pull origin develop
git merge origin/main
# Resolve conflicts manually
git commit
git push origin develop
```

**Prevention:** Never commit directly to main outside the release process

### Malformed CHANGELOG.md

**Symptom:** Script fails to parse changelog

**Common issues:**
- Missing `## [Unreleased]` header
- Inconsistent heading levels (using `####` instead of `###`)
- Non-standard category names

**Solution:**
Ensure CHANGELOG.md follows Keep a Changelog format:
```markdown
# Changelog

All notable changes to this plugin will be documented in this file.

## [Unreleased]

### Added
- Feature descriptions

### Fixed
- Bug fix descriptions

## [1.0.0] - 2025-01-15

### Added
- Initial release
```

---

## Emergency Procedures

### Rollback a Published Release

**Scenario:** Released version has critical bugs

**Steps:**

1. **Revert the merge commit on main**
   ```bash
   git checkout main
   git pull origin main
   git revert -m 1 <merge-commit-sha>
   git push origin main
   ```

2. **Delete the GitHub release**
   ```bash
   gh release delete v1.5.0 --yes
   ```

3. **Delete the tag**
   ```bash
   git push --delete origin v1.5.0
   git tag --delete v1.5.0
   ```

4. **Fix issues on develop**
   ```bash
   git checkout develop
   # Make fixes
   git commit -m "fix: critical bug in release v1.5.0"
   ```

5. **Create new release**
   - Run "Prepare Release" workflow again
   - This will create v1.5.1 (or v1.6.0 depending on fixes)

### Hotfix Direct to main

**Scenario:** Critical production bug, can't wait for develop cycle

**Steps:**

1. **Create hotfix branch from main**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b hotfix/critical-bug
   ```

2. **Make the fix and update CHANGELOG**
   ```bash
   # Fix the bug
   vim plugins/decode/skills/decode/SKILL.md

   # Add to CHANGELOG (manually create a patch version entry)
   vim plugins/decode/CHANGELOG.md
   # Add: ## [1.2.4] - 2025-01-15
   #      ### Fixed
   #      - Critical bug description
   ```

3. **Manually bump version** (all three locations)
   ```bash
   # Update plugin.json
   jq '.version = "1.2.4"' plugins/decode/plugin.json > tmp && mv tmp plugins/decode/plugin.json

   # Update SKILL.md
   sed -i 's/version: "1.2.3"/version: "1.2.4"/' plugins/decode/skills/decode/SKILL.md

   # Update marketplace.json
   jq '(.plugins[] | select(.name == "decode") | .version) = "1.2.4"' \
     .claude-plugin/marketplace.json > tmp && mv tmp .claude-plugin/marketplace.json

   # Bump marketplace version (patch)
   jq '.metadata.version = "1.0.1"' .claude-plugin/marketplace.json > tmp && mv tmp .claude-plugin/marketplace.json
   ```

4. **Commit and create PR to main**
   ```bash
   git add -A
   git commit -m "hotfix: critical bug in decode plugin"
   git push origin hotfix/critical-bug

   gh pr create --base main --head hotfix/critical-bug \
     --title "Hotfix: Critical Bug in Decode Plugin" \
     --label "hotfix"
   ```

5. **After merge, sync to develop**
   - The sync-develop.yml workflow will run automatically
   - If conflicts occur, resolve manually as described in Troubleshooting

### Script Failure Mid-Release

**Scenario:** prepare-release.sh fails partway through

**Recovery:**

1. **Check what was modified**
   ```bash
   git checkout develop
   git status
   git diff
   ```

2. **If changes are incomplete, reset**
   ```bash
   git reset --hard origin/develop
   ```

3. **Investigate failure**
   ```bash
   # Run in dry-run mode to see what would happen
   DRY_RUN=true .github/scripts/prepare-release.sh
   ```

4. **Fix issue and retry**
   - Fix the underlying issue (malformed changelog, etc.)
   - Commit fix to develop
   - Re-run workflow

---

## Best Practices

### For Contributors

1. **Update CHANGELOG.md in every PR** that changes functionality
2. **Use appropriate categories** - don't guess, read the table above
3. **Write clear, concise descriptions** - users will read these
4. **One category per change** - if a change spans multiple categories, choose the highest severity
5. **Test your changes** before submitting PR

### For Maintainers

1. **Release regularly** - weekly or bi-weekly keeps changes small
2. **Review release PRs carefully** - you're the last line of defense
3. **Communicate releases** - let users know when new versions are available
4. **Monitor feedback** - watch for issues after releases
5. **Document major releases** - write migration guides for breaking changes

### For Everyone

1. **Never commit directly to main** - always go through develop
2. **Keep changelogs clean** - no sensitive info, no jokes
3. **Test on develop first** - don't assume it works
4. **Ask if unsure** - reach out to maintainers if you're not sure about changelog categories

---

## Version History

### Marketplace Releases

See the [Releases page](https://github.com/ncssm-robotics/ftc-claude/releases) for the full version history.

### Plugin-Specific Releases

Individual plugin versions are tracked in their respective CHANGELOG.md files:

- `plugins/decode/CHANGELOG.md`
- `plugins/pedro-pathing/CHANGELOG.md`
- `plugins/pinpoint/CHANGELOG.md`
- ... (see `plugins/*/CHANGELOG.md` for all plugins)

---

## Additional Resources

- [VERSIONING.md](VERSIONING.md) - Semantic versioning rules and guidelines
- [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute to the marketplace
- [CLAUDE.md](CLAUDE.md) - Code review guidelines for AI reviewers
- [Keep a Changelog](https://keepachangelog.com/) - Changelog format standard
- [Semantic Versioning 2.0.0](https://semver.org/) - Version numbering spec

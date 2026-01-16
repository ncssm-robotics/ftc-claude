---
name: code-review
description: >-
  FTC skill code quality and structure checks. Activates when reviewing PRs,
  validating skills, or checking plugin compliance with marketplace standards.
  Use when reviewing pull requests, running local code review, or validating
  skill structure before submission.
license: MIT
compatibility: Claude Code, Codex CLI, VS Code Copilot, Cursor
metadata:
  author: ncssm-robotics
  version: "1.0.0"
  category: tools
allowed-tools: Read, Glob, Grep
---

# FTC Code Review Checks

This skill defines the code quality and structure checks for FTC marketplace skills. These checks are the source of truth for both local reviews (`/contributor:review`) and PR bot reviews.

## Structure Checks (Errors)

These checks must pass - errors block PR merge.

### Plugin Directory Structure
- [ ] `plugins/<skill-name>/` directory exists
- [ ] `plugins/<skill-name>/plugin.json` exists
- [ ] `plugins/<skill-name>/CHANGELOG.md` exists
- [ ] `plugins/<skill-name>/skills/<skill-name>/` directory exists
- [ ] `plugins/<skill-name>/skills/<skill-name>/SKILL.md` exists

### plugin.json Validation
- [ ] File is valid JSON (no syntax errors)
- [ ] Has `name` field matching directory name
- [ ] Has `version` field in semver format (X.Y.Z)
- [ ] Has `description` field (non-empty string)
- [ ] Has `author` field as object (NOT a string)
- [ ] Author object has `name` property
- [ ] Has `keywords` array (NOT `tags`)
- [ ] Keywords array includes "ftc"

### SKILL.md Frontmatter Validation
- [ ] File starts with `---` (YAML frontmatter)
- [ ] Has `name` field matching directory name
- [ ] Has `description` field (non-empty, < 1024 chars)
- [ ] Has `license` field
- [ ] Has `metadata` object
- [ ] Has `metadata.version` field matching plugin.json version
- [ ] Has `metadata.category` field

### Version Consistency
- [ ] Version in `plugin.json` matches version in SKILL.md frontmatter
- [ ] Version in `marketplace.json` entry matches plugin.json (if listed)

## Content Quality Checks (Warnings)

These are recommendations - warnings don't block merge but should be addressed.

### Description Quality
- [ ] Description explains WHAT the skill does
- [ ] Description explains WHEN to use it (trigger words)
- [ ] Description contains FTC-specific keywords
- [ ] Description is under 1024 characters

### SKILL.md Content
- [ ] File is under 500 lines (use progressive disclosure)
- [ ] Has "Quick Start" or "Getting Started" section
- [ ] Has code examples (```java or ```kotlin blocks)
- [ ] Has "Anti-Pattern" or "Don't" section with bad examples
- [ ] No `[TODO: ...]` placeholder markers remaining

### Code Examples
- [ ] Examples include both good and bad patterns
- [ ] Bad examples are marked with comments (// Bad, // Don't, etc.)
- [ ] Examples are syntactically correct

## Marketplace Checks (Errors)

### Registration
- [ ] Skill is listed in `.claude-plugin/marketplace.json`
- [ ] Entry uses `source` field (NOT `path`)
- [ ] Entry has `skills` array listing skill directories
- [ ] Version in marketplace entry matches plugin.json

## CHANGELOG Checks (Warnings)

### Format
- [ ] `CHANGELOG.md` follows Keep a Changelog format
- [ ] Has `## [Unreleased]` section at the top
- [ ] Categories use correct headers: Added, Changed, Fixed, Removed, Deprecated, Security

## New Skill vs Update Checks

### For New Skills (version 1.0.0)
- [ ] Version is 1.0.0 in all three locations
- [ ] This is CORRECT - new skills SHOULD start at 1.0.0
- [ ] CHANGELOG.md has initial 1.0.0 entry

### For Skill Updates
- [ ] New entries added to `## [Unreleased]` section
- [ ] Version NOT manually bumped (release process handles this)

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| `author` as string | Use object: `{"name": "...", "url": "..."}` |
| Using `tags` field | Rename to `keywords` |
| Using `path` in marketplace | Rename to `source` |
| Missing "ftc" keyword | Add "ftc" to keywords array |
| SKILL.md too long | Extract to API_REFERENCE.md, TROUBLESHOOTING.md |
| No anti-patterns | Always show what NOT to do |
| Version mismatch | Ensure all 3 locations match |

## Running This Review

```bash
/contributor:review <skill-name> --type code
```

Or as part of full review:
```bash
/contributor:review <skill-name>
```

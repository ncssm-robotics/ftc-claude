---
description: Validate an FTC skill plugin structure and content
argument-hint: <skill-name>
allowed-tools: Read, Glob, Grep, Bash(jq:*)
---

# Validate Skill Command

Validates that an FTC skill plugin follows marketplace requirements and best practices.

## Usage

```
/validate-skill <skill-name>
```

**Arguments:**
- `skill-name`: Name of the skill to validate (must exist in `plugins/`)

## Examples

```
/validate-skill pedro-pathing
/validate-skill rev-hub
```

## Validation Checks

### Structure Checks

- [ ] `plugins/<skill-name>/` directory exists
- [ ] `plugins/<skill-name>/plugin.json` exists and is valid JSON
- [ ] `plugins/<skill-name>/skills/<skill-name>/` directory exists
- [ ] `plugins/<skill-name>/skills/<skill-name>/SKILL.md` exists

### plugin.json Checks

- [ ] Has `name` field matching directory name
- [ ] Has `description` field (non-empty)
- [ ] Has `version` field (semver format)
- [ ] Has `license` field
- [ ] Has `tags` array with "ftc"
- [ ] Has `compatibility.agents` array

### SKILL.md Frontmatter Checks

- [ ] Has YAML frontmatter (starts with `---`)
- [ ] Has `name` field matching directory name
- [ ] Has `description` field (non-empty, < 1024 chars)
- [ ] `description` includes WHAT the skill does
- [ ] `description` includes WHEN to use it (trigger words)
- [ ] Has `license` field
- [ ] Has `metadata.category` field
- [ ] Has `metadata.version` field

### Content Quality Checks

- [ ] SKILL.md is under 500 lines
- [ ] Has "Quick Start" or "## Quick" section
- [ ] Has code examples (```java or ```kotlin blocks)
- [ ] Has "Anti-Pattern" or "Don't" section
- [ ] No `[TODO: ...]` placeholders remaining
- [ ] No hardcoded file paths from template

### marketplace.json Check

- [ ] Skill is listed in `.claude-plugin/marketplace.json`
- [ ] Entry has correct `path` field

### Script Checks (if scripts/ exists)

- [ ] All `.sh` files are executable
- [ ] All `.py` files are executable
- [ ] Scripts have shebang line

## Output Format

Report results as:

```
Validating skill: <skill-name>

Structure:
  ✓ plugin.json exists
  ✓ SKILL.md exists
  ✗ Missing scripts/ directory (optional)

plugin.json:
  ✓ Valid JSON
  ✓ Name matches directory
  ✗ Missing 'ftc' in tags

SKILL.md:
  ✓ Valid frontmatter
  ✓ Description includes WHAT
  ✗ Description missing WHEN triggers
  ✓ Under 500 lines (127 lines)

Content:
  ✓ Has Quick Start section
  ✓ Has code examples
  ✗ Missing Anti-Patterns section
  ✗ Contains [TODO: ...] placeholders

marketplace.json:
  ✓ Skill is registered

Summary: 8/12 checks passed
```

## Severity Levels

- **Error** (✗): Must fix before submitting PR
- **Warning** (⚠): Should fix, but not blocking
- **Info** (ℹ): Suggestion for improvement

### Errors (Must Fix)

- Missing required files (plugin.json, SKILL.md)
- Invalid JSON
- Name mismatch between folder and frontmatter
- Empty description
- Not in marketplace.json

### Warnings (Should Fix)

- Description missing WHEN triggers
- No Anti-Patterns section
- SKILL.md over 500 lines
- Missing 'ftc' tag
- [TODO: ...] placeholders remaining

### Info (Suggestions)

- No scripts/ directory
- Could add more code examples
- Consider adding TROUBLESHOOTING.md

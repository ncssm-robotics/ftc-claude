---
description: Run local code review checks (same as PR bot)
argument-hint: <skill-name> [--type code|security|youth]
allowed-tools: Read, Glob, Grep, Bash(jq:*)
---

# Review Command

Runs the same code review checks locally that the PR bot runs, giving you feedback before submitting a PR.

## Usage

```
/review <skill-name> [--type code|security|youth]
```

**Arguments:**
- `skill-name`: Name of the skill to review (must exist in `plugins/`)
- `--type`: Optional filter to run only specific review type(s)

## Type Options

| Flag | Reviews Run |
|------|-------------|
| (none) | All reviews (code + security + youth) |
| `--type code` | Code quality and structure only |
| `--type security` | Security checks only |
| `--type youth` | Content appropriateness only |

## Examples

```
/review pinpoint                  # Run all reviews
/review pedro-pathing --type code # Code review only
/review decode --type security    # Security review only
```

## Process

When this command is invoked:

1. **Validate the skill exists**
   - Check `plugins/<skill-name>/` directory exists

2. **Load review skills**
   - Load `code-review` skill (unless filtered out)
   - Load `security-review` skill (unless filtered out)
   - Load `youth-safety-review` skill (unless filtered out)

3. **Execute checks**
   - Run each check defined in the loaded review skills
   - Categorize results as pass (✓), warning (⚠), or error (✗)

4. **Output structured report**
   - Show results grouped by review type
   - Include pass/warn/fail counts per type
   - Show overall summary

## Output Format

```
Reviewing skill: pinpoint

=== Code Review ===
Structure:
  ✓ plugin.json exists and valid
  ✓ SKILL.md exists with frontmatter
  ✓ Name matches across files
  ✓ CHANGELOG.md exists with [Unreleased] section
Content Quality:
  ✓ Description includes WHAT and WHEN
  ✓ Under 500 lines (127 lines)
  ✓ Has Quick Start section
  ⚠ Missing Anti-Patterns section
  ✓ Has code examples
Marketplace:
  ✓ Listed in marketplace.json
  ✓ Version matches plugin.json
Code Review: 9/10 passed (1 warning)

=== Security Review ===
Credentials:
  ✓ No hardcoded API keys
  ✓ No hardcoded passwords
  ✓ No WiFi credentials
Configuration:
  ✓ Allowed FTC IPs only (192.168.43.1)
  ✓ No absolute paths
  ✓ No path traversal patterns
Code Injection:
  ✓ No eval/exec of user input
  ✓ No unsanitized shell commands
Security Review: 8/8 passed

=== Youth Safety Review ===
Language:
  ✓ No profanity detected
  ✓ Variable names appropriate
  ⚠ "killer_shot" may be flagged - verify context
Personal Info:
  ✓ No student names
  ✓ No school names
Content:
  ✓ Examples use neutral naming
Youth Safety Review: 4/5 passed (1 warning)

=== Summary ===
Code Review:     9/10  (1 warning)
Security Review: 8/8   (passed)
Youth Safety:    4/5   (1 warning)

Overall: PASSED with 2 warnings
```

## Result Interpretation

| Symbol | Meaning | Action |
|--------|---------|--------|
| ✓ | Check passed | No action needed |
| ⚠ | Warning | Review and fix if appropriate |
| ✗ | Error | Must fix before PR |

## Review Skills Referenced

This command loads and executes checks from:

- `code-review` - Structure, content quality, marketplace checks
- `security-review` - Credentials, file safety, injection checks
- `youth-safety-review` - Language, personal info, content checks

See those skill definitions for the complete check lists.

## After Reviewing

Based on results:

1. **All passed:** Ready to submit PR
2. **Warnings only:** Review each warning, fix if needed
3. **Errors:** Must fix all errors before submitting PR

Then:
```
/update-skill <skill-name>  # Generate changelog entries
git add . && git commit -m "..."         # Commit changes
git push                                  # Push to remote
```

## Checklist

The review verifies:
- [ ] plugin.json is valid and complete
- [ ] SKILL.md has proper frontmatter and content
- [ ] CHANGELOG.md has [Unreleased] section
- [ ] Skill is registered in marketplace.json
- [ ] No security vulnerabilities
- [ ] Content is appropriate for FTC students

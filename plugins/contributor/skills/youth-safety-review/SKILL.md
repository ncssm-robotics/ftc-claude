---
name: youth-safety-review
description: >-
  Content appropriateness review for FTC student code. Activates when checking
  variable names, comments, and strings for inappropriate content before sharing.
  Use when reviewing code that students will see, checking for inappropriate
  language, or ensuring content is suitable for ages 12-18.
license: MIT
compatibility: Claude Code, Codex CLI, VS Code Copilot, Cursor
metadata:
  author: ncssm-robotics
  version: "1.0.0"
  category: tools
allowed-tools: Read, Glob, Grep
---

# FTC Youth Safety Review Checks

This skill defines content appropriateness checks for FTC marketplace skills. FTC participants are students ages 12-18, so all content should be appropriate for that audience.

**Important:** These checks flag items for human review. They do not auto-reject content because context matters. A mentor or maintainer should review flagged items.

## Acceptable FTC Terms

These terms are ALLOWED despite potentially triggering filters:

| Term | Context |
|------|---------|
| `kill`, `killer` | Game mechanic (kill shot, killing it) |
| `attack`, `defense` | Game strategy terms |
| `destroy` | Game context (destroy opponent's stack) |
| `target` | Vision targeting, game elements |
| `shoot`, `shooter` | Game mechanisms |
| `score`, `scoring` | Points and objectives |
| `dead` | Battery dead, dead reckoning |

## Language Checks (Warnings)

Flag for human review if detected in:
- Variable names
- Function/method names
- Class names
- Comments
- String literals
- File names

### Profanity Detection
- [ ] No profanity in variable names
- [ ] No profanity in comments
- [ ] No profanity in string literals
- [ ] No l33tspeak variations of profanity

### Inappropriate Naming
- [ ] Variable names don't contain inappropriate content
- [ ] Function names are professional
- [ ] Class names are appropriate

### Insensitive Language
- [ ] No racial or ethnic slurs
- [ ] No gender-based insults
- [ ] No disability-related slurs
- [ ] No religious insults

## Comment Review (Warnings)

### Tone and Content
- [ ] Comments don't contain personal attacks
- [ ] Comments don't contain exclusionary language
- [ ] Comments don't reference inappropriate content
- [ ] TODO comments don't contain frustration venting

### Humor
- [ ] Jokes are appropriate for all ages
- [ ] Sarcasm doesn't cross into inappropriate territory
- [ ] Pop culture references are age-appropriate

## Personal Information (Errors)

These must be fixed - privacy is important.

### Student Information
- [ ] No real student names in examples
- [ ] No student photos or identifying information
- [ ] No birth dates or ages

### School Information
- [ ] No school names in examples (use "Team 12345" format)
- [ ] No school addresses
- [ ] No teacher/mentor names

### Contact Information
- [ ] No email addresses in code or examples
- [ ] No phone numbers
- [ ] No social media handles (Twitter/X, Instagram, etc.)

## Content Appropriateness (Warnings)

### Topics to Avoid
- [ ] No references to alcohol or drugs
- [ ] No gambling references
- [ ] No dating/relationship content inappropriate for youth
- [ ] No violent content beyond game mechanics
- [ ] No political or religious advocacy

### Example Content
- [ ] Examples use neutral/robot-related naming
- [ ] Sample data doesn't contain inappropriate content
- [ ] Test cases use appropriate test values

## Severity Levels

| Level | Meaning | Action |
|-------|---------|--------|
| Error | Must fix | Personal information, clear violations |
| Warning | Flag for review | Context-dependent, needs human judgment |
| Info | Suggestion | Style improvements |

## Review Process

When flagging items:

1. **Quote the specific content** - Show exactly what was flagged
2. **Explain why** - What rule does it potentially violate
3. **Suggest alternative** - Offer appropriate replacement
4. **Request human review** - A mentor should make final call

## Example Flags

### Flagged (Context Review Needed)
```java
// Variable name flagged
double killer_shot_power = 0.8;  // "killer" flagged - is this game context?
```
**Recommendation:** Rename to `scoring_shot_power` for clarity.

### Acceptable (No Flag)
```java
// Game mechanic - acceptable
void scoreInHighBasket() { ... }

// Dead reckoning - acceptable
void driveByDeadReckoning() { ... }
```

### Must Fix (Error)
```java
// Personal information - must remove
// Created by John Smith, Central High School
String studentEmail = "john@school.edu";
```
**Required:** Remove personal information.

## Running This Review

```bash
/contributor:review <skill-name> --type youth
```

Or as part of full review:
```bash
/contributor:review <skill-name>
```

## See Also

- [FIRST Youth Protection Program](https://www.firstinspires.org/programs/youth-protection-program)
- [FIRST Code of Conduct](https://www.firstinspires.org/about/vision-and-mission)

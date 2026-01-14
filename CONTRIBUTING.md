# Contributing to FTC Claude Skills

Thank you for your interest in contributing to the FTC Claude Skills Marketplace! This guide will help you create and submit skills that help FTC teams worldwide.

## Table of Contents

- [Getting Started](#getting-started)
- [Creating a New Skill](#creating-a-new-skill)
- [Skill Structure](#skill-structure)
- [Writing Good Skills](#writing-good-skills)
- [Testing Your Skill](#testing-your-skill)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Code of Conduct](#code-of-conduct)

## Getting Started

### Prerequisites

- Git installed on your computer
- A GitHub account
- Familiarity with the FTC library/hardware/tool you're documenting
- A coding agent to test with (Claude Code, Codex CLI, etc.)

### Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR-USERNAME/ftc-claude.git
cd ftc-claude
```

## Creating a New Skill

### Step 1: Copy the Template

```bash
cp -r template plugins/your-skill-name
```

### Step 2: Rename the Skill Folder

```bash
mv plugins/your-skill-name/skills/my-skill plugins/your-skill-name/skills/your-skill-name
```

### Step 3: Update plugin.json

Edit `plugins/your-skill-name/plugin.json`:

```json
{
  "name": "your-skill-name",
  "description": "Brief description (shown in marketplace listings)",
  "version": "1.0.0",
  "author": "Your Name or Team Number",
  "license": "MIT",
  "repository": "https://github.com/ncssm-robotics/ftc-claude",
  "tags": ["ftc", "relevant", "keywords"],
  "compatibility": {
    "agents": ["claude-code", "codex", "cursor", "vscode-copilot"]
  }
}
```

### Step 4: Write SKILL.md

This is the most important file. Edit `plugins/your-skill-name/skills/your-skill-name/SKILL.md`:

```yaml
---
name: your-skill-name
description: Detailed description of what this skill does and when the AI should use it. Include keywords that will trigger this skill.
license: MIT
compatibility: Claude Code, Codex CLI, VS Code Copilot, Cursor
metadata:
  author: your-github-username
  version: "1.0.0"
  category: hardware | library | framework | tools | game
---

# Your Skill Name

Your content here...
```

### Step 5: Add to Marketplace Registry

Edit `.claude-plugin/marketplace.json` and add your plugin to the `plugins` array:

```json
{
  "name": "your-skill-name",
  "description": "Your skill description",
  "version": "1.0.0",
  "path": "plugins/your-skill-name",
  "category": "hardware",
  "tags": ["ftc", "your", "tags"]
}
```

## Skill Structure

```
plugins/your-skill-name/
├── plugin.json                    # Required: Plugin metadata
└── skills/
    └── your-skill-name/
        ├── SKILL.md               # Required: Main skill instructions
        ├── API_REFERENCE.md       # Optional: Detailed API docs
        ├── TROUBLESHOOTING.md     # Optional: Common issues
        └── scripts/               # Optional: Utility scripts
            └── helper.py
```

## Writing Good Skills

### The Description Field is Critical

The `description` in your SKILL.md frontmatter determines when your skill gets activated. Make it specific:

**Good:**
```yaml
description: Helps configure REV Spark Mini motor controllers for FTC robots. Use when setting up Spark Mini, configuring motor parameters, or troubleshooting REV motor controllers.
```

**Bad:**
```yaml
description: Motor controller help.
```

### Include Practical Examples

Show copy-paste ready code that actually works:

```java
// GOOD: Complete, working example
@TeleOp(name = "Spark Mini Test")
public class SparkMiniTest extends LinearOpMode {
    private DcMotorEx motor;

    @Override
    public void runOpMode() {
        motor = hardwareMap.get(DcMotorEx.class, "motor");
        motor.setMode(DcMotor.RunMode.RUN_USING_ENCODER);

        waitForStart();

        while (opModeIsActive()) {
            motor.setPower(-gamepad1.left_stick_y);
        }
    }
}
```

### Use Tables for Quick Reference

```markdown
| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| kP | 10.0 | 0-100 | Proportional gain |
| kI | 0.0 | 0-10 | Integral gain |
```

### Keep SKILL.md Under 500 Lines

Move detailed content to reference files:

- `API_REFERENCE.md` - Complete method documentation
- `TROUBLESHOOTING.md` - Common problems and solutions
- `EXAMPLES.md` - Extended code examples

### Progressive Disclosure

Put the most common use case first. Users should be able to get started by reading just the first section.

## Testing Your Skill

### Install Locally

```bash
# Test with Claude Code
./install.sh --project your-skill-name

# Or copy manually
cp -r plugins/your-skill-name/skills/your-skill-name ~/.claude/skills/
```

### Test Activation

Start a new conversation and ask questions that should trigger your skill:

```
"Help me set up [your hardware/library]"
"How do I configure [specific feature]?"
"Show me an example of [common task]"
```

### Validate Structure

The CI will run these checks, but you can run them locally:

```bash
# Check plugin.json is valid JSON
jq empty plugins/your-skill-name/plugin.json

# Check SKILL.md has frontmatter
head -1 plugins/your-skill-name/skills/your-skill-name/SKILL.md
# Should output: ---
```

## Submitting a Pull Request

### 1. Create a Branch

```bash
git checkout -b add-your-skill-name
```

### 2. Commit Your Changes

```bash
git add plugins/your-skill-name .claude-plugin/marketplace.json
git commit -m "Add your-skill-name skill for [brief description]"
```

### 3. Push to Your Fork

```bash
git push origin add-your-skill-name
```

### 4. Open a Pull Request

Go to GitHub and create a pull request. Include:

- **Title:** `Add [skill-name] skill`
- **Description:**
  - What the skill does
  - What FTC hardware/library/tool it covers
  - Any dependencies or requirements
  - How you tested it

### 5. CI Validation

Your PR will automatically run validation checks. Fix any errors before requesting review.

## Checklist Before Submitting

- [ ] `name` in SKILL.md matches the folder name
- [ ] `name` is lowercase with hyphens only
- [ ] `description` clearly explains when to use this skill
- [ ] Code examples are tested and working
- [ ] No sensitive information (API keys, team credentials)
- [ ] Added to `marketplace.json`
- [ ] License specified (MIT recommended)
- [ ] Spell-checked content

## Skill Categories

Use these categories in your `plugin.json` and SKILL.md metadata:

| Category | Description | Examples |
|----------|-------------|----------|
| `hardware` | Physical components | Pinpoint, Limelight, REV Hub |
| `library` | Software libraries | Pedro Pathing, RoadRunner |
| `framework` | Code frameworks | NextFTC, FTCLib |
| `tools` | Development tools | Panels, MeepMeep |
| `game` | Season-specific | DECODE, INTO THE DEEP |

## Code of Conduct

- Be respectful and welcoming to all contributors
- Focus on constructive feedback
- Help newcomers learn
- Credit original sources and authors
- Follow [FIRST values](https://www.firstinspires.org/about/vision-and-mission)

## Questions?

- Open an issue on GitHub
- Tag maintainers in your PR for help
- Check existing skills for examples

---

Thank you for contributing to the FTC community! 🤖

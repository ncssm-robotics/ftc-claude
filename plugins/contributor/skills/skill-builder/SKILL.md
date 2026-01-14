---
name: skill-builder
description: Create, structure, and optimize FTC skills for the marketplace. Use when creating a new skill, improving an existing skill, scaffolding a plugin, or needing guidance on skill design patterns, triggers, frontmatter, progressive disclosure, or skill testing.
license: MIT
compatibility: Claude Code, Codex CLI, VS Code Copilot, Cursor
metadata:
  author: ncssm-robotics
  version: "1.0.0"
  category: tools
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(mkdir:*), Bash(chmod:*)
---

# FTC Skill Builder

This skill teaches you how to create high-quality skills for the FTC Claude Skills Marketplace. Skills are knowledge packs that help AI coding agents assist FTC teams with specific hardware, libraries, frameworks, or tools.

## Quick Reference

| Element | Purpose | Required |
|---------|---------|----------|
| `name` | Unique identifier (kebab-case) | Yes |
| `description` | WHAT it does + WHEN to use it | Yes |
| `license` | Usually MIT for FTC community | Recommended |
| `compatibility` | Which agents support it | Recommended |
| `metadata` | Author, version, category | Recommended |
| `SKILL.md` | Main instructions (<500 lines) | Yes |
| Reference files | Detailed docs (API_REFERENCE.md) | Optional |
| `scripts/` | Utility scripts | Optional |

## When to Create a Skill vs Other Options

| Need | Solution |
|------|----------|
| Domain expertise (hardware, library) | **Skill** - auto-activates when relevant |
| Explicit user action | **Command** - `/create-skill name` |
| Project-wide instructions | **CLAUDE.md** - always loaded |
| One-off task | Just ask Claude directly |

## FTC Skill Categories

| Category | Description | Examples |
|----------|-------------|----------|
| `hardware` | Physical components | Pinpoint, Limelight, REV Hub, Spark Mini |
| `library` | Software libraries | Pedro Pathing, RoadRunner, FTCLib |
| `framework` | Code frameworks | NextFTC, command-based patterns |
| `tools` | Development tools | Panels, MeepMeep, EasyOpenCV |
| `game` | Season-specific | DECODE 2025-2026, INTO THE DEEP |

## Skill Anatomy

```
plugins/your-skill-name/
├── plugin.json                    # Plugin metadata
└── skills/
    └── your-skill-name/
        ├── SKILL.md               # Main instructions (required)
        ├── API_REFERENCE.md       # Detailed API docs (optional)
        ├── TROUBLESHOOTING.md     # Common issues (optional)
        ├── EXAMPLES.md            # Extended examples (optional)
        └── scripts/               # Utility scripts (optional)
            └── convert.py
```

## Writing the Description (CRITICAL)

The `description` field determines when your skill activates. It must answer:
1. **WHAT** does this skill do?
2. **WHEN** should Claude use it?

### Good Description (Clear WHAT + WHEN)

```yaml
description: >-
  Helps configure and use the GoBilda Pinpoint odometry computer for robot
  localization. Use when setting up Pinpoint, configuring pod offsets,
  troubleshooting LED status, tuning encoders, or integrating with Pedro Pathing.
```

**Why it works:**
- WHAT: Configure GoBilda Pinpoint odometry
- WHEN: Setup, pod offsets, LED status, tuning, Pedro integration

### Bad Description (Too Vague)

```yaml
description: Helps with odometry.
```

**Why it fails:**
- No specific hardware mentioned
- No trigger scenarios
- Won't activate on relevant questions

### FTC-Specific Trigger Words

Include these in descriptions where relevant:
- Hardware: "GoBilda", "REV", "Limelight", "Spark Mini", "encoder"
- Libraries: "Pedro Pathing", "RoadRunner", "FTCLib", "NextFTC"
- Concepts: "autonomous", "teleop", "path following", "PID", "odometry"
- Actions: "setup", "configure", "tune", "troubleshoot", "integrate"

## Frontmatter Reference

```yaml
---
name: your-skill-name              # Required: kebab-case, max 64 chars
description: >-                    # Required: max 1024 chars
  What this skill does.
  Use when [trigger 1], [trigger 2], or [trigger 3].
license: MIT                       # Recommended for FTC community
compatibility: Claude Code, Codex CLI, VS Code Copilot, Cursor
metadata:
  author: your-github-username     # Your GitHub username or team number
  version: "1.0.0"                 # Semantic versioning
  category: hardware               # hardware | library | framework | tools | game
allowed-tools: Read, Write, Edit   # Optional: restrict tool access
---
```

### Tool Restriction Patterns

```yaml
# Read-only skill (safe, no modifications)
allowed-tools: Read, Grep, Glob

# Can create/edit files
allowed-tools: Read, Write, Edit, Glob, Grep

# Can run specific commands
allowed-tools: Read, Write, Edit, Bash(./gradlew:*), Bash(uv:*)

# Full access (omit field entirely)
# allowed-tools: (not specified)
```

## Progressive Disclosure

Keep SKILL.md focused (~500 lines max). Link to detailed files that load on-demand.

```markdown
# My Hardware Skill

## Quick Start
[Essential setup - what 80% of users need]

## Common Patterns
[Frequently used code patterns]

## Detailed Reference
For complete API documentation, see [API_REFERENCE.md](API_REFERENCE.md).
For troubleshooting guides, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Utilities
Convert coordinates:
\`\`\`bash
uv run scripts/convert.py ftc-to-pedro 0 0 90
\`\`\`
```

**Rule:** Link directly from SKILL.md. Avoid A→B→C reference chains.

## Content Structure Patterns

### DO Patterns Section

```markdown
## Patterns

- Always call `pinpoint.update()` in your loop
- Set encoder resolution before calling `resetPosAndIMU()`
- Use mm internally, convert to inches for Pedro Pathing
- Check LED status before debugging code issues
```

### DON'T / Anti-Patterns Section

```markdown
## Anti-Patterns

- ❌ Calling `resetPosAndIMU()` while robot is moving
- ❌ Using I2C port 0 (reserved for internal IMU)
- ❌ Forgetting to call `update()` - position won't refresh
- ❌ Mixing mm and inches without conversion
```

### Examples Section

```markdown
## Examples

### Good: Proper initialization sequence

\`\`\`java
@Override
public void init() {
    pinpoint = hardwareMap.get(GoBildaPinpointDriver.class, "pinpoint");
    pinpoint.setEncoderResolution(goBILDA_4_BAR_POD);
    pinpoint.setOffsets(forwardOffset_mm, strafeOffset_mm);
    pinpoint.resetPosAndIMU();  // Robot must be stationary!
}
\`\`\`

### Bad: Wrong initialization order

\`\`\`java
// ❌ resetPosAndIMU before setEncoderResolution
@Override
public void init() {
    pinpoint = hardwareMap.get(GoBildaPinpointDriver.class, "pinpoint");
    pinpoint.resetPosAndIMU();  // Wrong! Resolution not set yet
    pinpoint.setEncoderResolution(goBILDA_4_BAR_POD);
}
\`\`\`
```

## Scripts in Skills

Scripts execute without loading content into context (zero token cost):

```markdown
## Utilities

Convert FTC coordinates to Pedro Pathing:
\`\`\`bash
uv run scripts/convert.py ftc-to-pedro 1.5 2.0 90
\`\`\`

Mirror red alliance pose for blue:
\`\`\`bash
uv run scripts/convert.py mirror-blue 7 6.75 0
\`\`\`
```

Make scripts executable:
```bash
chmod +x scripts/*.sh scripts/*.py
```

## Complete SKILL.md Template

```markdown
---
name: your-skill-name
description: >-
  [What this skill does - specific capabilities for FTC].
  Use when [trigger 1], [trigger 2], or [trigger 3].
license: MIT
compatibility: Claude Code, Codex CLI, VS Code Copilot, Cursor
metadata:
  author: your-github-username
  version: "1.0.0"
  category: hardware | library | framework | tools | game
---

# [Skill Name]

Brief introduction - what this helps FTC teams accomplish.

## Quick Start

### Installation/Setup
[How to add the dependency or configure hardware]

### Basic Usage
\`\`\`java
// Minimal working example
\`\`\`

## Key Concepts

| Term | Description |
|------|-------------|
| **Term 1** | What it means in FTC context |
| **Term 2** | What it means in FTC context |

## Common Patterns

### Pattern 1: [Descriptive Name]
\`\`\`java
// Code example
\`\`\`

### Pattern 2: [Descriptive Name]
\`\`\`java
// Code example
\`\`\`

## Anti-Patterns

- ❌ [Thing to avoid] - [Why it's bad]
- ❌ [Thing to avoid] - [Why it's bad]

## Examples

### Good: [Descriptive title]
\`\`\`java
// Working example with comments
\`\`\`

### Bad: [Descriptive title]
\`\`\`java
// ❌ What not to do
\`\`\`

## Reference Documentation

- [API_REFERENCE.md](API_REFERENCE.md) - Complete API documentation
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues and solutions

## External Resources

- [Official Documentation](https://example.com/docs)
- [GitHub Repository](https://github.com/example/repo)
```

## Skill Creation Checklist

Before submitting your skill:

- [ ] `name` matches folder name (kebab-case)
- [ ] `description` includes WHAT and WHEN triggers
- [ ] `description` includes FTC-specific keywords
- [ ] SKILL.md is under ~500 lines
- [ ] Includes Quick Start section
- [ ] Shows Good AND Bad examples
- [ ] Anti-patterns marked with ❌
- [ ] Code examples are tested and working
- [ ] Scripts are executable (`chmod +x`)
- [ ] No sensitive information (API keys, credentials)
- [ ] Added to marketplace.json
- [ ] plugin.json has correct metadata

## Testing Your Skill

1. Install locally:
   ```bash
   ./install.sh --project your-skill-name
   ```

2. Start a new conversation and test triggers:
   ```
   "Help me set up [your hardware/library]"
   "How do I configure [specific feature]?"
   "Show me an example of [common task]"
   ```

3. Claude should ask: "Should I use the [skill-name] skill?"

4. Verify the skill provides accurate, helpful information.

## Common Mistakes & Fixes

| Mistake | Fix |
|---------|-----|
| Vague description | Add specific FTC keywords and trigger scenarios |
| SKILL.md too long | Extract to API_REFERENCE.md, TROUBLESHOOTING.md |
| No anti-patterns | Always show what NOT to do |
| Scripts not executable | `chmod +x scripts/*` |
| Missing Quick Start | Put most common use case first |
| Only Java examples | Include Kotlin if the library supports it |

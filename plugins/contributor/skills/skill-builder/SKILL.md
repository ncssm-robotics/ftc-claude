---
name: skill-builder
description: Create, structure, and optimize FTC skills for the marketplace. Use when creating a new skill, improving an existing skill, scaffolding a plugin, or needing guidance on skill design patterns, triggers, frontmatter, progressive disclosure, or skill testing.
license: MIT
compatibility: Claude Code, Codex CLI, VS Code Copilot, Cursor
metadata:
  author: ncssm-robotics
  version: "1.2.0"
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

## Available Commands

| Command | Purpose |
|---------|---------|
| `/contributor:create-skill <name> [category]` | Create new plugin from template |
| `/contributor:validate-skill <name>` | Validate plugin structure before PR |
| ~~`/contributor:version <name>`~~ | ⚠️ **Deprecated** - versions now automated |

### Version Bump Command

> **⚠️ DEPRECATED:** This command is deprecated and will be removed in v2.0.0.
>
> **New Process:** Version bumps are now automated during the release process. Contributors should add changes to the `## [Unreleased]` section of `CHANGELOG.md` instead.
>
> See [RELEASES.md](../../../RELEASES.md) for the new automated release workflow.

Use `/contributor:version` to update plugin versions across all required locations:

```
/contributor:version decode
```

This command will:
1. Ask what type of change (MAJOR/MINOR/PATCH)
2. Ask what categories of changes (Added/Changed/Fixed/Removed)
3. Update version in `plugin.json`, `SKILL.md`, and `marketplace.json`
4. Create changelog entry with today's date

See [VERSIONING.md](../../../VERSIONING.md) for complete versioning guidelines.

## Skill Anatomy

```
plugins/your-skill-name/
├── plugin.json                    # Plugin metadata
├── CHANGELOG.md                   # Version history
└── skills/
    └── your-skill-name/
        ├── SKILL.md               # Main instructions (required)
        ├── API_REFERENCE.md       # Detailed API docs (optional)
        ├── TROUBLESHOOTING.md     # Common issues (optional)
        ├── EXAMPLES.md            # Extended examples (optional)
        └── scripts/               # Utility scripts (optional)
            └── convert.py
```

## plugin.json Format (IMPORTANT)

Every plugin needs a `plugin.json` file with the correct schema:

```json
{
  "name": "your-skill-name",
  "version": "1.0.0",
  "description": "Brief description for marketplace listing",
  "author": {
    "name": "Your Name or Team",
    "url": "https://github.com/your-username"
  },
  "repository": "https://github.com/ncssm-robotics/ftc-claude",
  "license": "MIT",
  "keywords": ["ftc", "category", "relevant", "keywords"]
}
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Must match folder name (kebab-case) |
| `version` | string | Semantic version (e.g., "1.0.0") |
| `description` | string | Brief description for listings |
| `author` | object | **Must be an object**, not a string |

### Author Object Format

```json
"author": {
  "name": "NCSSM Robotics",
  "url": "https://github.com/ncssm-robotics"
}
```

**Common Mistake:** Using `"author": "Name"` (string) instead of an object will cause installation to fail.

### Optional but Recommended Fields

| Field | Type | Description |
|-------|------|-------------|
| `repository` | string | GitHub repo URL |
| `license` | string | License type (MIT recommended) |
| `keywords` | array | Search keywords (include "ftc") |
| `homepage` | string | Documentation URL |

### Invalid Fields (Do NOT Use)

These fields are NOT supported and will cause errors:
- ❌ `tags` - use `keywords` instead
- ❌ `compatibility` - not a valid field
- ❌ `author` as string - must be object

## marketplace.json Entry

When adding your plugin to the marketplace, add an entry to `.claude-plugin/marketplace.json`:

```json
{
  "name": "your-skill-name",
  "description": "Brief description",
  "source": "./plugins/your-skill-name",
  "skills": ["./skills/your-skill-name"]
}
```

### Marketplace Fields

| Field | Description |
|-------|-------------|
| `name` | Plugin name (must match folder) |
| `description` | Brief description |
| `source` | Path to plugin folder (use `./plugins/name`) |
| `skills` | Array of skill paths within the plugin |

**Common Mistake:** Using `"path"` instead of `"source"` will cause marketplace registration to fail.

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

# Can run specific commands (use uv only when scripts need external deps)
allowed-tools: Read, Write, Edit, Bash(./gradlew:*), Bash(python:*)

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
python scripts/convert.py ftc-to-pedro 1.5 2.0 90
\`\`\`

Mirror red alliance pose for blue:
\`\`\`bash
python scripts/convert.py mirror-blue 7 6.75 0
\`\`\`
```

### Choosing Between `python` and `uv run`

**Use `python` when:**
- Script has NO external dependencies (only uses Python stdlib)
- Maximum accessibility - all systems have Python
- Example: Math conversions, file parsing with `sys`/`json`/`math`

**Use `uv run` when:**
- Script requires external packages (numpy, requests, etc.)
- Need reproducible dependency versions
- Want isolated environment to avoid conflicts
- Example: Data analysis with pandas, API calls with requests

```python
# Simple script with no deps - use `python`
import sys
import math

def convert_coords(x, y):
    return x * 25.4, y * 25.4  # inches to mm

# Complex script with deps - use `uv run`
import numpy as np
import requests

def fetch_and_analyze(url):
    data = requests.get(url).json()
    return np.mean(data['values'])
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

### plugin.json
- [ ] `name` matches folder name (kebab-case)
- [ ] `author` is an object with `name` field (NOT a string)
- [ ] `keywords` array includes "ftc" (NOT `tags`)
- [ ] No invalid fields (`tags`, `compatibility`)

### marketplace.json
- [ ] Entry added with `source` field (NOT `path`)
- [ ] `skills` array lists skill directories

### SKILL.md
- [ ] `name` in frontmatter matches folder name
- [ ] `description` includes WHAT and WHEN triggers
- [ ] `description` includes FTC-specific keywords
- [ ] Under ~500 lines
- [ ] Includes Quick Start section
- [ ] Shows Good AND Bad examples
- [ ] Anti-patterns marked with ❌
- [ ] Code examples are tested and working

### General
- [ ] Scripts are executable (`chmod +x`)
- [ ] No sensitive information (API keys, credentials)

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
| `author` as string | Use object: `{"name": "...", "url": "..."}` |
| Using `tags` field | Rename to `keywords` |
| Using `path` in marketplace | Rename to `source` |
| Using `compatibility` | Remove - not a valid field |
| Vague description | Add specific FTC keywords and trigger scenarios |
| SKILL.md too long | Extract to API_REFERENCE.md, TROUBLESHOOTING.md |
| No anti-patterns | Always show what NOT to do |
| Scripts not executable | `chmod +x scripts/*` |
| Missing Quick Start | Put most common use case first |
| Only Java examples | Include Kotlin if the library supports it |

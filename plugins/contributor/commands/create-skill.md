---
description: Create a new FTC skill plugin from template
argument-hint: <skill-name> [category]
allowed-tools: Read, Write, Edit, Bash(mkdir:*), Bash(chmod:*)
---

# Create Skill Command

Creates a new FTC skill plugin with proper structure and templates.

## Usage

```
/create-skill <skill-name> [category]
```

**Arguments:**
- `skill-name`: Name for the new skill (kebab-case, e.g., `rev-hub`, `roadrunner`)
- `category`: Optional - one of: `hardware`, `library`, `framework`, `tools`, `game`

## Examples

```
/create-skill rev-hub hardware
/create-skill roadrunner library
/create-skill meepmeep tools
```

## Process

When this command is invoked:

1. **Validate the skill name**
   - Must be kebab-case (lowercase, hyphens)
   - Must not already exist in `plugins/`
   - Must be 64 characters or less

2. **Create the plugin structure**
   ```
   plugins/<skill-name>/
   ├── plugin.json
   └── skills/
       └── <skill-name>/
           └── SKILL.md
   ```

3. **Generate plugin.json** with:
   - Name from argument
   - Category from argument (or ask user)
   - Placeholder description
   - MIT license
   - Standard compatibility list

4. **Generate SKILL.md** with:
   - Proper frontmatter (name, description placeholder, license, compatibility, metadata)
   - Template sections (Quick Start, Key Concepts, Patterns, Anti-Patterns, Examples)
   - Placeholder content marked with `[TODO: ...]`

5. **Add to marketplace.json**
   - Add entry to the plugins array
   - Set path to `plugins/<skill-name>`

6. **Prompt user** to fill in:
   - Description (WHAT + WHEN)
   - Quick Start content
   - Code examples
   - Reference documentation

## After Creation

Guide the user through:

1. Writing a good description with FTC-specific keywords
2. Adding Quick Start with working code examples
3. Creating Good/Bad example comparisons
4. Testing the skill activates correctly

## Validation

After creating, suggest running:
```
/validate-skill <skill-name>
```

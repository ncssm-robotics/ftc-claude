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
   ├── CHANGELOG.md
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

5. **Generate CHANGELOG.md** with:
   - Initial version 1.0.0 entry
   - Today's date
   - "Initial release" placeholder

6. **Add to marketplace.json**
   - Add entry to the plugins array
   - Include version field set to "1.0.0"
   - Set source to `./plugins/<skill-name>`

7. **Add to README.md skill table**
   - Add row to appropriate category table (FTC Skills or Contributor Tools)
   - Include skill name, category, and brief description
   - Ensure table stays alphabetically sorted within category

8. **Prompt user** to fill in:
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
5. Verifying README.md skill table entry is accurate

## Validation

After creating, suggest running:
```
/contributor:validate-skill <skill-name>
```

## Checklist

Before completing, verify:
- [ ] `plugins/<skill-name>/plugin.json` created with version "1.0.0"
- [ ] `plugins/<skill-name>/CHANGELOG.md` created with 1.0.0 entry
- [ ] `plugins/<skill-name>/skills/<skill-name>/SKILL.md` created
- [ ] Entry added to `.claude-plugin/marketplace.json` with version
- [ ] Row added to README.md skill table

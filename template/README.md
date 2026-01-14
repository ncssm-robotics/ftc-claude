# Skill Template

Use this template to create a new FTC skill for the marketplace.

## Quick Start

1. Copy this entire `template/` folder to `plugins/your-skill-name/`
2. Rename `skills/my-skill/` to `skills/your-skill-name/`
3. Update `plugin.json` with your skill's metadata
4. Update `SKILL.md` with your skill's content
5. Add any additional documentation files
6. Submit a pull request

## Structure

```
your-skill-name/
├── plugin.json              # Plugin metadata (required)
└── skills/
    └── your-skill-name/
        ├── SKILL.md         # Main skill file (required)
        ├── API_REFERENCE.md # Optional detailed docs
        └── scripts/         # Optional utility scripts
            └── example.py
```

## Checklist

Before submitting your skill:

- [ ] `name` in SKILL.md frontmatter matches folder name
- [ ] `name` is lowercase with hyphens (e.g., `my-cool-skill`)
- [ ] `description` clearly explains when Claude should use this skill
- [ ] Code examples are tested and work
- [ ] No sensitive information (API keys, credentials)
- [ ] License is specified (MIT recommended for FTC community)

## Tips for Good Skills

1. **Clear descriptions** - The `description` field is how Claude decides when to use your skill
2. **Practical examples** - Show copy-paste ready code
3. **Keep it focused** - One skill per library/hardware/concept
4. **Progressive disclosure** - Put common info in SKILL.md, details in reference files

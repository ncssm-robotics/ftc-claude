# Changelog

All notable changes to this plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `/contributor:update-skill` command for generating changelog entries from git diff
- `/contributor:review` command for running local code review checks (same as PR bot)
- `contributor:code-review` skill for structure and content quality checks
- `contributor:security-review` skill with FTC IP whitelist (192.168.43.1, 192.168.49.1)
- `contributor:youth-safety-review` skill for content appropriateness checks
- `contributor:versioning` skill as guardrail against manual version bumps

## [2.0.0] - 2026-01-16

### Removed
- `/contributor:version` command - version bumps are now automated during the release process. Contributors should add changes to `## [Unreleased]` sections in CHANGELOG.md instead. See [RELEASES.md](../../RELEASES.md).

## [1.2.0] - 2025-01-15

### Added
- README.md skill table update step in `/contributor:create-skill`
- CHANGELOG.md generation in `/contributor:create-skill`
- Checklist section in create-skill command
- Documentation sync guidelines in CLAUDE.md for code review

### Changed
- Updated create-skill to include version in marketplace.json entry
- Improved CLAUDE.md code review guidelines for contributor plugin changes

## [1.1.0] - 2025-01-15

### Added
- `/contributor:version` command for guided version bumping
- Interactive changelog generation using AskUserQuestion
- Automatic version synchronization across plugin.json, SKILL.md, and marketplace.json
- Available commands reference table in skill-builder SKILL.md

### Changed
- Updated skill-builder documentation to include versioning workflow
- Improved plugin anatomy diagram to show CHANGELOG.md

## [1.0.0] - 2025-01-15

### Added
- Initial release of contributor tools
- skill-builder skill for creating new plugins
- /create-skill command with guided wizard
- /validate-skill command for pre-PR checks
- Plugin template and structure documentation

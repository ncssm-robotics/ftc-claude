# Changelog

All notable changes to this plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Deprecated
- `/contributor:version` command - version bumps are now automated during the release process. Contributors should add changes to `## [Unreleased]` sections in CHANGELOG.md instead. This command will be removed in v2.0.0.

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

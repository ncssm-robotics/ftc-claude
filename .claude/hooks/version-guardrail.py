#!/usr/bin/env python3
"""
Version guardrail hook - blocks Claude from modifying version fields.
Versions are managed by the automated release process.

Blocks version edits (Edit tool only) in:
- plugins/<name>/plugin.json (version field)
- plugins/<name>/skills/<name>/SKILL.md (metadata.version in frontmatter)
- .claude-plugin/marketplace.json (version fields)

Note: Write tool is allowed because /create-skill needs to write new files
with initial version fields. Only Edit operations are blocked to prevent
accidental version changes to existing files.

Uses JSON output with permissionDecision: deny to block edits.
"""

import json
import re
import sys


def deny_edit(reason: str) -> None:
    """Output JSON to deny the edit and exit."""
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }
    print(json.dumps(output, indent=2))
    sys.exit(0)


def main() -> None:
    # Read input from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)  # Allow if we can't parse input

    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    old_string = tool_input.get("old_string", "")
    new_string = tool_input.get("new_string", "")
    content = tool_input.get("content", "")

    # Check JSON files (plugin.json, marketplace.json)
    if re.search(r"(plugin\.json|marketplace\.json)$", file_path):
        # For Edit tool: check if old_string or new_string contains version pattern
        if '"version"' in old_string or '"version"' in new_string:
            deny_edit(
                "🚫 BLOCKED: Manual version edits are not allowed. "
                "Versions are managed by the automated release process. "
                "Add changes to ## [Unreleased] in CHANGELOG.md instead. "
                "See: .claude/skills/versioning/SKILL.md"
            )

    # Check SKILL.md files for frontmatter version fields
    if file_path.endswith("SKILL.md"):
        # For Edit tool: check for version in YAML frontmatter
        # Matches: version: 1.0.0, version: "1.0.0", version: '1.0.0'
        version_pattern = r'version:\s*["\']?\d'

        if re.search(version_pattern, old_string) or re.search(version_pattern, new_string):
            deny_edit(
                "🚫 BLOCKED: Manual version edits in SKILL.md frontmatter are not allowed. "
                "Versions are managed by the automated release process. "
                "Add changes to ## [Unreleased] in CHANGELOG.md instead. "
                "See: .claude/skills/versioning/SKILL.md"
            )


if __name__ == "__main__":
    main()

#!/bin/bash
# Version guardrail hook - blocks Claude from modifying version fields
# Versions are managed by the automated release process
#
# Blocks version edits in:
# - plugins/<name>/plugin.json (version field)
# - plugins/<name>/skills/<name>/SKILL.md (metadata.version in frontmatter)
# - .claude-plugin/marketplace.json (version fields)
#
# Uses JSON output with permissionDecision: deny to block Edit/Write tools

input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')
old_string=$(echo "$input" | jq -r '.tool_input.old_string // empty')
new_string=$(echo "$input" | jq -r '.tool_input.new_string // empty')
content=$(echo "$input" | jq -r '.tool_input.content // empty')

deny_edit() {
  local reason="$1"
  cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "$reason"
  }
}
EOF
  exit 0
}

# Check JSON files (plugin.json, marketplace.json)
if [[ "$file_path" =~ (plugin\.json|marketplace\.json)$ ]]; then
  # For Edit tool: check if old_string or new_string contains version pattern
  if [[ "$old_string" =~ \"version\" || "$new_string" =~ \"version\" ]]; then
    deny_edit "🚫 BLOCKED: Manual version edits are not allowed. Versions are managed by the automated release process. Add changes to ## [Unreleased] in CHANGELOG.md instead. See: .claude/skills/versioning/SKILL.md"
  fi

  # For Write tool: check if content contains version field
  if [[ -n "$content" && "$content" =~ \"version\" ]]; then
    deny_edit "🚫 BLOCKED: Writing files with version fields is not allowed. Versions are managed by the automated release process. See: .claude/skills/versioning/SKILL.md"
  fi
fi

# Check SKILL.md files for frontmatter version fields
if [[ "$file_path" =~ SKILL\.md$ ]]; then
  # For Edit tool: check for version in YAML frontmatter
  # Matches: version: 1.0.0, version: "1.0.0", version: '1.0.0'
  if [[ "$old_string" =~ version:[[:space:]]*[\"\']?[0-9] || "$new_string" =~ version:[[:space:]]*[\"\']?[0-9] ]]; then
    deny_edit "🚫 BLOCKED: Manual version edits in SKILL.md frontmatter are not allowed. Versions are managed by the automated release process. Add changes to ## [Unreleased] in CHANGELOG.md instead. See: .claude/skills/versioning/SKILL.md"
  fi

  # For Write tool: check for version field in frontmatter
  if [[ -n "$content" && "$content" =~ version:[[:space:]]*[\"\']?[0-9] ]]; then
    deny_edit "🚫 BLOCKED: Writing SKILL.md with version fields is not allowed. Versions are managed by the automated release process. See: .claude/skills/versioning/SKILL.md"
  fi
fi

exit 0

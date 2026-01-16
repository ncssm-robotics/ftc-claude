#!/bin/bash
# Version guardrail hook - reminds Claude to check versioning skill before modifying version fields
file_path=$(jq -r '.tool_input.file_path // empty' 2>/dev/null)
if [[ "$file_path" =~ (plugin\.json|SKILL\.md|marketplace\.json)$ ]]; then
  echo '⚠️ VERSIONING: If modifying version fields, read .claude/skills/versioning/SKILL.md first.'
fi
exit 0

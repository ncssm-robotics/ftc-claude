#!/usr/bin/env bash
#
# Validate an FTC skill plugin
# Usage: ./validate-skill.sh <skill-name>
#

set -e

SKILL_NAME="$1"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
PLUGIN_DIR="$REPO_ROOT/plugins/$SKILL_NAME"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

errors=0
warnings=0

check() {
    local status=$1
    local message=$2
    local level=${3:-error}

    if [ "$status" = "pass" ]; then
        echo -e "  ${GREEN}✓${NC} $message"
    elif [ "$level" = "warning" ]; then
        echo -e "  ${YELLOW}⚠${NC} $message"
        warnings=$((warnings + 1))
    else
        echo -e "  ${RED}✗${NC} $message"
        errors=$((errors + 1))
    fi
}

if [ -z "$SKILL_NAME" ]; then
    echo "Usage: ./validate-skill.sh <skill-name>"
    exit 1
fi

echo "Validating skill: $SKILL_NAME"
echo ""

# Structure checks
echo "Structure:"
if [ -d "$PLUGIN_DIR" ]; then
    check "pass" "Plugin directory exists"
else
    check "fail" "Plugin directory missing: plugins/$SKILL_NAME"
    exit 1
fi

if [ -f "$PLUGIN_DIR/plugin.json" ]; then
    check "pass" "plugin.json exists"
else
    check "fail" "plugin.json missing"
fi

if [ -d "$PLUGIN_DIR/skills/$SKILL_NAME" ]; then
    check "pass" "skills/$SKILL_NAME directory exists"
else
    check "fail" "skills/$SKILL_NAME directory missing"
fi

if [ -f "$PLUGIN_DIR/skills/$SKILL_NAME/SKILL.md" ]; then
    check "pass" "SKILL.md exists"
else
    check "fail" "SKILL.md missing"
fi

echo ""

# plugin.json checks
echo "plugin.json:"
if [ -f "$PLUGIN_DIR/plugin.json" ]; then
    if jq empty "$PLUGIN_DIR/plugin.json" 2>/dev/null; then
        check "pass" "Valid JSON"

        json_name=$(jq -r '.name' "$PLUGIN_DIR/plugin.json")
        if [ "$json_name" = "$SKILL_NAME" ]; then
            check "pass" "Name matches directory"
        else
            check "fail" "Name mismatch: '$json_name' vs '$SKILL_NAME'"
        fi

        if jq -e '.description | length > 0' "$PLUGIN_DIR/plugin.json" > /dev/null 2>&1; then
            check "pass" "Has description"
        else
            check "fail" "Missing description"
        fi

        if jq -e '.tags | contains(["ftc"])' "$PLUGIN_DIR/plugin.json" > /dev/null 2>&1; then
            check "pass" "Has 'ftc' tag"
        else
            check "fail" "Missing 'ftc' tag" "warning"
        fi
    else
        check "fail" "Invalid JSON"
    fi
fi

echo ""

# SKILL.md checks
echo "SKILL.md:"
SKILL_MD="$PLUGIN_DIR/skills/$SKILL_NAME/SKILL.md"
if [ -f "$SKILL_MD" ]; then
    if head -1 "$SKILL_MD" | grep -q "^---$"; then
        check "pass" "Has YAML frontmatter"
    else
        check "fail" "Missing YAML frontmatter"
    fi

    if grep -q "^name:" "$SKILL_MD"; then
        yaml_name=$(sed -n '/^---$/,/^---$/p' "$SKILL_MD" | grep "^name:" | sed 's/name: *//')
        if [ "$yaml_name" = "$SKILL_NAME" ]; then
            check "pass" "Frontmatter name matches"
        else
            check "fail" "Frontmatter name mismatch: '$yaml_name'"
        fi
    else
        check "fail" "Missing 'name' in frontmatter"
    fi

    if grep -q "^description:" "$SKILL_MD"; then
        check "pass" "Has description field"

        if grep -i "use when" "$SKILL_MD" > /dev/null; then
            check "pass" "Description includes WHEN triggers"
        else
            check "fail" "Description missing WHEN triggers" "warning"
        fi
    else
        check "fail" "Missing 'description' in frontmatter"
    fi

    line_count=$(wc -l < "$SKILL_MD" | tr -d ' ')
    if [ "$line_count" -lt 500 ]; then
        check "pass" "Under 500 lines ($line_count lines)"
    else
        check "fail" "Over 500 lines ($line_count lines)" "warning"
    fi
fi

echo ""

# Content checks
echo "Content:"
if [ -f "$SKILL_MD" ]; then
    if grep -qi "quick start\|## quick" "$SKILL_MD"; then
        check "pass" "Has Quick Start section"
    else
        check "fail" "Missing Quick Start section" "warning"
    fi

    if grep -q '```java\|```kotlin' "$SKILL_MD"; then
        check "pass" "Has code examples"
    else
        check "fail" "Missing code examples" "warning"
    fi

    if grep -qi "anti-pattern\|don't\|avoid" "$SKILL_MD"; then
        check "pass" "Has Anti-Patterns section"
    else
        check "fail" "Missing Anti-Patterns section" "warning"
    fi

    if grep -q '\[TODO:' "$SKILL_MD"; then
        check "fail" "Contains [TODO: ...] placeholders" "warning"
    else
        check "pass" "No TODO placeholders"
    fi
fi

echo ""

# marketplace.json check
echo "marketplace.json:"
MARKETPLACE="$REPO_ROOT/.claude-plugin/marketplace.json"
if [ -f "$MARKETPLACE" ]; then
    if jq -e ".plugins[] | select(.name == \"$SKILL_NAME\")" "$MARKETPLACE" > /dev/null 2>&1; then
        check "pass" "Skill is registered in marketplace"
    else
        check "fail" "Skill not in marketplace.json"
    fi
else
    check "fail" "marketplace.json not found"
fi

echo ""

# Summary
total=$((errors + warnings))
passed=$((12 - errors))
echo "Summary: $passed/12 checks passed ($errors errors, $warnings warnings)"

if [ $errors -gt 0 ]; then
    echo -e "\n${RED}Validation failed. Fix errors before submitting.${NC}"
    exit 1
else
    echo -e "\n${GREEN}Validation passed!${NC}"
    exit 0
fi

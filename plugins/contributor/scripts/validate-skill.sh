#!/usr/bin/env bash
#
# Validate an FTC skill plugin
# Usage: ./validate-skill.sh <plugin-name>
#
# Validates plugin structure and all skills listed in marketplace.json

set -e

PLUGIN_NAME="$1"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
PLUGIN_DIR="$REPO_ROOT/plugins/$PLUGIN_NAME"
MARKETPLACE="$REPO_ROOT/.claude-plugin/marketplace.json"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

errors=0
warnings=0
total_checks=0

check() {
    local status=$1
    local message=$2
    local level=${3:-error}

    total_checks=$((total_checks + 1))
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

if [ -z "$PLUGIN_NAME" ]; then
    echo "Usage: ./validate-skill.sh <plugin-name>"
    exit 1
fi

echo "Validating plugin: $PLUGIN_NAME"
echo ""

# Structure checks
echo "Structure:"
if [ -d "$PLUGIN_DIR" ]; then
    check "pass" "Plugin directory exists"
else
    check "fail" "Plugin directory missing: plugins/$PLUGIN_NAME"
    exit 1
fi

if [ -f "$PLUGIN_DIR/plugin.json" ]; then
    check "pass" "plugin.json exists"
else
    check "fail" "plugin.json missing"
fi

if [ -f "$PLUGIN_DIR/CHANGELOG.md" ]; then
    check "pass" "CHANGELOG.md exists"
else
    check "fail" "CHANGELOG.md missing" "warning"
fi

echo ""

# plugin.json checks
echo "plugin.json:"
if [ -f "$PLUGIN_DIR/plugin.json" ]; then
    if jq empty "$PLUGIN_DIR/plugin.json" 2>/dev/null; then
        check "pass" "Valid JSON"

        json_name=$(jq -r '.name' "$PLUGIN_DIR/plugin.json")
        if [ "$json_name" = "$PLUGIN_NAME" ]; then
            check "pass" "Name matches directory"
        else
            check "fail" "Name mismatch: '$json_name' vs '$PLUGIN_NAME'"
        fi

        if jq -e '.description | length > 0' "$PLUGIN_DIR/plugin.json" > /dev/null 2>&1; then
            check "pass" "Has description"
        else
            check "fail" "Missing description"
        fi

        # Check for keywords array with 'ftc' (not tags)
        if jq -e '.keywords | contains(["ftc"])' "$PLUGIN_DIR/plugin.json" > /dev/null 2>&1; then
            check "pass" "Has 'ftc' keyword"
        else
            check "fail" "Missing 'ftc' in keywords array" "warning"
        fi

        # Check author is object not string
        if jq -e '.author | type == "object"' "$PLUGIN_DIR/plugin.json" > /dev/null 2>&1; then
            check "pass" "Author is object (not string)"
        else
            check "fail" "Author must be object, not string"
        fi
    else
        check "fail" "Invalid JSON"
    fi
fi

echo ""

# Get skills from marketplace.json
echo "Skills (from marketplace.json):"
if [ -f "$MARKETPLACE" ]; then
    # Get the skills array for this plugin
    SKILLS_JSON=$(jq -r ".plugins[] | select(.name == \"$PLUGIN_NAME\") | .skills // []" "$MARKETPLACE" 2>/dev/null)

    if [ -z "$SKILLS_JSON" ] || [ "$SKILLS_JSON" = "[]" ] || [ "$SKILLS_JSON" = "null" ]; then
        check "fail" "Plugin not found in marketplace.json or has no skills"
    else
        # Convert JSON array to bash array
        SKILLS=($(echo "$SKILLS_JSON" | jq -r '.[]' | sed 's|^\./skills/||'))

        echo "  Found ${#SKILLS[@]} skill(s): ${SKILLS[*]}"
        echo ""

        for SKILL in "${SKILLS[@]}"; do
            SKILL_DIR="$PLUGIN_DIR/skills/$SKILL"
            SKILL_MD="$SKILL_DIR/SKILL.md"

            echo "  Skill: $SKILL"

            if [ -d "$SKILL_DIR" ]; then
                check "pass" "Directory exists"
            else
                check "fail" "Directory missing: skills/$SKILL"
                continue
            fi

            if [ -f "$SKILL_MD" ]; then
                check "pass" "SKILL.md exists"
            else
                check "fail" "SKILL.md missing"
                continue
            fi

            # Frontmatter checks
            if head -1 "$SKILL_MD" | grep -q "^---$"; then
                check "pass" "Has YAML frontmatter"
            else
                check "fail" "Missing YAML frontmatter"
            fi

            if grep -q "^name:" "$SKILL_MD"; then
                # Extract only the first name: from frontmatter (between first two ---)
                yaml_name=$(awk '/^---$/{p++} p==1 && /^name:/{gsub(/^name: */, ""); print; exit}' "$SKILL_MD")
                if [ "$yaml_name" = "$SKILL" ]; then
                    check "pass" "Frontmatter name matches ($yaml_name)"
                else
                    check "fail" "Frontmatter name mismatch: '$yaml_name' vs '$SKILL'"
                fi
            else
                check "fail" "Missing 'name' in frontmatter"
            fi

            if grep -q "^description:" "$SKILL_MD"; then
                check "pass" "Has description field"
            else
                check "fail" "Missing 'description' in frontmatter"
            fi

            # Line count
            line_count=$(wc -l < "$SKILL_MD" | tr -d ' ')
            if [ "$line_count" -lt 500 ]; then
                check "pass" "Under 500 lines ($line_count lines)"
            else
                check "fail" "Over 500 lines ($line_count lines)" "warning"
            fi

            echo ""
        done
    fi
else
    check "fail" "marketplace.json not found"
fi

# marketplace.json registration check
echo "Marketplace:"
if [ -f "$MARKETPLACE" ]; then
    if jq -e ".plugins[] | select(.name == \"$PLUGIN_NAME\")" "$MARKETPLACE" > /dev/null 2>&1; then
        check "pass" "Plugin is registered in marketplace"

        # Check uses 'source' not 'path'
        if jq -e ".plugins[] | select(.name == \"$PLUGIN_NAME\") | .source" "$MARKETPLACE" > /dev/null 2>&1; then
            check "pass" "Uses 'source' field (not 'path')"
        else
            check "fail" "Missing 'source' field (using deprecated 'path'?)"
        fi
    else
        check "fail" "Plugin not in marketplace.json"
    fi
fi

echo ""

# Summary
passed=$((total_checks - errors))
echo "Summary: $passed/$total_checks checks passed ($errors errors, $warnings warnings)"

if [ $errors -gt 0 ]; then
    echo -e "\n${RED}Validation failed. Fix errors before submitting.${NC}"
    exit 1
else
    echo -e "\n${GREEN}Validation passed!${NC}"
    exit 0
fi

#!/bin/bash
# Version bump utilities for updating plugin versions across all files
# Updates: plugin.json, SKILL.md frontmatter, and marketplace.json

set -euo pipefail

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source version utilities
# shellcheck source=./version-utils.sh
source "$SCRIPT_DIR/version-utils.sh"

# Update version in plugin.json
# Usage: update_plugin_json <plugin_dir> <new_version>
update_plugin_json() {
    local plugin_dir="$1"
    local new_version="$2"

    local plugin_json="$plugin_dir/plugin.json"

    if [ ! -f "$plugin_json" ]; then
        echo "Error: plugin.json not found: $plugin_json" >&2
        return 1
    fi

    # Use jq to update the version field
    local tmp_file
    tmp_file=$(mktemp)

    jq --arg version "$new_version" '.version = $version' "$plugin_json" > "$tmp_file"
    mv "$tmp_file" "$plugin_json"

    echo "Updated version in $plugin_json to $new_version"
}

# Update version in SKILL.md frontmatter
# Usage: update_skill_md <plugin_dir> <plugin_name> <new_version>
update_skill_md() {
    local plugin_dir="$1"
    local plugin_name="$2"
    local new_version="$3"

    local skill_md="$plugin_dir/skills/$plugin_name/SKILL.md"

    if [ ! -f "$skill_md" ]; then
        echo "Error: SKILL.md not found: $skill_md" >&2
        return 1
    fi

    # Use awk to update the version in the frontmatter metadata section
    local tmp_file
    tmp_file=$(mktemp)

    awk -v new_version="$new_version" '
        BEGIN { in_metadata=0; version_updated=0 }

        # Detect metadata section in frontmatter
        /^metadata:/ { in_metadata=1 }

        # If in metadata and line starts with version:, update it
        in_metadata && /^  version:/ {
            print "  version: \"" new_version "\""
            version_updated=1
            next
        }

        # Exit metadata section when indentation returns to base level
        in_metadata && /^[^ ]/ && !/^  / { in_metadata=0 }

        # Print all other lines as-is
        { print }

        END {
            if (!version_updated) {
                print "Warning: version field not found in metadata section" > "/dev/stderr"
            }
        }
    ' "$skill_md" > "$tmp_file"

    mv "$tmp_file" "$skill_md"

    echo "Updated version in $skill_md to $new_version"
}

# Update version in marketplace.json for a specific plugin
# Usage: update_marketplace_json <marketplace_json> <plugin_name> <new_version>
update_marketplace_json_plugin() {
    local marketplace_json="$1"
    local plugin_name="$2"
    local new_version="$3"

    if [ ! -f "$marketplace_json" ]; then
        echo "Error: marketplace.json not found: $marketplace_json" >&2
        return 1
    fi

    # Use jq to update the version for the specific plugin in the plugins array
    local tmp_file
    tmp_file=$(mktemp)

    jq --arg name "$plugin_name" --arg version "$new_version" \
        '(.plugins[] | select(.name == $name) | .version) = $version' \
        "$marketplace_json" > "$tmp_file"

    mv "$tmp_file" "$marketplace_json"

    echo "Updated version for plugin '$plugin_name' in $marketplace_json to $new_version"
}

# Update marketplace version in marketplace.json metadata
# Usage: update_marketplace_version <marketplace_json> <new_version>
update_marketplace_version() {
    local marketplace_json="$1"
    local new_version="$2"

    if [ ! -f "$marketplace_json" ]; then
        echo "Error: marketplace.json not found: $marketplace_json" >&2
        return 1
    fi

    # Use jq to update the metadata.version field
    local tmp_file
    tmp_file=$(mktemp)

    jq --arg version "$new_version" '.metadata.version = $version' \
        "$marketplace_json" > "$tmp_file"

    mv "$tmp_file" "$marketplace_json"

    echo "Updated marketplace version in $marketplace_json to $new_version"
}

# Get current version from plugin.json
# Usage: get_plugin_version <plugin_dir>
get_plugin_version() {
    local plugin_dir="$1"
    local plugin_json="$plugin_dir/plugin.json"

    if [ ! -f "$plugin_json" ]; then
        echo "Error: plugin.json not found: $plugin_json" >&2
        return 1
    fi

    jq -r '.version' "$plugin_json"
}

# Get current marketplace version from marketplace.json
# Usage: get_marketplace_version <marketplace_json>
get_marketplace_version() {
    local marketplace_json="$1"

    if [ ! -f "$marketplace_json" ]; then
        echo "Error: marketplace.json not found: $marketplace_json" >&2
        return 1
    fi

    jq -r '.metadata.version' "$marketplace_json"
}

# Verify version consistency across all three files
# Usage: verify_version_consistency <plugin_dir> <plugin_name> <marketplace_json>
# Returns: 0 if consistent, 1 if inconsistent
verify_version_consistency() {
    local plugin_dir="$1"
    local plugin_name="$2"
    local marketplace_json="$3"

    # Get versions from all three locations
    local plugin_json_version
    plugin_json_version=$(jq -r '.version' "$plugin_dir/plugin.json")

    local skill_md_version
    skill_md_version=$(awk '
        BEGIN { in_metadata=0 }
        /^metadata:/ { in_metadata=1; next }
        in_metadata && /^  version:/ {
            match($0, /"([^"]+)"/, arr)
            print arr[1]
            exit
        }
        in_metadata && /^[^ ]/ { exit }
    ' "$plugin_dir/skills/$plugin_name/SKILL.md")

    local marketplace_version
    marketplace_version=$(jq -r --arg name "$plugin_name" \
        '.plugins[] | select(.name == $name) | .version' \
        "$marketplace_json")

    # Check if all three match
    if [ "$plugin_json_version" = "$skill_md_version" ] && \
       [ "$plugin_json_version" = "$marketplace_version" ]; then
        return 0
    else
        echo "Error: Version mismatch for plugin '$plugin_name':" >&2
        echo "  plugin.json: $plugin_json_version" >&2
        echo "  SKILL.md: $skill_md_version" >&2
        echo "  marketplace.json: $marketplace_version" >&2
        return 1
    fi
}

# Update all version locations for a plugin atomically
# Usage: update_plugin_version <plugin_dir> <plugin_name> <new_version> <marketplace_json>
update_plugin_version() {
    local plugin_dir="$1"
    local plugin_name="$2"
    local new_version="$3"
    local marketplace_json="$4"

    echo "Updating plugin '$plugin_name' to version $new_version..."

    # Validate new version format
    if ! validate_version "$new_version"; then
        echo "Error: Invalid version format: $new_version" >&2
        return 1
    fi

    # Update all three locations
    update_plugin_json "$plugin_dir" "$new_version" || return 1
    update_skill_md "$plugin_dir" "$plugin_name" "$new_version" || return 1
    update_marketplace_json_plugin "$marketplace_json" "$plugin_name" "$new_version" || return 1

    # Verify consistency
    if ! verify_version_consistency "$plugin_dir" "$plugin_name" "$marketplace_json"; then
        echo "Error: Version update failed consistency check" >&2
        return 1
    fi

    echo "✓ Successfully updated plugin '$plugin_name' to version $new_version"
    return 0
}

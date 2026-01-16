#!/bin/bash
# Changelog parser for Keep a Changelog format
# Extracts Unreleased section and determines version bump type

set -euo pipefail

# Determine version bump type from changelog categories
# Priority: Removed/Changed (MAJOR) > Added/Deprecated (MINOR) > Fixed/Security (PATCH)
# Usage: determine_bump_type <changelog_file>
# Returns: "major", "minor", "patch", or "none"
determine_bump_type() {
    local changelog_file="$1"

    if [ ! -f "$changelog_file" ]; then
        echo "Error: Changelog file not found: $changelog_file" >&2
        return 1
    fi

    # Extract the Unreleased section
    local unreleased_section
    unreleased_section=$(extract_unreleased_section "$changelog_file")

    # Check if Unreleased section is empty or only has whitespace
    if [ -z "$(echo "$unreleased_section" | tr -d '[:space:]')" ]; then
        echo "none"
        return 0
    fi

    # Check for MAJOR changes (breaking changes)
    if echo "$unreleased_section" | grep -q "^### Removed"; then
        echo "major"
        return 0
    fi
    if echo "$unreleased_section" | grep -q "^### Changed"; then
        echo "major"
        return 0
    fi

    # Check for MINOR changes (new features)
    if echo "$unreleased_section" | grep -q "^### Added"; then
        echo "minor"
        return 0
    fi
    if echo "$unreleased_section" | grep -q "^### Deprecated"; then
        echo "minor"
        return 0
    fi

    # Check for PATCH changes (bug fixes)
    if echo "$unreleased_section" | grep -q "^### Fixed"; then
        echo "patch"
        return 0
    fi
    if echo "$unreleased_section" | grep -q "^### Security"; then
        echo "patch"
        return 0
    fi

    # If we got here, Unreleased section exists but has no recognized categories
    echo "none"
}

# Extract the Unreleased section from a changelog file
# Usage: extract_unreleased_section <changelog_file>
# Returns: The content of the Unreleased section (excluding the header)
extract_unreleased_section() {
    local changelog_file="$1"

    if [ ! -f "$changelog_file" ]; then
        echo "Error: Changelog file not found: $changelog_file" >&2
        return 1
    fi

    # Use awk to extract content between ## [Unreleased] and the next ## heading
    awk '
        /^## \[Unreleased\]/ { capture=1; next }
        /^## \[/ { capture=0 }
        capture && NF { print }
    ' "$changelog_file"
}

# Move Unreleased section to a versioned section
# Usage: move_unreleased_to_version <changelog_file> <version> <date>
# Modifies the changelog file in place
move_unreleased_to_version() {
    local changelog_file="$1"
    local version="$2"
    local date="$3"

    if [ ! -f "$changelog_file" ]; then
        echo "Error: Changelog file not found: $changelog_file" >&2
        return 1
    fi

    # Validate inputs
    if [ -z "$version" ] || [ -z "$date" ]; then
        echo "Error: Version and date are required" >&2
        return 1
    fi

    # Create a temporary file
    local tmp_file
    tmp_file=$(mktemp)

    # Use awk to transform the changelog
    awk -v version="$version" -v date="$date" '
        # Print everything before Unreleased section as-is
        !found && !/^## \[Unreleased\]/ { print; next }

        # When we find Unreleased header, replace it with new version and keep fresh Unreleased
        /^## \[Unreleased\]/ {
            if (!found) {
                print "## [Unreleased]"
                print ""
                print "## [" version "] - " date
                found = 1
                next
            }
        }

        # After finding Unreleased, print everything else
        found { print }
    ' "$changelog_file" > "$tmp_file"

    # Replace original file with modified version
    mv "$tmp_file" "$changelog_file"
}

# Validate changelog format
# Usage: validate_changelog <changelog_file>
# Returns: 0 if valid, 1 if invalid
validate_changelog() {
    local changelog_file="$1"

    if [ ! -f "$changelog_file" ]; then
        echo "Error: Changelog file not found: $changelog_file" >&2
        return 1
    fi

    # Check if Unreleased section exists
    if ! grep -q "^## \[Unreleased\]" "$changelog_file"; then
        echo "Error: Changelog missing '## [Unreleased]' section: $changelog_file" >&2
        return 1
    fi

    # Check if changelog follows Keep a Changelog format (has # Changelog header)
    if ! grep -q "^# Changelog" "$changelog_file"; then
        echo "Warning: Changelog should start with '# Changelog' header: $changelog_file" >&2
        # Don't fail, just warn
    fi

    return 0
}

# Get list of changes from Unreleased section
# Usage: get_unreleased_changes <changelog_file>
# Returns: Formatted list of changes by category
get_unreleased_changes() {
    local changelog_file="$1"

    if [ ! -f "$changelog_file" ]; then
        echo "Error: Changelog file not found: $changelog_file" >&2
        return 1
    fi

    # Extract and format the Unreleased section
    extract_unreleased_section "$changelog_file"
}

# Check if changelog has unreleased changes
# Usage: has_unreleased_changes <changelog_file>
# Returns: 0 if has changes, 1 if empty
has_unreleased_changes() {
    local changelog_file="$1"

    local unreleased_section
    unreleased_section=$(extract_unreleased_section "$changelog_file" 2>/dev/null)

    # Check if section is empty or only whitespace
    if [ -z "$(echo "$unreleased_section" | tr -d '[:space:]')" ]; then
        return 1
    fi

    return 0
}

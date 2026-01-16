#!/bin/bash
# Version utility functions for semantic versioning
# Provides parsing, validation, increment, and comparison for semantic versions

set -euo pipefail

# Parse a semantic version string into components
# Usage: parse_version "1.2.3" -> returns "1 2 3"
parse_version() {
    local version="$1"

    # Remove 'v' prefix if present
    version="${version#v}"

    # Remove pre-release suffix if present (e.g., 1.2.3-alpha.1 -> 1.2.3)
    version="${version%%-*}"

    # Validate format
    if ! [[ "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo "Error: Invalid semantic version format: $version" >&2
        echo "Expected: X.Y.Z where X, Y, Z are non-negative integers" >&2
        return 1
    fi

    # Split into components
    local major minor patch
    IFS='.' read -r major minor patch <<< "$version"

    echo "$major $minor $patch"
}

# Validate a semantic version string
# Usage: validate_version "1.2.3" -> returns 0 if valid, 1 if invalid
validate_version() {
    local version="$1"

    # Try to parse; if it fails, version is invalid
    if parse_version "$version" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Increment MAJOR version (X.0.0)
# Usage: increment_major "1.2.3" -> "2.0.0"
increment_major() {
    local version="$1"

    local components
    components=$(parse_version "$version") || return 1

    local major minor patch
    read -r major minor patch <<< "$components"

    major=$((major + 1))

    echo "${major}.0.0"
}

# Increment MINOR version (X.Y.0)
# Usage: increment_minor "1.2.3" -> "1.3.0"
increment_minor() {
    local version="$1"

    local components
    components=$(parse_version "$version") || return 1

    local major minor patch
    read -r major minor patch <<< "$components"

    minor=$((minor + 1))

    echo "${major}.${minor}.0"
}

# Increment PATCH version (X.Y.Z)
# Usage: increment_patch "1.2.3" -> "1.2.4"
increment_patch() {
    local version="$1"

    local components
    components=$(parse_version "$version") || return 1

    local major minor patch
    read -r major minor patch <<< "$components"

    patch=$((patch + 1))

    echo "${major}.${minor}.${patch}"
}

# Compare two semantic versions
# Usage: compare_versions "1.2.3" "1.3.0"
# Returns: -1 if v1 < v2, 0 if v1 == v2, 1 if v1 > v2
compare_versions() {
    local v1="$1"
    local v2="$2"

    local components1 components2
    components1=$(parse_version "$v1") || return 1
    components2=$(parse_version "$v2") || return 1

    local major1 minor1 patch1
    local major2 minor2 patch2
    read -r major1 minor1 patch1 <<< "$components1"
    read -r major2 minor2 patch2 <<< "$components2"

    # Compare major
    if [ "$major1" -lt "$major2" ]; then
        echo "-1"
        return 0
    elif [ "$major1" -gt "$major2" ]; then
        echo "1"
        return 0
    fi

    # Compare minor
    if [ "$minor1" -lt "$minor2" ]; then
        echo "-1"
        return 0
    elif [ "$minor1" -gt "$minor2" ]; then
        echo "1"
        return 0
    fi

    # Compare patch
    if [ "$patch1" -lt "$patch2" ]; then
        echo "-1"
        return 0
    elif [ "$patch1" -gt "$patch2" ]; then
        echo "1"
        return 0
    fi

    # Equal
    echo "0"
}

# Get the higher severity bump type between two bump types
# Usage: max_bump_type "minor" "patch" -> "minor"
# Severity order: major > minor > patch > none
max_bump_type() {
    local type1="$1"
    local type2="$2"

    # Convert to lowercase for comparison
    type1=$(echo "$type1" | tr '[:upper:]' '[:lower:]')
    type2=$(echo "$type2" | tr '[:upper:]' '[:lower:]')

    # Define severity levels
    local severity1=0
    local severity2=0

    case "$type1" in
        major) severity1=3 ;;
        minor) severity2=2 ;;
        patch) severity1=1 ;;
        none) severity1=0 ;;
        *)
            echo "Error: Invalid bump type: $type1" >&2
            return 1
            ;;
    esac

    case "$type2" in
        major) severity2=3 ;;
        minor) severity2=2 ;;
        patch) severity2=1 ;;
        none) severity2=0 ;;
        *)
            echo "Error: Invalid bump type: $type2" >&2
            return 1
            ;;
    esac

    # Return the higher severity type
    if [ "$severity1" -ge "$severity2" ]; then
        echo "$type1"
    else
        echo "$type2"
    fi
}

# Apply a bump type to a version
# Usage: apply_bump "1.2.3" "minor" -> "1.3.0"
apply_bump() {
    local version="$1"
    local bump_type="$2"

    bump_type=$(echo "$bump_type" | tr '[:upper:]' '[:lower:]')

    case "$bump_type" in
        major)
            increment_major "$version"
            ;;
        minor)
            increment_minor "$version"
            ;;
        patch)
            increment_patch "$version"
            ;;
        none)
            echo "$version"
            ;;
        *)
            echo "Error: Invalid bump type: $bump_type" >&2
            return 1
            ;;
    esac
}

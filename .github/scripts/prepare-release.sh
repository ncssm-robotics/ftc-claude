#!/bin/bash
# Release preparation script
# Automatically calculates version bumps and creates release PR

set -euo pipefail

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source utility libraries
# shellcheck source=./lib/version-utils.sh
source "$SCRIPT_DIR/lib/version-utils.sh"
# shellcheck source=./lib/changelog-parser.sh
source "$SCRIPT_DIR/lib/changelog-parser.sh"
# shellcheck source=./lib/version-bump.sh
source "$SCRIPT_DIR/lib/version-bump.sh"

# Configuration
DRY_RUN="${DRY_RUN:-false}"
TARGET_BRANCH="${TARGET_BRANCH:-main}"
MARKETPLACE_JSON="$REPO_ROOT/.claude-plugin/marketplace.json"
PLUGINS_DIR="$REPO_ROOT/plugins"
RELEASE_NOTES_FILE="/tmp/RELEASE_NOTES.tmp.md"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ${NC} $*"
}

log_success() {
    echo -e "${GREEN}✓${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $*"
}

log_error() {
    echo -e "${RED}✗${NC} $*" >&2
}

# Main function
main() {
    log_info "Starting release preparation..."
    log_info "Dry run: $DRY_RUN"
    log_info "Target branch: $TARGET_BRANCH"
    echo

    # Ensure we're in the repo root
    cd "$REPO_ROOT"

    # Check if we're on develop branch
    current_branch=$(git branch --show-current)
    if [ "$current_branch" != "develop" ] && [ "$DRY_RUN" = "false" ]; then
        log_error "Must be on 'develop' branch to prepare release"
        log_error "Current branch: $current_branch"
        exit 1
    fi

    # Ensure working directory is clean
    if [ "$DRY_RUN" = "false" ]; then
        if ! git diff --quiet || ! git diff --cached --quiet; then
            log_error "Working directory is not clean. Commit or stash your changes."
            exit 1
        fi
    fi

    # Track changes
    declare -A plugin_bumps
    declare -A plugin_versions
    local highest_bump="none"
    local plugins_changed=0

    # Initialize release notes
    local today
    today=$(date +%Y-%m-%d)
    echo "# Release Notes" > "$RELEASE_NOTES_FILE"
    echo "" >> "$RELEASE_NOTES_FILE"

    # Process each plugin
    log_info "Analyzing plugins for version bumps..."
    echo

    for plugin_dir in "$PLUGINS_DIR"/*; do
        if [ ! -d "$plugin_dir" ]; then
            continue
        fi

        local plugin_name
        plugin_name=$(basename "$plugin_dir")

        local changelog="$plugin_dir/CHANGELOG.md"
        if [ ! -f "$changelog" ]; then
            log_warning "No CHANGELOG.md found for plugin '$plugin_name', skipping"
            continue
        fi

        # Validate changelog format
        if ! validate_changelog "$changelog"; then
            log_error "Invalid changelog format for plugin '$plugin_name'"
            exit 1
        fi

        # Check if plugin has unreleased changes
        if ! has_unreleased_changes "$changelog"; then
            log_info "Plugin '$plugin_name': no unreleased changes, skipping"
            continue
        fi

        # Determine bump type
        local bump_type
        bump_type=$(determine_bump_type "$changelog")

        if [ "$bump_type" = "none" ]; then
            log_info "Plugin '$plugin_name': no recognized changes in Unreleased section, skipping"
            continue
        fi

        # Get current version
        local current_version
        current_version=$(get_plugin_version "$plugin_dir")

        # Calculate new version
        local new_version
        new_version=$(apply_bump "$current_version" "$bump_type")

        # Track this plugin's changes
        plugin_bumps["$plugin_name"]="$bump_type"
        plugin_versions["$plugin_name"]="$new_version"
        plugins_changed=$((plugins_changed + 1))

        # Update highest bump type
        highest_bump=$(max_bump_type "$highest_bump" "$bump_type")

        log_success "Plugin '$plugin_name': $current_version → $new_version ($bump_type)"

        # Extract unreleased changes for release notes
        echo "## $plugin_name ($new_version)" >> "$RELEASE_NOTES_FILE"
        echo "" >> "$RELEASE_NOTES_FILE"
        get_unreleased_changes "$changelog" >> "$RELEASE_NOTES_FILE"
        echo "" >> "$RELEASE_NOTES_FILE"
    done

    echo

    # Check if any plugins were changed
    if [ "$plugins_changed" -eq 0 ]; then
        log_warning "No plugins have unreleased changes. Nothing to release."
        rm -f "$RELEASE_NOTES_FILE"
        exit 0
    fi

    log_info "Plugins to be updated: $plugins_changed"
    log_info "Highest severity bump: $highest_bump"
    echo

    # Calculate new marketplace version
    local current_marketplace_version
    current_marketplace_version=$(get_marketplace_version "$MARKETPLACE_JSON")
    log_info "Current marketplace version: $current_marketplace_version"

    local new_marketplace_version
    new_marketplace_version=$(apply_bump "$current_marketplace_version" "$highest_bump")
    log_info "New marketplace version: $new_marketplace_version"
    echo

    # Stop here if dry run
    if [ "$DRY_RUN" = "true" ]; then
        log_info "Dry run complete. Changes that would be made:"
        echo
        for plugin in "${!plugin_bumps[@]}"; do
            echo "  - $plugin: ${plugin_versions[$plugin]} (${plugin_bumps[$plugin]})"
        done
        echo
        echo "  - Marketplace: $new_marketplace_version ($highest_bump)"
        echo
        log_info "Release notes preview:"
        cat "$RELEASE_NOTES_FILE"
        rm -f "$RELEASE_NOTES_FILE"
        exit 0
    fi

    # Apply version bumps
    log_info "Applying version bumps..."
    echo

    for plugin_name in "${!plugin_bumps[@]}"; do
        local plugin_dir="$PLUGINS_DIR/$plugin_name"
        local new_version="${plugin_versions[$plugin_name]}"
        local changelog="$plugin_dir/CHANGELOG.md"

        # Update plugin version
        if ! update_plugin_version "$plugin_dir" "$plugin_name" "$new_version" "$MARKETPLACE_JSON"; then
            log_error "Failed to update version for plugin '$plugin_name'"
            exit 1
        fi

        # Move Unreleased to versioned section in changelog
        move_unreleased_to_version "$changelog" "$new_version" "$today"
        log_success "Updated changelog for '$plugin_name'"
    done

    echo

    # Update marketplace version
    log_info "Updating marketplace version..."
    update_marketplace_version "$MARKETPLACE_JSON" "$new_marketplace_version"
    log_success "Updated marketplace version to $new_marketplace_version"
    echo

    # Create release branch
    local release_branch="release/v$new_marketplace_version"
    log_info "Creating release branch: $release_branch"
    git checkout -b "$release_branch"

    # Commit changes
    log_info "Committing changes..."
    git add -A
    git commit -m "chore: prepare release v$new_marketplace_version

Automated version bumps:
$(for plugin in "${!plugin_bumps[@]}"; do
    echo "- $plugin: ${plugin_versions[$plugin]} (${plugin_bumps[$plugin]})"
done)

Marketplace version: $new_marketplace_version ($highest_bump)"

    log_success "Changes committed"
    echo

    # Push branch
    log_info "Pushing release branch..."
    git push -u origin "$release_branch"
    log_success "Branch pushed to origin"
    echo

    # Create pull request
    log_info "Creating pull request..."

    # Ensure labels exist (create if missing)
    gh label create release --description "Release PR" --color "0e8a16" 2>/dev/null || true
    gh label create autogenerated --description "Auto-generated by workflow" --color "d4c5f9" 2>/dev/null || true

    # Prepare PR body from release notes
    local pr_body
    pr_body=$(cat "$RELEASE_NOTES_FILE")

    gh pr create \
        --base "$TARGET_BRANCH" \
        --head "$release_branch" \
        --title "Release v$new_marketplace_version" \
        --body "$pr_body" \
        --label "release" \
        --label "autogenerated"

    log_success "Pull request created"
    echo

    # Clean up
    rm -f "$RELEASE_NOTES_FILE"

    log_success "Release preparation complete!"
    log_info "Review the PR and merge when ready."
}

# Run main function
main "$@"

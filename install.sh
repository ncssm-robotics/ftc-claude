#!/usr/bin/env bash
#
# FTC Claude Skills Installer
# Installs skills for Claude Code, Codex CLI, and other compatible agents
#
# Usage:
#   ./install.sh [skill-name...]           # Install specific skills
#   ./install.sh --all                     # Install all skills
#   ./install.sh --list                    # List available skills
#   ./install.sh --agent codex pedro-pathing  # Install to specific agent
#   ./install.sh --project pedro-pathing   # Install to current project
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGINS_DIR="$SCRIPT_DIR/plugins"

# Available skills
AVAILABLE_SKILLS=("decode" "pedro-pathing" "pinpoint" "limelight" "nextftc" "panels" "contributor")

# Agent skill directories
declare -A AGENT_DIRS=(
    ["claude"]="$HOME/.claude/skills"
    ["codex"]="$HOME/.codex/skills"
    ["cursor"]="$HOME/.cursor/skills"
)

# Print colored message
print_msg() {
    local color=$1
    local msg=$2
    echo -e "${color}${msg}${NC}"
}

# Print usage
usage() {
    cat << EOF
FTC Claude Skills Installer

USAGE:
    ./install.sh [OPTIONS] [SKILL...]

OPTIONS:
    --all               Install all available skills
    --list              List available skills
    --agent AGENT       Install to specific agent (claude, codex, cursor)
    --project           Install to current project's .claude/skills/
    --help              Show this help message

SKILLS:
    decode              DECODE 2025-2026 game reference
    pedro-pathing       Pedro Pathing autonomous library
    pinpoint            GoBilda Pinpoint odometry
    limelight           Limelight 3A vision system
    nextftc             NextFTC command-based framework
    panels              Panels debugging dashboard
    contributor         Skill-builder tools for contributors

EXAMPLES:
    ./install.sh pedro-pathing pinpoint     # Install two skills to detected agent
    ./install.sh --all                       # Install all skills
    ./install.sh --agent codex pedro-pathing # Install to Codex CLI
    ./install.sh --project --all             # Install all to current project

EOF
}

# List available skills
list_skills() {
    print_msg "$BLUE" "\nAvailable FTC Skills:\n"
    for skill in "${AVAILABLE_SKILLS[@]}"; do
        local desc=$(grep -m1 '"description"' "$PLUGINS_DIR/$skill/plugin.json" | sed 's/.*: "\(.*\)".*/\1/' | cut -c1-60)
        printf "  ${GREEN}%-16s${NC} %s...\n" "$skill" "$desc"
    done
    echo ""
}

# Detect installed agents
detect_agent() {
    if [ -d "$HOME/.claude" ] || command -v claude &> /dev/null; then
        echo "claude"
    elif [ -d "$HOME/.codex" ] || command -v codex &> /dev/null; then
        echo "codex"
    elif [ -d "$HOME/.cursor" ]; then
        echo "cursor"
    else
        echo ""
    fi
}

# Install a skill
install_skill() {
    local skill=$1
    local target_dir=$2
    local source_dir="$PLUGINS_DIR/$skill/skills/$skill"

    if [ ! -d "$source_dir" ]; then
        print_msg "$RED" "Error: Skill '$skill' not found"
        return 1
    fi

    mkdir -p "$target_dir"
    cp -r "$source_dir" "$target_dir/"
    print_msg "$GREEN" "✓ Installed $skill to $target_dir/$skill"
}

# Main
main() {
    local agent=""
    local project_install=false
    local install_all=false
    local skills_to_install=()

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                usage
                exit 0
                ;;
            --list|-l)
                list_skills
                exit 0
                ;;
            --all|-a)
                install_all=true
                shift
                ;;
            --agent)
                agent="$2"
                shift 2
                ;;
            --project|-p)
                project_install=true
                shift
                ;;
            -*)
                print_msg "$RED" "Unknown option: $1"
                usage
                exit 1
                ;;
            *)
                skills_to_install+=("$1")
                shift
                ;;
        esac
    done

    # Determine target directory
    local target_dir=""
    if [ "$project_install" = true ]; then
        target_dir="$(pwd)/.claude/skills"
        print_msg "$BLUE" "Installing to project: $target_dir"
    elif [ -n "$agent" ]; then
        if [ -z "${AGENT_DIRS[$agent]}" ]; then
            print_msg "$RED" "Unknown agent: $agent"
            print_msg "$YELLOW" "Supported agents: claude, codex, cursor"
            exit 1
        fi
        target_dir="${AGENT_DIRS[$agent]}"
        print_msg "$BLUE" "Installing to $agent: $target_dir"
    else
        # Auto-detect agent
        agent=$(detect_agent)
        if [ -z "$agent" ]; then
            print_msg "$YELLOW" "No coding agent detected. Installing to Claude Code default location."
            agent="claude"
        else
            print_msg "$BLUE" "Detected agent: $agent"
        fi
        target_dir="${AGENT_DIRS[$agent]}"
    fi

    # Determine skills to install
    if [ "$install_all" = true ]; then
        skills_to_install=("${AVAILABLE_SKILLS[@]}")
    fi

    if [ ${#skills_to_install[@]} -eq 0 ]; then
        print_msg "$RED" "No skills specified. Use --list to see available skills."
        usage
        exit 1
    fi

    # Validate skills
    for skill in "${skills_to_install[@]}"; do
        local valid=false
        for available in "${AVAILABLE_SKILLS[@]}"; do
            if [ "$skill" = "$available" ]; then
                valid=true
                break
            fi
        done
        if [ "$valid" = false ]; then
            print_msg "$RED" "Unknown skill: $skill"
            list_skills
            exit 1
        fi
    done

    # Install skills
    print_msg "$BLUE" "\nInstalling ${#skills_to_install[@]} skill(s)...\n"
    for skill in "${skills_to_install[@]}"; do
        install_skill "$skill" "$target_dir"
    done

    print_msg "$GREEN" "\n✓ Installation complete!"
    print_msg "$YELLOW" "\nNote: Restart your coding agent to load the new skills."
}

main "$@"

#!/bin/bash
#
# Howdy User Monitoring Script (Bash Version)
#
# This script periodically checks if the authorized user is present using
# Howdy through PAM authentication and performs actions when the user is not detected.
#
# This implements the solution suggested in GitHub issue #1055.
#
# Usage:
#   ./monitor_user.sh [--interval SECONDS] [--lock-command COMMAND]
#
# Requirements:
#   - Howdy must be properly configured for PAM authentication
#   - pamtester must be installed (sudo apt install libpam-test)
#
# Example:
#   # Check every 5 minutes using default settings
#   ./monitor_user.sh
#
#   # Check every 60 seconds
#   ./monitor_user.sh --interval 60
#

set -euo pipefail

# Default configuration
CHECK_INTERVAL=${CHECK_INTERVAL:-300}  # 5 minutes default
LOCK_COMMAND=${LOCK_COMMAND:-"loginctl lock-session"}
DRY_RUN=${DRY_RUN:-false}
TIMEOUT=${TIMEOUT:-5}  # timeout for pamtester

# Function to display usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Options:
    --interval SECONDS    Time between checks (default: 300)
    --lock-command CMD    Command to execute when user not detected
    --timeout SECONDS     Timeout for authentication check (default: 5)
    --dry-run            Show what would be done without executing
    --help               Show this help message

Environment variables:
    CHECK_INTERVAL       Alternative to --interval
    LOCK_COMMAND         Alternative to --lock-command
    DRY_RUN              Set to 'true' for dry run mode
    TIMEOUT              Alternative to --timeout

Examples:
    $0                           # Default: check every 5 minutes
    $0 --interval 60             # Check every minute
    $0 --dry-run                 # Show actions without executing
EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --interval)
            CHECK_INTERVAL="$2"
            shift 2
            ;;
        --lock-command)
            LOCK_COMMAND="$2"
            shift 2
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Validate interval
if ! [[ "$CHECK_INTERVAL" =~ ^[0-9]+$ ]] || [ "$CHECK_INTERVAL" -lt 10 ]; then
    echo "Error: Interval must be a positive number >= 10 seconds"
    exit 1
fi

# Validate timeout
if ! [[ "$TIMEOUT" =~ ^[0-9]+$ ]] || [ "$TIMEOUT" -lt 1 ]; then
    echo "Error: Timeout must be a positive number >= 1 second"
    exit 1
fi

# Get current user
CURRENT_USER="${USER:-$(whoami)}"

# Function to execute lock command
execute_lock_command() {
    local lock_cmd="$1"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    if [ "$DRY_RUN" = "true" ]; then
        echo "[$timestamp] DRY RUN: Would execute lock command: $lock_cmd"
    else
        echo "[$timestamp] Executing lock command: $lock_cmd"
        eval "$lock_cmd" || echo "Warning: Lock command failed"
    fi
}

# Function to check authentication using pamtester
check_authentication() {
    local timeout="$1"
    
    # Check if pamtester is available
    if ! command -v pamtester >/dev/null 2>&1; then
        echo "Error: pamtester not found. Install with: sudo apt install libpam-test"
        return 2
    fi
    
    # Try authentication with timeout
    if timeout "$timeout" pamtester login "$CURRENT_USER" authenticate >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to get default lock command
get_default_lock_command() {
    # Check desktop environment
    local desktop_session="${DESKTOP_SESSION:-}"
    local xdg_current_desktop="${XDG_CURRENT_DESKTOP:-}"
    
    # Common lock commands for different desktop environments
    if [[ "$desktop_session" == *"gnome"* ]] || [[ "$xdg_current_desktop" == *"GNOME"* ]]; then
        echo "gnome-screensaver-command --lock"
    elif [[ "$desktop_session" == *"kde"* ]] || [[ "$xdg_current_desktop" == *"KDE"* ]]; then
        echo "qdbus org.kde.screensaver /ScreenSaver Lock"
    elif [[ "$desktop_session" == *"xfce"* ]]; then
        echo "xfce4-session-logout --suspend"
    elif [[ "$desktop_session" == *"mate"* ]]; then
        echo "mate-screensaver-command --lock"
    elif [[ "$desktop_session" == *"cinnamon"* ]]; then
        echo "cinnamon-screensaver-command --lock"
    elif command -v loginctl >/dev/null 2>&1; then
        echo "loginctl lock-session"
    else
        echo "xscreensaver-command -lock"
    fi
}

# Main monitoring loop
main() {
    local consecutive_failures=0
    local max_consecutive_failures=3
    
    # Set default lock command if not specified
    if [ -z "${LOCK_COMMAND:-}" ] || [ "$LOCK_COMMAND" = "loginctl lock-session" ]; then
        LOCK_COMMAND=$(get_default_lock_command)
    fi
    
    echo "Howdy User Monitoring Script (Bash Version)"
    echo "=========================================="
    echo "User: $CURRENT_USER"
    echo "Check interval: $CHECK_INTERVAL seconds"
    echo "Lock command: $LOCK_COMMAND"
    echo "Timeout: $TIMEOUT seconds"
    if [ "$DRY_RUN" = "true" ]; then
        echo "Mode: DRY RUN (no actual actions will be performed)"
    fi
    echo ""
    echo "Press Ctrl+C to stop monitoring"
    echo ""
    
    # Check dependencies
    if [ "$DRY_RUN" = "false" ]; then
        if ! check_authentication 1 >/dev/null 2>&1; then
            # pamtester failed, but this might be expected if user is not near camera
            # We'll continue and try again in the main loop
            :
        fi
    fi
    
    while true; do
        local timestamp
        timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        
        echo "[$timestamp] Checking user presence..."
        
        # Check authentication
        if check_authentication "$TIMEOUT"; then
            echo "[$timestamp] User recognized."
            consecutive_failures=0
        else
            local exit_code=$?
            if [ $exit_code -eq 124 ]; then
                echo "[$timestamp] Authentication check timed out after $TIMEOUT seconds"
            else
                echo "[$timestamp] User NOT recognized."
            fi
            
            consecutive_failures=$((consecutive_failures + 1))
            echo "[$timestamp] Authentication failure $consecutive_failures/$max_consecutive_failures"
            
            if [ $consecutive_failures -ge $max_consecutive_failures ]; then
                echo "[$timestamp] Locking session - user not detected $consecutive_failures times!"
                execute_lock_command "$LOCK_COMMAND"
                consecutive_failures=0  # Reset after locking
            fi
        fi
        
        echo "[$timestamp] Sleeping for $CHECK_INTERVAL seconds..."
        echo ""
        sleep "$CHECK_INTERVAL"
    done
}

# Signal handlers for graceful shutdown
trap 'echo ""; echo "Monitoring stopped by user"; exit 0' INT TERM

# Run main function
main "$@"
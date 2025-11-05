#!/bin/bash

# Howdy Monitor Script
# Periodically checks if the user is present using facial recognition
# and locks the screen if the user is not recognized

set -euo pipefail

# Default configuration
CHECK_INTERVAL=${HOWDY_CHECK_INTERVAL:-300}  # 5 minutes
TIMEOUT=${HOWDY_TIMEOUT:-10}                # 10 seconds
FAILURE_THRESHOLD=${HOWDY_FAILURE_THRESHOLD:-2}  # Failures before locking
LOCK_COMMAND=${HOWDY_LOCK_COMMAND:-"loginctl lock-session"}
VERBOSE=${HOWDY_VERBOSE:-false}
USER=${HOWDY_USER:-$USER}

# Function to print help
show_help() {
    cat << EOF
Howdy Monitor Script

Periodically checks if the user is present using facial recognition
and locks the screen if the user is not recognized.

USAGE:
    $0 [OPTIONS]

OPTIONS:
    -i, --interval SECONDS    Check interval in seconds (default: $CHECK_INTERVAL)
    -t, --timeout SECONDS     Recognition timeout in seconds (default: $TIMEOUT)
    -f, --failures COUNT      Failure threshold before locking (default: $FAILURE_THRESHOLD)
    -l, --lock-command CMD    Custom lock command (default: "$LOCK_COMMAND")
    -u, --user USERNAME       User to check (default: current user)
    -v, --verbose             Enable verbose output
    -h, --help                Show this help message

ENVIRONMENT VARIABLES:
    HOWDY_CHECK_INTERVAL      Check interval in seconds
    HOWDY_TIMEOUT            Recognition timeout in seconds  
    HOWDY_FAILURE_THRESHOLD  Failure threshold before locking
    HOWDY_LOCK_COMMAND       Custom lock command
    HOWDY_USER               User to check
    HOWDY_VERBOSE            Enable verbose output

EXAMPLES:
    # Basic usage with 5-minute intervals
    $0

    # Quick checking every minute
    $0 --interval 60

    # Custom lock command with 30-second timeout
    $0 --interval 120 --timeout 30 --lock-command "gnome-screensaver-command --lock"

    # Monitor for specific user with verbose output
    $0 --user john --verbose

INSTALLATION AS SERVICE:
    # Copy to system location
    sudo cp \$0 /usr/local/bin/howdy-monitor

    # Create systemd service
    sudo tee /etc/systemd/system/howdy-monitor.service > /dev/null << SERVICE
[Unit]
Description=Howdy Monitor Service
After=graphical-session.target

[Service]
Type=simple
User=$USER
ExecStart=/usr/local/bin/howdy-monitor
Restart=always
RestartSec=10

[Install]
WantedBy=graphical-session.target
SERVICE

    # Enable and start the service
    sudo systemctl daemon-reload
    sudo systemctl enable howdy-monitor
    sudo systemctl start howdy-monitor

EXIT CODES:
    0 - Normal operation
    1 - Configuration error
    2 - Missing howdy command

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -i|--interval)
            CHECK_INTERVAL="$2"
            shift 2
            ;;
        -t|--timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        -f|--failures)
            FAILURE_THRESHOLD="$2"
            shift 2
            ;;
        -l|--lock-command)
            LOCK_COMMAND="$2"
            shift 2
            ;;
        -u|--user)
            USER="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate configuration
if ! [[ "$CHECK_INTERVAL" =~ ^[0-9]+$ ]] || [ "$CHECK_INTERVAL" -lt 1 ]; then
    echo "Error: CHECK_INTERVAL must be a positive integer"
    exit 1
fi

if ! [[ "$TIMEOUT" =~ ^[0-9]+$ ]] || [ "$TIMEOUT" -lt 1 ]; then
    echo "Error: TIMEOUT must be a positive integer"
    exit 1
fi

if ! [[ "$FAILURE_THRESHOLD" =~ ^[0-9]+$ ]] || [ "$FAILURE_THRESHOLD" -lt 1 ]; then
    echo "Error: FAILURE_THRESHOLD must be a positive integer"
    exit 1
fi

# Check if howdy command is available
if ! command -v howdy >/dev/null 2>&1; then
    echo "Error: howdy command not found. Make sure howdy is installed."
    exit 2
fi

# Function to log messages
log_message() {
    if [ "$VERBOSE" = true ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S'): $1" >&2
    fi
}

# Function to check recognition
check_recognition() {
    local args="--timeout $TIMEOUT"
    if [ -n "$USER" ]; then
        args="$args --user $USER"
    fi
    
    if howdy check $args --quiet; then
        return 0
    else
        return 1
    fi
}

# Function to lock the screen
lock_screen() {
    log_message "USER NOT RECOGNIZED - Locking screen"
    
    if eval "$LOCK_COMMAND"; then
        log_message "Screen locked successfully"
    else
        log_message "Warning: Lock command failed with exit code $?"
    fi
}

# Main monitoring loop
main() {
    local failure_count=0
    
    log_message "Starting Howdy Monitor (user: $USER, interval: ${CHECK_INTERVAL}s, timeout: ${TIMEOUT}s, failures: $FAILURE_THRESHOLD)"
    
    while true; do
        if check_recognition; then
            if [ "$failure_count" -gt 0 ] || [ "$VERBOSE" = true ]; then
                log_message "User recognized (failure count reset from $failure_count)"
            fi
            failure_count=0
        else
            failure_count=$((failure_count + 1))
            log_message "Recognition failed (attempt $failure_count of $FAILURE_THRESHOLD)"
            
            if [ "$failure_count" -ge "$FAILURE_THRESHOLD" ]; then
                lock_screen
                failure_count=0  # Reset after locking
            fi
        fi
        
        sleep "$CHECK_INTERVAL"
    done
}

# Signal handling for graceful shutdown
trap 'log_message "Howdy Monitor stopped"; exit 0' SIGTERM SIGINT

# Start monitoring
main
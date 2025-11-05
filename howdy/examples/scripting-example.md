[complete, functional code content - NOT documentation]
# Howdy Scripting Guide

This guide shows how to use howdy programmatically in scripts and automation.

## Table of Contents
- [Basic Usage](#basic-usage)
- [Monitoring Scripts](#monitoring-scripts)
- [Service Installation](#service-installation)
- [Exit Codes](#exit-codes)
- [Examples](#examples)

## Basic Usage

### The `howdy check` Command

Howdy now includes a `check` command specifically designed for scripting:


# Basic recognition check
howdy check

# Check with custom timeout (5 seconds)
howdy check --timeout 5

# Quiet mode for automation (no output)
howdy check --quiet

# Check a specific user
howdy check john --timeout 5


### Exit Codes

The `check` command returns specific exit codes:

- `0` - User recognized successfully
- `1` - User not recognized or error occurred
- `124` - Recognition timeout occurred

This allows you to use it in conditional statements:


#!/bin/bash
if howdy check --quiet; then
    echo "User recognized"
else
    echo "User not recognized"
fi


## Monitoring Scripts

Two monitoring scripts are provided for periodic verification:

### 1. howdy-monitor.sh

The main monitoring script that uses howdy directly:


# Basic usage
./examples/howdy-monitor.sh

# Check every minute with verbose logging
./examples/howdy-monitor.sh --interval 60 --verbose

# Custom lock command
./examples/howdy-monitor.sh --lock-command "gnome-screensaver-command --lock"

# Disable automatic locking
./examples/howdy-monitor.sh --no-lock


### 2. pamtester-monitor.sh

Alternative script using PAM for verification:


# Install pamtester first
sudo apt install libpam0g-bin

# Run the PAM-based monitor
./examples/pamtester-monitor.sh


## Service Installation

### Systemd Service (howdy-monitor)

1. Copy the monitoring script:

sudo cp examples/howdy-monitor.sh /usr/local/bin/
sudo chmod +x /usr/local/bin/howdy-monitor.sh


2. Create the systemd service file:

sudo tee /etc/systemd/system/howdy-monitor.service > /dev/null <<EOF
[Unit]
Description=Howdy Periodic User Verification
After=multi-user.target

[Service]
Type=simple
User=$USER
Environment=HOME=$HOME
ExecStart=/usr/local/bin/howdy-monitor.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF


3. Enable and start the service:

sudo systemctl daemon-reload
sudo systemctl enable howdy-monitor.service
sudo systemctl start howdy-monitor.service


4. Check service status:

sudo systemctl status howdy-monitor.service


### Custom Service Configuration

You can customize the service by creating an override:


sudo systemctl edit howdy-monitor.service


Add environment variables:

[Service]
Environment=CHECK_INTERVAL=60
Environment=TIMEOUT=5
Environment=MAX_FAILURES=2
Environment=ENABLE_LOCKING=true


## Configuration Options

### Environment Variables

- `CHECK_INTERVAL` - Check interval in seconds (default: 300)
- `TIMEOUT` - Recognition timeout in seconds (default: 10)
- `LOCK_COMMAND` - Command to run when user not recognized (default: `loginctl lock-session`)
- `MAX_FAILURES` - Max consecutive failures before locking (default: 3)
- `ENABLE_LOCKING` - Set to 'false' to disable automatic locking
- `VERBOSE` - Set to 'true' for verbose logging

### Command Line Options

Both monitoring scripts support these options:

- `-i, --interval SECONDS` - Check interval in seconds
- `-t, --timeout SECONDS` - Recognition timeout in seconds
- `-l, --lock-command CMD` - Command to run when user not recognized
- `-m, --max-failures NUM` - Max consecutive failures before locking
- `--no-lock` - Disable automatic locking
- `-v, --verbose` - Enable verbose logging
- `-h, --help` - Show help message

## Examples

### Simple Periodic Check


#!/bin/bash
while true; do
    if howdy check --quiet; then
        echo "$(date): User is present"
    else
        echo "$(date): User not detected, locking screen"
        loginctl lock-session
    fi
    sleep 300  # Check every 5 minutes
done


### Custom Lock Action


#!/bin/bash
# Use a custom lock command
LOCK_COMMAND="gnome-screensaver-command --lock" ./examples/howdy-monitor.sh --lock-command "$LOCK_COMMAND"


### Multiple Failure Threshold


#!/bin/bash
# Require 5 consecutive failures before locking
./examples/howdy-monitor.sh --max-failures 5


### Environment-based Configuration


#!/bin/bash
# Set custom configuration via environment
CHECK_INTERVAL=60 \\
TIMEOUT=5 \\
LOCK_COMMAND="i3lock -c 000000" \\
MAX_FAILURES=2 \\
VERBOSE=true \\
./examples/howdy-monitor.sh


### PAM-based Verification


#!/bin/bash
# Use PAM verification (requires howdy configured for PAM login)
sudo apt install libpam0g-bin
./examples/pamtester-monitor.sh --interval 300


## Troubleshooting

### Recognition Not Working

1. Check if howdy is working:
   ```bash
   howdy test
   ```

2. Verify models exist:
   ```bash
   howdy list
   ```

3. Check camera permissions and availability

### Script Not Running

1. Make scripts executable:
   ```bash
   chmod +x examples/howdy-monitor.sh
   chmod +x examples/pamtester-monitor.sh
   ```

2. Check howdy installation:
   ```bash
   which howdy
   howdy --version
   ```

3. Test the check command:
   ```bash
   howdy check --timeout 5
   ```

### Service Issues

1. Check service status:
   ```bash
   sudo systemctl status howdy-monitor.service
   ```

2. Check service logs:
   ```bash
   sudo journalctl -u howdy-monitor.service -f
   ```

3. Test script manually:
   ```bash
   sudo -u $USER /usr/local/bin/howdy-monitor.sh --verbose
   ```

## Security Notes

- These scripts are designed for convenience, not security
- Howdy is less secure than passwords
- Consider multiple authentication factors for critical systems
- Review and customize lock commands based on your desktop environment
- Monitor logs for suspicious activity

## Advanced Usage

### Integration with Other Tools

You can integrate the howdy check command with other monitoring tools:


# Integration with systemd timers
# Integration with cron jobs
# Integration with desktop environment tools


### Custom Actions

Modify the lock command to perform custom actions:


# Send notification
LOCK_COMMAND="notify-send 'Security Alert' 'User not recognized'; loginctl lock-session"

# Log to file
LOCK_COMMAND="echo '$(date): Lock triggered' >> /var/log/howdy-security.log; loginctl lock-session"

# Send email alert (be careful with authentication)
LOCK_COMMAND="echo 'User not recognized at $(date)' | mail -s 'Security Alert' admin@example.com"
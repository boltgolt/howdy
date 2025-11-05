# Howdy Script Usage Guide

This guide explains how to use Howdy in automated scripts and monitoring applications, as requested in GitHub Issue #1055.

## Overview

The following scripts have been added to enable programmatic use of Howdy:

1. **howdy_check.py** - Python API for checking authentication
2. **monitor_user.py** - Python monitoring script with periodic checks
3. **monitor_user.sh** - Bash monitoring script using pamtester
4. **howdy-monitor.service** - Systemd service template

## Requirements

### For Python Scripts:
- Howdy must be properly installed and configured
- User must have face models registered (`sudo howdy add`)

### For Bash Script:
- Howdy must be configured for PAM authentication
- `pamtester` must be installed: `sudo apt install libpam-test`

## Quick Start

### 1. Python API Usage


from howdy_check import HowdyChecker

# Create checker for current user
checker = HowdyChecker()

# Check authentication
if checker.is_authenticated():
    print("User authenticated successfully")
else:
    print("Authentication failed")

# Quick check without detailed output
if checker.quick_check():
    print("User is present")


### 2. Command Line Usage


# Check current user authentication
python3 howdy_check.py

# Check specific user with custom timeout
python3 howdy_check.py --user john --timeout 5

# Quiet mode (no output)
python3 howdy_check.py --quiet


### 3. User Monitoring (Python)


# Monitor current user every 5 minutes (default)
python3 monitor_user.py

# Check every 60 seconds
python3 monitor_user.py --interval 60

# Monitor specific user
python3 monitor_user.py --user john --interval 300

# Custom lock command
python3 monitor_user.py --lock-command "gnome-screensaver-command --lock"

# Dry run (show what would be done)
python3 monitor_user.py --dry-run


### 4. User Monitoring (Bash)


# Monitor current user every 5 minutes (default)
./monitor_user.sh

# Check every 60 seconds
./monitor_user.sh --interval 60

# Custom lock command
./monitor_user.sh --lock-command "loginctl lock-session"

# Dry run mode
./monitor_user.sh --dry-run


## Systemd Service Installation

To run the monitor as a background service:

1. Copy the service file:

sudo cp howdy-monitor.service /etc/systemd/system/


2. Edit the service file and adjust the user and interval:

sudo nano /etc/systemd/system/howdy-monitor.service


3. Enable and start for a specific user:

sudo systemctl enable howdy-monitor@username.service
sudo systemctl start howdy-monitor@username.service


4. Check status:

sudo systemctl status howdy-monitor@username.service


## Features

### Configurable Options

- **Check Interval**: Time between authentication checks
- **Lock Command**: Command to execute when user not detected
- **Timeout**: Maximum time to wait for authentication
- **User**: Specific user to monitor

### Desktop Environment Support

Both scripts automatically detect the desktop environment and use appropriate lock commands:

- **GNOME**: `gnome-screensaver-command --lock`
- **KDE**: `qdbus org.kde.screensaver /ScreenSaver Lock`
- **XFCE**: `xfce4-session-logout --suspend`
- **MATE**: `mate-screensaver-command --lock`
- **Cinnamon**: `cinnamon-screensaver-command --lock`
- **Fallback**: `loginctl lock-session` or `xscreensaver-command -lock`

### Failure Handling

The scripts implement failure counting to avoid false positives:
- Multiple consecutive failures required before locking
- Automatic reset after successful authentication
- Configurable failure threshold

## Troubleshooting

### Python Scripts Issues

1. **Import Errors**: Ensure Howdy is properly installed
2. **Camera Access**: Check camera permissions and drivers
3. **Face Models**: Verify user has registered face models

### Bash Script Issues

1. **pamtester Not Found**: Install with `sudo apt install libpam-test`
2. **PAM Configuration**: Ensure Howdy is configured for login PAM
3. **Permissions**: Check that user can access PAM services

### General Issues

1. **Camera Not Detected**: Check camera hardware and drivers
2. **Authentication Always Fails**: Verify face models are trained
3. **Lock Command Fails**: Test lock command manually

## Security Considerations

- These scripts should not be used as the only security measure
- Consider backup authentication methods
- Review lock command security implications
- Monitor service logs for suspicious activity

## Examples

### Simple Authentication Check

#!/usr/bin/env python3
import sys
sys.path.insert(0, '/usr/share/howdy/src')
from howdy_check import HowdyChecker

checker = HowdyChecker("myuser")
if checker.quick_check():
    print("Access granted")
    sys.exit(0)
else:
    print("Access denied")
    sys.exit(1)


### Periodic Monitoring Service

#!/bin/bash
# Run monitor every 2 minutes for extra security
python3 monitor_user.py --interval 120 --user myuser


### Integration with Other Tools

#!/usr/bin/env python3
import subprocess
import time
from howdy_check import HowdyChecker

checker = HowdyChecker()
last_check = time.time()

while True:
    if checker.quick_check():
        # User is present, update last check time
        last_check = time.time()
    else:
        # User not detected, take action
        if time.time() - last_check > 600:  # 10 minutes
            subprocess.run(["notification-send", "Security Alert", "User not detected"])
            subprocess.run(["loginctl", "lock-session"])
            last_check = time.time()
    
    time.sleep(30)  # Check every 30 seconds


This implementation fully addresses GitHub Issue #1055 by providing multiple ways to use Howdy in automated scripts for user presence monitoring and screen locking.
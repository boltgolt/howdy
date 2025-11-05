#!/usr/bin/env python3
"""
Howdy User Monitoring Script

This script periodically checks if the authorized user is present using
facial recognition and performs actions when the user is not detected.

This addresses GitHub issue #1055 - providing a way to use Howdy in scripts
for periodic user verification and automatic screen locking.

Usage:
    python3 monitor_user.py [--interval SECONDS] [--user USERNAME] [--lock-command COMMAND]

Example:
    # Check every 5 minutes for the current user
    python3 monitor_user.py --interval 300
    
    # Check every 60 seconds for a specific user
    python3 monitor_user.py --interval 60 --user john
    
    # Custom lock command
    python3 monitor_user.py --lock-command "gnome-screensaver-command --lock"
"""

import sys
import os
import time
import signal
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

try:
    from howdy_check import HowdyChecker
except ImportError as e:
    print(f"Error importing Howdy modules: {e}")
    print("Make sure Howdy is properly installed and howdy_check.py is available")
    sys.exit(1)


class UserMonitor:
    """
    Monitor user presence using Howdy facial recognition
    """
    
    def __init__(self, username=None, check_interval=300, lock_command=None, timeout=10):
        """
        Initialize the user monitor
        
        Args:
            username (str): Username to monitor
            check_interval (int): Time between checks in seconds
            lock_command (str): Command to execute when user not detected
            timeout (int): Timeout for authentication attempts
        """
        self.username = username or os.getenv('USER') or os.getenv('USERNAME')
        self.check_interval = check_interval
        self.lock_command = lock_command or self._get_default_lock_command()
        self.timeout = timeout
        self.running = False
        
        try:
            self.checker = HowdyChecker(self.username, self.timeout)
        except Exception as e:
            print(f"Failed to initialize Howdy checker: {e}")
            raise
    
    def _get_default_lock_command(self):
        """
        Get the default lock command for the current desktop environment
        
        Returns:
            str: Default lock command
        """
        # Check if running in a desktop environment
        desktop_session = os.getenv('DESKTOP_SESSION', '').lower()
        xdg_current_desktop = os.getenv('XDG_CURRENT_DESKTOP', '').lower()
        
        # Common lock commands for different desktop environments
        if 'gnome' in desktop_session or 'gnome' in xdg_current_desktop:
            return "gnome-screensaver-command --lock"
        elif 'kde' in desktop_session or 'kde' in xdg_current_desktop:
            return "qdbus org.kde.screensaver /ScreenSaver Lock"
        elif 'xfce' in desktop_session or 'xfce4' in desktop_session:
            return "xfce4-session-logout --suspend"
        elif 'mate' in desktop_session:
            return "mate-screensaver-command --lock"
        elif ' cinnamon' in desktop_session:
            return "cinnamon-screensaver-command --lock"
        else:
            # Fallback to loginctl if available
            try:
                subprocess.run(['which', 'loginctl'], check=True, capture_output=True)
                return "loginctl lock-session"
            except subprocess.CalledProcessError:
                return "xscreensaver-command -lock"
    
    def _execute_lock_command(self):
        """Execute the lock command"""
        try:
            print(f"{datetime.now()}: Executing lock command: {self.lock_command}")
            subprocess.run(self.lock_command, shell=True, check=False)
        except Exception as e:
            print(f"Error executing lock command: {e}")
    
    def check_user_presence(self):
        """
        Check if the user is currently present
        
        Returns:
            bool: True if user is detected, False otherwise
        """
        try:
            is_authenticated = self.checker.is_authenticated()
            return is_authenticated
        except Exception as e:
            print(f"Error during user presence check: {e}")
            return False
    
    def start_monitoring(self):
        """Start the monitoring loop"""
        self.running = True
        
        print(f"{datetime.now()}: Starting Howdy user monitoring")
        print(f"Monitoring user: {self.username}")
        print(f"Check interval: {self.check_interval} seconds")
        print(f"Lock command: {self.lock_command}")
        print("Press Ctrl+C to stop")
        print()
        
        consecutive_failures = 0
        max_consecutive_failures = 3  # Require multiple failures before locking
        
        try:
            while self.running:
                current_time = datetime.now()
                
                print(f"{current_time}: Checking user presence...")
                is_user_present = self.check_user_presence()
                
                if is_user_present:
                    consecutive_failures = 0
                    print(f"{current_time}: User recognized - continuing monitoring")
                else:
                    consecutive_failures += 1
                    print(f"{current_time}: User NOT recognized (failure {consecutive_failures}/{max_consecutive_failures})")
                    
                    if consecutive_failures >= max_consecutive_failures:
                        print(f"{current_time}: Locking session - user not detected {consecutive_failures} times")
                        self._execute_lock_command()
                        consecutive_failures = 0  # Reset after locking
                
                # Sleep until next check
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print(f"\n{datetime.now()}: Monitoring stopped by user")
        except Exception as e:
            print(f"{datetime.now()}: Unexpected error: {e}")
        finally:
            self.running = False
    
    def stop_monitoring(self):
        """Stop the monitoring loop"""
        self.running = False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Monitor user presence using Howdy and lock screen when user absent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Monitor current user every 5 minutes
  %(prog)s --interval 300          # Check every 5 minutes
  %(prog)s --user john --interval 60 # Monitor user 'john' every minute
  %(prog)s --lock-command "gnome-screensaver-command --lock" # Custom lock command
        """
    )
    
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=300,
        help='Check interval in seconds (default: 300 = 5 minutes)'
    )
    
    parser.add_argument(
        '--user', '-u',
        type=str,
        help='Username to monitor (default: current user)'
    )
    
    parser.add_argument(
        '--lock-command', '-l',
        type=str,
        help='Command to execute when user not detected'
    )
    
    parser.add_argument(
        '--timeout', '-t',
        type=int,
        default=10,
        help='Authentication timeout in seconds (default: 10)'
    )
    
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Show what would be done without actually executing'
    )
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("DRY RUN MODE - No actual actions will be performed")
        print(f"Target user: {args.user or os.getenv('USER')}")
        print(f"Check interval: {args.interval} seconds")
        print(f"Timeout: {args.timeout} seconds")
        if args.lock_command:
            print(f"Lock command: {args.lock_command}")
        else:
            monitor = UserMonitor(args.user, args.interval, None, args.timeout)
            print(f"Default lock command: {monitor.lock_command}")
        sys.exit(0)
    
    try:
        monitor = UserMonitor(args.user, args.interval, args.lock_command, args.timeout)
        monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Failed to start monitoring: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
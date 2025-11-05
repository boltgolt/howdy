#!/usr/bin/env python3
"""
Howdy Python API for programmatic authentication checking

This module provides a simple interface to use Howdy's facial recognition
capabilities in scripts and other applications without relying on PAM.

Usage:
    from howdy_check import HowdyChecker
    
    checker = HowdyChecker("username")
    if checker.is_authenticated():
        print("User authenticated successfully")
    else:
        print("Authentication failed")
"""

import sys
import os
import time
import argparse
from pathlib import Path

# Add the src directory to the path so we can import howdy modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

try:
    from howdy.core import HowdyCore
    from howdy.utils.config import Config
except ImportError as e:
    print(f"Error importing Howdy modules: {e}")
    print("Make sure Howdy is properly installed")
    sys.exit(1)


class HowdyChecker:
    """
    A class to programmatically check authentication using Howdy
    """
    
    def __init__(self, username=None, timeout=10):
        """
        Initialize the Howdy checker
        
        Args:
            username (str): Username to authenticate. If None, uses current user
            timeout (int): Timeout in seconds for authentication attempts
        """
        self.username = username or os.getenv('USER') or os.getenv('USERNAME')
        self.timeout = timeout
        self.core = None
        
        try:
            # Initialize Howdy core
            config = Config()
            self.core = HowdyCore(config)
            self.core.set_user(self.username)
        except Exception as e:
            print(f"Error initializing Howdy: {e}")
            raise
    
    def is_authenticated(self, device_id=-1):
        """
        Check if the user can be authenticated using facial recognition
        
        Args:
            device_id (int): Camera device ID to use
            
        Returns:
            bool: True if authenticated, False otherwise
        """
        try:
            # Attempt authentication
            result = self.core.start_recognition(device_id, self.timeout)
            return result
        except Exception as e:
            print(f"Authentication error: {e}")
            return False
    
    def quick_check(self, device_id=-1):
        """
        Perform a quick authentication check without detailed output
        
        Args:
            device_id (int): Camera device ID to use
            
        Returns:
            bool: True if authenticated, False otherwise
        """
        try:
            # Suppress output for quick checks
            result = self.core.start_recognition(device_id, self.timeout)
            return result
        except:
            return False


def main():
    """Command-line interface for Howdy checking"""
    parser = argparse.ArgumentParser(
        description="Check authentication using Howdy facial recognition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Check current user
  %(prog)s --user john             # Check specific user
  %(prog)s --timeout 5             # Use 5 second timeout
  %(prog)s --quiet                 # Suppress output
        """
    )
    
    parser.add_argument(
        '--user', '-u',
        type=str,
        help='Username to authenticate'
    )
    
    parser.add_argument(
        '--timeout', '-t',
        type=int,
        default=10,
        help='Authentication timeout in seconds (default: 10)'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress output messages'
    )
    
    parser.add_argument(
        '--device-id', '-d',
        type=int,
        default=-1,
        help='Camera device ID (default: auto-detect)'
    )
    
    args = parser.parse_args()
    
    try:
        checker = HowdyChecker(args.user, args.timeout)
        
        if not args.quiet:
            print(f"Checking authentication for user: {checker.username}")
        
        is_authenticated = checker.quick_check(args.device_id)
        
        if is_authenticated:
            if not args.quiet:
                print("Authentication successful")
            sys.exit(0)
        else:
            if not args.quiet:
                print("Authentication failed")
            sys.exit(1)
            
    except Exception as e:
        if not args.quiet:
            print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
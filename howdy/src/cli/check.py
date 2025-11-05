#!/usr/bin/env python3

import sys
import argparse
import time
from pathlib import Path

# Add the parent directory to the path so we can import howdy modules
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import howdy.core.config
    import howdy.core.face_rec
except ImportError as e:
    print(f"Error importing howdy modules: {e}", file=sys.stderr)
    print("Make sure howdy is properly installed", file=sys.stderr)
    sys.exit(1)

def check_recognition(user=None, timeout=10, quiet=False):
    """
    Check facial recognition for a user.
    
    Args:
        user: User to check recognition for (None for current user)
        timeout: Timeout in seconds for the recognition attempt
        quiet: Suppress output
    
    Returns:
        bool: True if recognition successful, False otherwise
    """
    try:
        # Set up configuration
        config = howdy.core.config.Config(user)
        
        # Initialize face recognition
        face_rec = howdy.core.face_rec.FaceRecognition(
            device_id=config.get_option("device_id"),
            db_path=config.get_option("db_path"),
            user=user,
        )
        
        if not quiet:
            print("Checking facial recognition...", file=sys.stderr)
        
        # Set a timeout for the recognition attempt
        import signal
        
        class TimeoutError(Exception):
            pass
        
        def timeout_handler(signum, frame):
            raise TimeoutError("Recognition timed out")
        
        # Set up signal handler for timeout
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(int(timeout))
        
        try:
            # Attempt recognition
            result = face_rec.checkFace()
            signal.alarm(0)  # Cancel the alarm
            
            if result:
                if not quiet:
                    print("✓ User recognized successfully", file=sys.stderr)
                return True
            else:
                if not quiet:
                    print("✗ User not recognized", file=sys.stderr)
                return False
                
        except TimeoutError:
            if not quiet:
                print("⚠ Recognition timeout", file=sys.stderr)
            signal.alarm(0)  # Cancel the alarm
            return False
            
    except Exception as e:
        if not quiet:
            print(f"✗ Recognition error: {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(
        prog='howdy check',
        description='Check facial recognition for scripting purposes'
    )
    parser.add_argument(
        '-u', '--user',
        help='User to check recognition for (default: current user)'
    )
    parser.add_argument(
        '-t', '--timeout',
        type=int,
        default=10,
        help='Timeout in seconds for recognition (default: 10)'
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Suppress output, only return exit code'
    )
    parser.add_argument(
        '--help-extended',
        action='store_true',
        help='Show extended help with usage examples'
    )
    
    args = parser.parse_args()
    
    if args.help_extended:
        print(__doc__)
        print("\nUSAGE EXAMPLES:")
        print("  # Basic recognition check")
        print("  howdy check")
        print("")
        print("  # Check for specific user")
        print("  howdy check --user john")
        print("")
        print("  # Silent check for scripts")
        print("  howdy check --quiet")
        print("")
        print("  # Check with custom timeout")
        print("  howdy check --timeout 5")
        print("")
        print("EXIT CODES:")
        print("  0 - User recognized successfully")
        print("  1 - User not recognized")
        print("  124 - Recognition timeout")
        print("")
        print("SCRIPTING EXAMPLES:")
        print("  # Bash script integration")
        print("  if howdy check --quiet; then")
        print("      echo 'User recognized'")
        print("  else")
        print("      echo 'User not recognized - locking screen'")
        print("      loginctl lock-session")
        print("  fi")
        print("")
        print("  # Periodic checking")
        print("  while true; do")
        print("      if howdy check --timeout 5 --quiet; then")
        print("          echo '$(date): User present'")
        print("      else")
        print("          echo '$(date): User absent - locking'")
        print("          loginctl lock-session")
        print("      fi")
        print("      sleep 60")
        print("  done")
        return 0
    
    # Perform the recognition check
    success = check_recognition(user=args.user, timeout=args.timeout, quiet=args.quiet)
    
    if success:
        return 0
    elif args.timeout and not success:
        return 124  # Timeout exit code
    else:
        return 1

if __name__ == '__main__':
    sys.exit(main())
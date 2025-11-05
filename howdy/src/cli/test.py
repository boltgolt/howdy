[complete, functional code content - NOT documentation]
#!/usr/bin/env python3

import sys
import os
import argparse

# Add the parent directory to the path to get access to howdy functions
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

def run(args):
    """
    Test the camera and recognition methods
    """
    
    if args.user:
        username = args.user
    else:
        import pwd
        username = pwd.getpwuid(os.getuid()).pw_name
    
    print(f"Testing howdy for user: {username}")
    print("Starting camera test...")
    
    try:
        import howdy
        
        # Create recognition session
        recognition = howdy.Recognition(username, debug=True)
        
        print("\nPress Ctrl+C to exit")
        print("Looking for faces...")
        
        # Start recognition
        result = recognition.start()
        
        if result:
            print("\n✓ Face recognized successfully!")
            print(f"User ID: {result}")
            return 0
        else:
            print("\n✗ No face recognized")
            return 1
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        return 0
    except Exception as e:
        print(f"\nError during test: {e}")
        return 1

def help():
    return """Usage: howdy test [user]

Test the camera and recognition methods

Arguments:
    user    Username to test with (defaults to current user)

Examples:
    howdy test
    howdy test john
"""
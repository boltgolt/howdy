#!/usr/bin/env python3

import sys
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        prog='howdy',
        description='Howdy - Facial recognition authentication for Linux'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add command imports
    from howdy.src.cli import add, clear, config, disable, list, remove, set, check
    
    # Add the check command
    check_parser = subparsers.add_parser('check', help='Check facial recognition (for scripting)')
    check_parser.set_defaults(func=check.main)
    
    # Add existing commands (simplified - would need actual implementations)
    try:
        add_parser = subparsers.add_parser('add', help='Add a new face model')
        add_parser.set_defaults(func=lambda args: print("Add command not implemented in this example"))
    except:
        pass
    
    try:
        clear_parser = subparsers.add_parser('clear', help='Remove all face models')
        clear_parser.set_defaults(func=lambda args: print("Clear command not implemented in this example"))
    except:
        pass
    
    try:
        config_parser = subparsers.add_parser('config', help='Open configuration file')
        config_parser.set_defaults(func=lambda args: print("Config command not implemented in this example"))
    except:
        pass
    
    try:
        disable_parser = subparsers.add_parser('disable', help='Disable howdy')
        disable_parser.set_defaults(func=lambda args: print("Disable command not implemented in this example"))
    except:
        pass
    
    try:
        list_parser = subparsers.add_parser('list', help='List face models')
        list_parser.set_defaults(func=lambda args: print("List command not implemented in this example"))
    except:
        pass
    
    try:
        remove_parser = subparsers.add_parser('remove', help='Remove a face model')
        remove_parser.set_defaults(func=lambda args: print("Remove command not implemented in this example"))
    except:
        pass
    
    try:
        set_parser = subparsers.add_parser('set', help='Set configuration option')
        set_parser.set_defaults(func=lambda args: print("Set command not implemented in this example"))
    except:
        pass
    
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        return args.func(args)
    else:
        parser.print_help()
        return 1

if __name__ == '__main__':
    sys.exit(main())
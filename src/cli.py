#!/usr/bin/env python3
# CLI directly called by running the howdy command

# Import required modules
import sys
import os
import getpass
import argparse
import builtins

# Try to get the original username (not "root") from shell
try:
	user = os.getlogin()
except Exception:
	user = os.environ.get("SUDO_USER")

# If that fails, try to get the direct user
if user == "root" or user is None:
	env_user = getpass.getuser().strip()

	# If even that fails, error out
	if env_user == "":
		print("Could not determine user, please use the --user flag")
		sys.exit(1)
	else:
		user = env_user

# Basic command setup
parser = argparse.ArgumentParser(
	description="Command line interface for Howdy face authentication.",
	formatter_class=argparse.RawDescriptionHelpFormatter,
	add_help=False,
	prog="howdy",
	epilog="For support please visit\nhttps://github.com/boltgolt/howdy")

# Add an argument for the command
parser.add_argument(
	"command",
	help="The command option to execute, can be one of the following: add, clear, config, disable, list, remove, snapshot, test or version.",
	metavar="command",
	choices=["add", "clear", "config", "disable", "list", "remove", "snapshot", "test", "version"])

# Add an argument for the extra arguments of diable and remove
parser.add_argument(
	"argument",
	help="Either 0 (enable) or 1 (disable) for the disable command, or the model ID for the remove command.",
	nargs="?")

# Add the user flag
parser.add_argument(
	"-U", "--user",
	default=user,
	help="Set the user account to use.")

# Add the -y flag
parser.add_argument(
	"-y",
	help="Skip all questions.",
	action="store_true")

# Overwrite the default help message so we can use a uppercase S
parser.add_argument(
	"-h", "--help",
	action="help",
	default=argparse.SUPPRESS,
	help="Show this help message and exit.")

# If we only have 1 argument we print the help text
if len(sys.argv) < 2:
	print("current active user: " + user + "\n")
	parser.print_help()
	sys.exit(0)

# Parse all arguments above
args = parser.parse_args()

# Save the args and user as builtins which can be accessed by the imports
builtins.howdy_args = args
builtins.howdy_user = args.user

# Check if we have rootish rights
# This is this far down the file so running the command for help is always possible
if os.getenv("SUDO_USER") is None and os.getuid() != 0:
	print("Please run this command as root:\n")
	print("\tsudo howdy " + " ".join(sys.argv[1:]))
	sys.exit(1)

# Beond this point the user can't change anymore, if we still have root as user we need to abort
if args.user == "root":
	print("Can't run howdy commands as root, please run this command with the --user flag")
	sys.exit(1)

# Execute the right command
if args.command == "add":
	import cli.add
elif args.command == "clear":
	import cli.clear
elif args.command == "config":
	import cli.config
elif args.command == "disable":
	import cli.disable
elif args.command == "list":
	import cli.list
elif args.command == "remove":
	import cli.remove
elif args.command == "snapshot":
	import cli.snap
elif args.command == "test":
	import cli.test
else:
	print("Howdy 2.6.1")

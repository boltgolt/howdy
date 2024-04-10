#!/usr/bin/python3
# CLI directly called by running the howdy command

# Import required modules
import sys
import os
import pwd
import getpass
import argparse
import builtins

from i18n import _

# Try to get the original username (not "root") from shell
sudo_user = os.environ.get("SUDO_USER")
doas_user = os.environ.get("DOAS_USER")
pkexec_uid = os.environ.get("PKEXEC_UID")
pkexec_user = pwd.getpwuid(int(pkexec_uid))[0] if pkexec_uid else ""
env_user = getpass.getuser()
user = next((u for u in [sudo_user, doas_user, pkexec_user, env_user] if u), "")

# If that fails, error out
if user == "":
    print(_("Could not determine user, please use the --user flag"))
    sys.exit(1)

# Basic command setup
parser = argparse.ArgumentParser(
	description=_("Command line interface for Howdy face authentication."),
	formatter_class=argparse.RawDescriptionHelpFormatter,
	add_help=False,
	prog="howdy",
	usage="howdy [-U USER] [--plain] [-h] [-y] {command} [{arguments}...]".format(command=_("command"), arguments=_("arguments")),
	epilog=_("For support please visit\nhttps://github.com/boltgolt/howdy"))

# Add an argument for the command
parser.add_argument(
	_("command"),
	help=_("The command option to execute, can be one of the following: add, clear, config, disable, list, remove, snapshot, set, test or version."),
	metavar="command",
	choices=["add", "clear", "config", "disable", "list", "remove", "set", "snapshot", "test", "version"])

# Add an argument for the extra arguments of disable and remove
parser.add_argument(
	_("arguments"),
	help=_("Optional arguments for the add, disable, remove and set commands."),
	nargs="*")

# Add the user flag
parser.add_argument(
	"-U", "--user",
	default=user,
	help=_("Set the user account to use."))

# Add the -y flag
parser.add_argument(
	"-y",
	help=_("Skip all questions."),
	action="store_true")

# Add the --plain flag
parser.add_argument(
	"--plain",
	help=_("Print machine-friendly output."),
	action="store_true")

# Overwrite the default help message so we can use a uppercase S
parser.add_argument(
	"-h", "--help",
	action="help",
	default=argparse.SUPPRESS,
	help=_("Show this help message and exit."))

# If we only have 1 argument we print the help text
if len(sys.argv) < 2:
	print(_("current active user: ") + user + "\n")
	parser.print_help()
	sys.exit(0)

# Parse all arguments above
args = parser.parse_args()

# Save the args and user as builtins which can be accessed by the imports
builtins.howdy_args = args
builtins.howdy_user = args.user

# Check if we have rootish rights
# This is this far down the file so running the command for help is always possible
if os.geteuid() != 0:
	print(_("Please run this command as root:\n"))
	print("\tsudo howdy " + " ".join(sys.argv[1:]))
	sys.exit(1)

# Beyond this point the user can't change anymore, if we still have root as user we need to abort
if args.user == "root":
	print(_("Can't run howdy commands as root, please run this command with the --user flag"))
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
elif args.command == "set":
	import cli.set
elif args.command == "snapshot":
	import cli.snap
elif args.command == "test":
	import cli.test
else:
	print("Howdy 3.0.0 BETA")

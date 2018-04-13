#!/usr/bin/env python3
# CLI directly called by running the howdy command

# Import required modules
import sys
import os
import subprocess
import getpass
import argparse

user = subprocess.check_output("echo $(logname 2>/dev/null || echo $SUDO_USER)", shell=True).decode("ascii").strip()

if user == "root" or user == "":
	env_user = getpass.getuser().strip()

	if env_user == "root" or env_user == "":
		print("Could not determine user, please use the --user flag")
		sys.exit(1)
	else:
		user = env_user

parser = argparse.ArgumentParser(description="Command line interface for Howdy face authentication.",
								 formatter_class=argparse.RawDescriptionHelpFormatter,
								 add_help=False,
								 prog="howdy",
								 epilog="For support please visit\nhttps://github.com/Boltgolt/howdy")


parser.add_argument("command",
					help="The command option to execute, can be one of the following: add, clear, config, disable, list, remove or test.",
					metavar="command",
					choices=["add", "clear", "config", "disable", "list", "remove", "test"])

parser.add_argument("argument",
					help="Either 0 or 1 for the disable command, or the model ID for the remove command.",
					nargs="?")

parser.add_argument("-U", "--user",
					default=user,
                    help="Set the user account to use.")

parser.add_argument("-y",
                    help="Skip all questions.",
					action="store_true")

parser.add_argument("-h", "--help",
					action="help",
					default=argparse.SUPPRESS,
                    help="Show this help message and exit.")

if len(sys.argv) < 2:
    parser.print_help()
    sys.exit(0)

args = parser.parse_args()

print(args)
sys.exit(1)

# Check if if a command has been given and print help otherwise
if (len(sys.argv) < 2):
	print("Howdy IR face recognition help")
	import cli.help
	sys.exit()

# The command given
cmd = sys.argv[1]

# Call the right files for commands that don't need root
if cmd == "help":
	print("Howdy IR face recognition")
	import cli.help
elif cmd == "test":
	import cli.test
else:
	# Check if the minimum of 3 arugemnts has been met and print help otherwise
	if (len(sys.argv) < 3):
		print("Howdy IR face recognition help")
		import cli.help
		sys.exit()

	# Requre sudo for comamnds that need root rights to read the model files
	if os.getenv("SUDO_USER") is None:
		print("Please run this command with sudo")
		sys.exit(1)

	# Frome here on we require the second argument to be the username,
	# switching the command to the 3rd
	cmd = sys.argv[2]

	if cmd == "list":
		import cli.list
	elif cmd == "add":
		import cli.add
	elif cmd == "remove":
		import cli.remove
	elif cmd == "clear":
		import cli.clear
	else:
		# If the comand is invalid, check if the user hasn't swapped the username and command
		if sys.argv[1] in ["list", "add", "remove", "clear"]:
			print("Usage: howdy <user> <command>")
			sys.exit(1)
		else:
			print('Unknown command "' + cmd + '"')
			import cli.help
			sys.exit(1)

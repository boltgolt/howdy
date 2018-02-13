#!/usr/bin/env python3

# CLI directly called by running the howdy command

# Import required modules
import sys
import os

# Check if the minimum of 3 arugemnts has been met and print help otherwise
if (len(sys.argv) < 3):
	print("Howdy IR face recognition help")
	import cli.help
	sys.exit()

# The command given
cmd = sys.argv[2]

# Requre sudo for comamnds that need root rights to read the model files
if cmd in ["list", "add", "remove", "clear"] and os.getenv("SUDO_USER") is None:
	print("Please run this command with sudo")
	sys.exit()

# Call the right files for the given command
if cmd == "list":
	import cli.list
elif cmd == "help":
	print("Howdy IR face recognition")
	import cli.help
elif cmd == "add":
	import cli.add
elif cmd == "remove":
	import cli.remove
elif cmd == "clear":
	import cli.clear
else:
	# If the comand is invalid, check if the user hasn't swapped the username and command
	if sys.argv[1] in ["list", "add", "remove", "clear", "help"]:
		print("Usage: howdy <user> <command>")
	else:
		print('Unknown command "' + cmd + '"')
		import cli.help

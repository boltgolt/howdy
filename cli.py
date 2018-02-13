#!/usr/bin/env python3
import sys
import os

if (len(sys.argv) < 3):
	print("Howdy IR face recognition help")
	import cli.help
	sys.exit()

user = sys.argv[1]
cmd = sys.argv[2]

if cmd in ["list", "add", "remove", "clear"] and os.getenv("SUDO_USER") is None:
	print("Please run this command with sudo")
	sys.exit()

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
	if sys.argv[1] in ["list", "add", "remove", "clear", "help"]:
		print("Usage: howdy <user> <command>")
	else:
		print('Unknown command "' + cmd + '"')
		import cli.help

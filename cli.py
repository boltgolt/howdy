#!/usr/bin/env python3
import sys

if (len(sys.argv) == 1):
	import cli.help
	sys.exit()

cmd = sys.argv[1]

if cmd == "list":
	import cli.list
elif cmd == "help":
	import cli.help
elif cmd == "add":
	import cli.add

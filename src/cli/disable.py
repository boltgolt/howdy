# Set the disable flag

# Import required modules
import sys
import os
import builtins
import fileinput
import configparser

from i18n import _

# Get the absolute filepath
config_path = os.path.dirname(os.path.abspath(__file__)) + "/../config.ini"

# Read config from disk
config = configparser.ConfigParser()
config.read(config_path)

# Check if enough arguments have been passed
if not builtins.howdy_args.arguments:
	print(_("Please add a 0 (enable) or a 1 (disable) as an argument"))
	sys.exit(1)

# Get the cli argument
argument = builtins.howdy_args.arguments[0]

# Translate the argument to the right string
if argument == "1" or argument.lower() == "true":
	out_value = "true"
elif argument == "0" or argument.lower() == "false":
	out_value = "false"
else:
	# Of it's not a 0 or a 1, it's invalid
	print(_("Please only use 0 (enable) or 1 (disable) as an argument"))
	sys.exit(1)

# Don't do anything when the state is already the requested one
if out_value == config.get("core", "disabled"):
	print(_("The disable option has already been set to ") + out_value)
	sys.exit(1)

# Loop though the config file and only replace the line containing the disable config
for line in fileinput.input([config_path], inplace=1):
	print(line.replace("disabled = " + config.get("core", "disabled"), "disabled = " + out_value), end="")

# Print what we just did
if out_value == "true":
	print(_("Howdy has been disabled"))
else:
	print(_("Howdy has been enabled"))

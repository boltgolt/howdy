# Set the disable flag

# Import required modules
import sys
import os
import json
import builtins
import fileinput
import configparser

# Get the absolute filepath
config_path = os.path.dirname(os.path.abspath(__file__)) + "/../config.ini"

# Read config from disk
config = configparser.ConfigParser()
config.read(config_path)

# Check if enough arguments have been passed
if builtins.howdy_args.argument is None:
	print("Please add a 0 (enable) or a 1 (disable) as an argument")
	sys.exit(1)

# Translate the argument to the right string
if builtins.howdy_args.argument == "1" or builtins.howdy_args.argument.lower() == "true":
	out_value = "true"
elif builtins.howdy_args.argument == "0" or builtins.howdy_args.argument.lower() == "false":
	out_value = "false"
else:
	# Of it's not a 0 or a 1, it's invalid
	print("Please only use false (enable) or true (disable) as an argument")
	sys.exit(1)

# Don't do anything when the state is already the requested one
if out_value == config.get("core", "disabled"):
	print("The disable option has already been set to " + out_value)
	sys.exit(1)

# Loop though the config file and only replace the line containing the disable config
for line in fileinput.input([config_path], inplace=1):
	print(line.replace("disabled = " + config.get("core", "disabled"), "disabled = " + out_value), end="")

# Print what we just did
if builtins.howdy_args.argument == "1":
	print("Howdy has been disabled")
else:
	print("Howdy has been enabled")

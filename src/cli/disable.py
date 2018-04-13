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
if builtins.howdy_args.argument == None:
	print("Please add a 0 (enable) or a 1 (disable) as an argument")
	sys.exit(1)

# Translate the argument to the right string
if builtins.howdy_args.argument == "1":
	out_value = "true"
elif builtins.howdy_args.argument == "0":
	out_value = "false"
else:
	# Of it's not a 0 or a 1, it's invalid
	print("Please only use a 0 (enable) or a 1 (disable) as an argument")
	sys.exit(1)

# Loop though the config file and only replace the line containing the disable config
for line in fileinput.input([config_path], inplace=1):
	print(line.replace("disabled = " + config.get("core", "disabled"), "disabled = " + out_value), end="")

# Print what we just did
if builtins.howdy_args.argument == "1":
	print("Howdy has been disabled")
else:
	print("Howdy has been enabled")

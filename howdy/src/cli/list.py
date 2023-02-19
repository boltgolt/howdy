# List all models for a user

# Import required modules
import sys
import os
import json
import time
import builtins

from i18n import _

# Get the absolute path and the username
path = "/etc/howdy"
user = builtins.howdy_user

# Check if the models file has been created yet
if not os.path.exists(path + "/models"):
	print(_("Face models have not been initialized yet, please run:"))
	print("\n\tsudo howdy -U " + user + " add\n")
	sys.exit(1)

# Path to the models file
enc_file = path + "/models/" + user + ".dat"

# Try to load the models file and abort if the user does not have it yet
try:
	encodings = json.load(open(enc_file))
except FileNotFoundError:
	print(_("No face model known for the user {}, please run:").format(user))
	print("\n\tsudo howdy -U " + user + " add\n")
	sys.exit(1)

# Print a header if we're not in plain mode
if not builtins.howdy_args.plain:
	print(_("Known face models for {}:").format(user))
	print("\n\033[1;29m" + _("ID  Date                 Label\033[0m"))

# Loop through all encodings and print info about them
for enc in encodings:
	# Start with the id
	print(str(enc["id"]), end="")

	# Add comma for machine reading
	if builtins.howdy_args.plain:
		print(",", end="")
	# Print padding spaces after the id for a nice layout
	else:
		print((4 - len(str(enc["id"]))) * " ", end="")

	# Format the time as ISO in the local timezone
	print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(enc["time"])), end="")

	# Separate with commas again for machines, spaces otherwise
	print("," if builtins.howdy_args.plain else "  ", end="")

	# End with the label
	print(enc["label"])

# Add a closing enter
print()

# Remove a encoding from the models file

# Import required modules
import sys
import os
import json
import builtins
import paths_factory

from i18n import _

user = builtins.howdy_user

# Check if enough arguments have been passed
if not builtins.howdy_args.arguments:
	print(_("Please add the ID of the model you want to remove as an argument"))
	print(_("For example:"))
	print("\n\thowdy remove 0\n")
	print(_("You can find the IDs by running:"))
	print("\n\thowdy list\n")
	sys.exit(1)

# Check if the models file has been created yet
if not os.path.exists(paths_factory.user_models_dir_path()):
	print(_("Face models have not been initialized yet, please run:"))
	print("\n\thowdy add\n")
	sys.exit(1)

# Path to the models file
enc_file = paths_factory.user_model_path(user)

# Try to load the models file and abort if the user does not have it yet
try:
	encodings = json.load(open(enc_file))
except FileNotFoundError:
	print(_("No face model known for the user {}, please run:").format(user))
	print("\n\thowdy add\n")
	sys.exit(1)

# Tracks if a encoding with that id has been found
found = False

# Get the ID from the cli arguments
id = builtins.howdy_args.arguments[0]

# Loop though all encodings and check if they match the argument
for enc in encodings:
	if str(enc["id"]) == id:
		# Only ask the user if there's no -y flag
		if not builtins.howdy_args.y:
			# Double check with the user
			print(_('This will remove the model called "{label}" for {user}').format(label=enc["label"], user=user))
			ans = input(_("Do you want to continue [y/N]: "))

			# Abort if the answer isn't yes
			if (ans.lower() != "y"):
				print(_('\nInterpreting as a "NO", aborting'))
				sys.exit(1)

			# Add a padding empty  line
			print()

		# Mark as found and print an enter
		found = True
		break

# Abort if no matching id was found
if not found:
	print(_("No model with ID {id} exists for {user}").format(id=id, user=user))
	sys.exit(1)

# Remove the entire file if this encoding is the only one
if len(encodings) == 1:
	os.remove(paths_factory.user_model_path(user))
	print(_("Removed last model, howdy disabled for user"))
else:
	# A place holder to contain the encodings that will remain
	new_encodings = []

	# Loop though all encodings and only add those that don't need to be removed
	for enc in encodings:
		if str(enc["id"]) != id:
			new_encodings.append(enc)

	# Save this new set to disk
	with open(enc_file, "w") as datafile:
		json.dump(new_encodings, datafile)

	print(_("Removed model {}").format(id))

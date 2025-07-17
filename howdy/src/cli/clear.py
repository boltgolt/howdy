# Clear all models by deleting the whole file

# Import required modules
import os
import sys
import builtins
import paths_factory

from i18n import _

# Get the passed user
user = builtins.howdy_user

# Check if the models folder is there
if not os.path.exists(paths_factory.user_models_dir_path()):
	print(_("No models created yet, can't clear them if they don't exist"))
	sys.exit(1)

# Check if the user has a models file to delete
if not os.path.isfile(paths_factory.user_model_path(user)):
	print(_("{} has no models or they have been cleared already").format(user))
	sys.exit(1)

# Only ask the user if there's no -y flag
if not builtins.howdy_args.y:
	# Double check with the user
	print(_("This will clear all models for ") + user)
	ans = input(_("Do you want to continue [y/N]: "))

	# Abort if they don't answer y or Y
	if (ans.lower() != "y"):
		print(_('\nInterpreting as a "NO", aborting'))
		sys.exit(1)

# Delete otherwise
os.remove(paths_factory.user_model_path(user))
print(_("\nModels cleared"))

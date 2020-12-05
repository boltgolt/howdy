# Remove a encoding from the models file

# Import required modules
import sys
import os
import json
import builtins

# Get the absolute path and the username
path = os.path.dirname(os.path.realpath(__file__)) + "/.."
user = builtins.howdy_user

# Check if enough arguments have been passed
if not builtins.howdy_args.arguments:
	print("Please add the ID of the model you want to remove as an argument")
	print("For example:")
	print("\n\thowdy remove 0\n")
	print("You can find the IDs by running:")
	print("\n\thowdy list\n")
	sys.exit(1)

# Check if the models file has been created yet
if not os.path.exists(path + "/models"):
	print("Face models have not been initialized yet, please run:")
	print("\n\thowdy add\n")
	sys.exit(1)

# Path to the models file
enc_file = path + "/models/" + user + ".dat"

# Try to load the models file and abort if the user does not have it yet
try:
	encodings = json.load(open(enc_file))
except FileNotFoundError:
	print("No face model known for the user " + user + ", please run:")
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
			print('This will remove the model called "' + enc["label"] + '" for ' + user)
			ans = input("Do you want to continue [y/N]: ")

			# Abort if the answer isn't yes
			if (ans.lower() != "y"):
				print('\nInterpreting as a "NO", aborting')
				sys.exit(1)

			# Add a padding empty  line
			print()

		# Mark as found and print an enter
		found = True
		break

# Abort if no matching id was found
if not found:
	print("No model with ID " + id + " exists for " + user)
	sys.exit(1)

# Remove the entire file if this encoding is the only one
if len(encodings) == 1:
	os.remove(path + "/models/" + user + ".dat")
	print("Removed last model, howdy disabled for user")
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

	print("Removed model " + id)

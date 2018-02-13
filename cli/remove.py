# Remove a encoding from the models file

# Import required modules
import sys
import os
import json

# Get the absolute path and the username
path = os.path.dirname(os.path.realpath(__file__))  + "/.."
user = sys.argv[1]

# Check if enough arguments have been passed
if len(sys.argv) == 3:
	print("Please add the ID of the model to remove as an argument")
	print("You can find the IDs by running:")
	print("\n\thowdy " + user + " list\n")
	sys.exit(1)

# Check if the models file has been created yet
if not os.path.exists(path + "/models"):
	print("Face models have not been initialized yet, please run:")
	print("\n\thowdy " + user + " add\n")
	sys.exit(1)

# Path to the models file
enc_file = path + "/models/" + user + ".dat"

# Try to load the models file and abort if the user does not have it yet
try:
	encodings = json.load(open(enc_file))
except FileNotFoundError:
	print("No face model known for the user " + user + ", please run:")
	print("\n\thowdy " + user + " add\n")
	sys.exit(1)

# Tracks if a encoding with that id has been found
found = False

# Loop though all encodings and check if they match the argument
for enc in encodings:
	if str(enc["id"]) == sys.argv[3]:
		# Double check with the user
		print('This will remove the model called "' + enc["label"] + '" for ' + user)
		ans = input("Do you want to continue [y/N]: ")

		# Abort if the answer isn't yes
		if (ans.lower() != "y"):
			print('\nInerpeting as a "NO"')
			sys.exit()

		# Mark as found and print an enter
		found = True
		print()
		break

# Abort if no matching id was found
if not found:
	print("No model with ID " + sys.argv[3] + " exists for " + user)
	sys.exit()

# Remove the entire file if this encoding is the only one
if len(encodings) == 1:
	os.remove(path + "/models/" + user + ".dat")
	print("Removed last model, howdy disabled for user")
else:
	# A place holder to contain the encodings that will remain
	new_encodings = []

	# Loop though all encodin and only add thos that don't need to be removed
	for enc in encodings:
		if str(enc["id"]) != sys.argv[3]:
			new_encodings.append(enc)

	# Save this new set to disk 
	with open(enc_file, "w") as datafile:
		json.dump(new_encodings, datafile)

	print("Removed model " + sys.argv[3])

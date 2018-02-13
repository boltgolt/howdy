import sys
import os
import json

path = os.path.dirname(os.path.realpath(__file__))  + "/.."
user = sys.argv[1]

if len(sys.argv) == 3:
	print("Please add the ID of the model to remove as an argument")
	print("You can find the IDs by running:")
	print("\n\thowdy " + user + " list\n")
	sys.exit(1)

if not os.path.exists(path + "/models"):
	print("Face models have not been initialized yet, please run:")
	print("\n\thowdy " + user + " add\n")
	sys.exit(1)

enc_file = path + "/models/" + user + ".dat"

try:
	encodings = json.load(open(enc_file))
except FileNotFoundError:
	print("No face model known for the user " + user + ", please run:")
	print("\n\thowdy " + user + " add\n")
	sys.exit(1)

found = False

for enc in encodings:
	if str(enc["id"]) == sys.argv[3]:
		print('This will remove the model called "' + enc["label"] + '" for ' + user)
		ans = input("Do you want to continue [y/N]: ")

		if (ans.lower() != "y"):
			print('\nInerpeting as a "NO"')
			sys.exit()

		found = True
		print()
		break

if not found:
	print("No model with ID " + sys.argv[3] + " exists for " + user)
	sys.exit()

if len(encodings) == 1:
	os.remove(path + "/models/" + user + ".dat")
	print("Removed last model, howdy disabled for user")
else:
	new_encodings = []

	for enc in encodings:
		if str(enc["id"]) != sys.argv[3]:
			new_encodings.append(enc)

	with open(enc_file, "w") as datafile:
		json.dump(new_encodings, datafile)

	print("Removed model " + sys.argv[3])

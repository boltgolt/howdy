# Clear all models by deleting the whole file

# Import required modules
import os
import sys

# Get the full path to this file
path = os.path.dirname(os.path.abspath(__file__))
# Get the passed user
user = sys.argv[1]

# Check if the models folder is there
if not os.path.exists(path + "/../models"):
	print("No models created yet, can't clear them if they don't exist")
	sys.exit()

# Check if the user has a models file to delete
if not os.path.isfile(path + "/../models/" + user + ".dat"):
	print(user + " has no models or they have been cleared already")
	sys.exit()

# Double check with the user
print("This will clear all models for " + user)
ans = input("Do you want to continue [y/N]: ")

# Abort if they don't answer y or Y
if (ans.lower() != "y"):
	print('\nInerpeting as a "NO"')
	sys.exit()

# Delete otherwise
os.remove(path + "/../models/" + user + ".dat")
print("\nModels cleared")

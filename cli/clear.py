import os
import sys

# Get the full path to this file
path = os.path.dirname(os.path.abspath(__file__))
# Get the passed user
user = sys.argv[1]

if not os.path.exists(path + "/../models"):
	print("No models created yet, can't clear them if they don't exist")
	sys.exit()

if not os.path.isfile(path + "/../models/" + user + ".dat"):
	print(user + " has no models or they have been cleared already")
	sys.exit()

print("This will clear all models for " + user)
ans = input("Do you want to continue [y/N]: ")

if (ans.lower() != "y"):
	print('\nInerpeting as a "NO"')
	sys.exit()

os.remove(path + "/../models/" + user + ".dat")
print("\nModels cleared")

# Useful support functions

def print_menu(encodings):
	"""Show a menu asking the user what he wants to do"""
	if len(encodings) == 3:
		print("There is 1 existing face model for this user")
	else:
		print("There are " + str(int(len(encodings) / 3)) + " existing face models for this user")
	print("What do you want to do?\n")

	print("1: Add additional face model")
	print("2: Overwrite older model(s)")
	print("0: Exit")

	com = input("Option: ")

	if com == "1":
		return encodings
	elif com == "2":
		return []
	elif com == "0":
		sys.exit()
	else:
		print("Invalid option '" + com + "'\n")
		return print_menu(encodings)

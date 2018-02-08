#!/usr/bin/env python3
import sys
import os
import json
import time

path = os.path.dirname(os.path.realpath(__file__))
cmd = sys.argv[1]

if cmd == "list":
	if not os.path.exists(path + "/models"):
		print("Face models have not been initialized yet, please run:")
		print("\n\thowdy add\n")
		sys.exit(1)

	user = os.environ.get("USER")
	enc_file = path + "/models/" + user + ".dat"

	try:
		encodings = json.load(open(enc_file))
	except FileNotFoundError:
		print("No face model known for the current user (" + user + "), please run:")
		print("\n\thowdy add\n")
		sys.exit(1)

	print("Known face models for " + user + ":")
	print("\n\t\033[1;29mID  Date                 Label\033[0m")

	for enc in encodings:
		print("\t" + str(enc["id"]), end="")
		print((4 - len(str(enc["id"]))) * " ", end="")
		print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(enc["time"])), end="")
		print("  " + enc["label"])

	print()

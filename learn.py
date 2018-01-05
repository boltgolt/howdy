import face_recognition
import subprocess
import time
import os
import sys
import json

import config
import utils

def captureFrame(delay):
	subprocess.call(["fswebcam", "-S", str(delay), "--no-banner", "-d", "/dev/video" + str(config.device_id), tmp_file], stderr=open(os.devnull, "wb"))

	ref = face_recognition.load_image_file(tmp_file)
	enc = face_recognition.face_encodings(ref)

	if len(enc) == 0:
		print("No face detected, aborting")
		sys.exit()
	if len(enc) > 1:
		print("Multiple faces detected, aborting")
		sys.exit()

	clean_enc = []

	for point in enc[0]:
		clean_enc.append(point)

	encodings.append(clean_enc)

user = os.environ.get("USER")
tmp_file = "/tmp/howdy_" + user + ".jpg"
enc_file = "./models/" + user + ".dat"
encodings = []

if not os.path.exists("models"):
	print("No face model folder found, creating one")
	os.makedirs("models")

try:
	encodings = json.load(open(enc_file))
except FileNotFoundError:
	encodings = False

if encodings != False:
	encodings = utils.print_menu(encodings)

print("\nLearning face for the user account " + user)
print("Please look straight into the camera for 5 seconds")

time.sleep(2)

for delay in [30, 6, 0]:
	time.sleep(.3)
	captureFrame(delay)

with open(enc_file, "w") as datafile:
	json.dump(encodings, datafile)

os.remove(tmp_file)

print("Done.")

# Save the face of the user in encoded form

# Import required modules
import face_recognition
import subprocess
import time
import os
import sys
import json

# Import config and extra functions
import config
import utils

def captureFrame(delay):
	"""Capture and encode 1 frame of video"""

	# Call fswebcam to save a frame to /tmp with a set delay
	subprocess.call(["fswebcam", "-S", str(delay), "--no-banner", "-d", "/dev/video" + str(config.device_id), tmp_file], stderr=open(os.devnull, "wb"))

	# Get the faces in htat image
	ref = face_recognition.load_image_file(tmp_file)
	enc = face_recognition.face_encodings(ref)

	# If 0 faces are detected we can't continue
	if len(enc) == 0:
		print("No face detected, aborting")
		sys.exit()
	# If more than 1 faces are detected we can't know wich one belongs to the user
	if len(enc) > 1:
		print("Multiple faces detected, aborting")
		sys.exit()

	clean_enc = []

	# Copy the values into a clean array so we can export it as JSON later on
	for point in enc[0]:
		clean_enc.append(point)

	encodings.append(clean_enc)

# The current user
user = os.environ.get("USER")
# The name of the tmp frame file to user
tmp_file = "/tmp/howdy_" + user + ".jpg"
# The permanent file to store the encoded model in
enc_file = "./models/" + user + ".dat"
# Known encodings
encodings = []

# Make the ./models folder if it doesn't already exist
if not os.path.exists("models"):
	print("No face model folder found, creating one")
	os.makedirs("models")

# To try read a premade encodings file if it exists
try:
	encodings = json.load(open(enc_file))
except FileNotFoundError:
	encodings = False

# If a file does exist, ask the user what needs to be done
if encodings != False:
	encodings = utils.print_menu(encodings)

print("\nLearning face for the user account " + user)
print("Please look straight into the camera for 5 seconds")

# Give the user time to read
time.sleep(2)

# Capture with 3 different delays to simulate different camera exposures
for delay in [30, 6, 0]:
	time.sleep(.3)
	captureFrame(delay)

# Save the new encodings to disk
with open(enc_file, "w") as datafile:
	json.dump(encodings, datafile)

# Remove any left over temp files
os.remove(tmp_file)

print("Done.")

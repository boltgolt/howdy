# Save the face of the user in encoded form

# Import required modules
import subprocess
import time
import os
import sys
import json

# Import config
import configparser

try:
	import face_recognition
except ImportError as err:
	print(err)

	print("\nCan't import face_recognition module, check the output of")
	print("pip3 show face_recognition")
	sys.exit()

path = os.path.dirname(os.path.abspath(__file__))

# Read config from disk
config = configparser.ConfigParser()
config.read(path + "/../config.ini")

def captureFrame(delay):
	"""Capture and encode 1 frame of video"""
	global insert_model

	# Call fswebcam to save a frame to /tmp with a set delay
	exit_code = subprocess.call(["fswebcam", "-S", str(delay), "--no-banner", "-d", "/dev/video" + str(config.get("video", "device_id")), tmp_file])

	# Check if fswebcam exited normally
	if (exit_code != 0):
		print("Webcam frame capture failed!")
		print("Please make sure fswebcam is installed on this system")
		sys.exit()

	# Try to load the image from disk
	try:
		ref = face_recognition.load_image_file(tmp_file)
	except FileNotFoundError:
		print("No webcam frame captured, check if /dev/video" + str(config.get("video", "device_id")) + " is the right webcam")
		sys.exit()

	# Make a face encoding from the loaded image
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

	insert_model["data"].append(clean_enc)

# The current user
user = os.environ.get("USER")
# The name of the tmp frame file to user
tmp_file = "/tmp/howdy_" + user + ".jpg"
# The permanent file to store the encoded model in
enc_file = path + "/../models/" + user + ".dat"
# Known encodings
encodings = []

# Make the ./models folder if it doesn't already exist
if not os.path.exists(path + "/../models"):
	print("No face model folder found, creating one")
	os.makedirs(path + "/../models")

# To try read a premade encodings file if it exists
try:
	encodings = json.load(open(enc_file))
except FileNotFoundError:
	encodings = []

print("Adding face model for the user account " + user)

label = "Initial model"

if len(encodings) > 0:
	label = "Model #" + str(len(encodings) + 1)

label_in = input("Enter a label for this new model [" + label + "]: ")

if label_in != "":
	label = label_in

insert_model = {
	"time": int(time.time()),
	"label": label,
	"id": len(encodings),
	"data": []
}

print("\nPlease look straight into the camera for 5 seconds")

# Give the user time to read
time.sleep(2)

# Capture with 3 different delays to simulate different camera exposures
for delay in [30, 6, 0]:
	time.sleep(.3)
	captureFrame(delay)

encodings.append(insert_model)

# Save the new encodings to disk
with open(enc_file, "w") as datafile:
	json.dump(encodings, datafile)

# Remove any left over temp files
os.remove(tmp_file)

print("Done.")

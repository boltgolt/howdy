# Save the face of the user in encoded form

# Import required modules
import subprocess
import time
import os
import sys
import json
import cv2
import configparser
import builtins

# Try to import face_recognition and give a nice error if we can't
# Add should be the first point where import issues show up
try:
	import face_recognition
except ImportError as err:
	print(err)

	print("\nCan't import the face_recognition module, check the output of")
	print("pip3 show face_recognition")
	sys.exit(1)

# Get the absolute path to the current file
path = os.path.dirname(os.path.abspath(__file__))

# Read config from disk
config = configparser.ConfigParser()
config.read(path + "/../config.ini")

user = builtins.howdy_user
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

# Print a warning if too many encodings are being added
if len(encodings) > 3:
	print("WARNING: Every additional model slows down the face recognition engine")
	print("Press ctrl+C to cancel\n")

print("Adding face model for the user " + user)

# Set the default label
label = "Initial model"

# If models already exist, set that default label
if len(encodings) > 0:
	label = "Model #" + str(len(encodings) + 1)

# Keep de default name if we can't ask questions
if builtins.howdy_args.y:
	print("Using default label \"" + label + "\" because of -y flag")
else:
	# Ask the user for a custom label
	label_in = input("Enter a label for this new model [" + label + "]: ")

	# Set the custom label (if any) and limit it to 24 characters
	if label_in != "":
		label = label_in[:24]

# Prepare the metadata for insertion
insert_model = {
	"time": int(time.time()),
	"label": label,
	"id": len(encodings),
	"data": []
}

# Open the camera
video_capture = cv2.VideoCapture(int(config.get("video", "device_id")))

# Force MJPEG decoding if true
if config.get("video", "force_mjpeg") == "true":
	video_capture.set(cv2.CAP_PROP_FOURCC, 1196444237)

# Set the frame width and height if requested
if int(config.get("video", "frame_width")) != -1:
	video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, int(config.get("video", "frame_width")))

if int(config.get("video", "frame_height")) != -1:
	video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, int(config.get("video", "frame_height")))

# Request a frame to wake the camera up
video_capture.read()

print("\nPlease look straight into the camera")

# Give the user time to read
time.sleep(2)

# Will contain found face encodings
enc = []
# Count the amount or read frames
frames = 0

# Loop through frames till we hit a timeout
while frames < 60:
	frames += 1

	# Grab a single frame of video
	# Don't remove ret, it doesn't work without it
	ret, frame = video_capture.read()

	# Get the encodings in the frame
	enc = face_recognition.face_encodings(frame)

	# If we've found at least one, we can continue
	if len(enc) > 0:
		break

# If 0 faces are detected we can't continue
if len(enc) == 0:
	print("No face detected, aborting")
	sys.exit(1)

# If more than 1 faces are detected we can't know wich one belongs to the user
if len(enc) > 1:
	print("Multiple faces detected, aborting")
	sys.exit(1)

# Totally clean array that can be exported as JSON
clean_enc = []

# Copy the values into a clean array so we can export it as JSON later on
for point in enc[0]:
	clean_enc.append(point)

insert_model["data"].append(clean_enc)

# Insert full object into the list
encodings.append(insert_model)

# Save the new encodings to disk
with open(enc_file, "w") as datafile:
	json.dump(encodings, datafile)

# Give let the user know how it went
print("""Scan complete

Added a new model to """ + user)

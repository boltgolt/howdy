# Compare incomming video with known faces
# Running in a local python instance to get around PATH issues

# Import required modules
import cv2
import sys
import os
import json
import time
import math
import configparser

# Start timing
timings = [time.time()]

# Import face recognition, takes some time
import face_recognition
timings.append(time.time())

# Read config from disk
config = configparser.ConfigParser()
config.read(os.path.dirname(os.path.abspath(__file__)) + "/config.ini")

def stop(status):
	"""Stop the execution and close video stream"""
	video_capture.release()
	sys.exit(status)

# Make sure we were given an username to tast against
try:
	if not isinstance(sys.argv[1], str):
		sys.exit(1)
except IndexError:
	sys.exit(1)

# The username of the authenticating user
user = sys.argv[1]
# The model file contents
models = []
# Encoded face models
encodings = []
# Amount of frames already matched
tries = 0

# Try to load the face model from the models folder
try:
	models = json.load(open(os.path.dirname(os.path.abspath(__file__)) + "/models/" + user + ".dat"))
except FileNotFoundError:
	sys.exit(10)

# Check if the file contains a model
if len(models) < 1:
	sys.exit(10)

# Put all models together into 1 array
for model in models:
	encodings += model["data"]

# Start video capture on the IR camera
video_capture = cv2.VideoCapture(int(config.get("video", "device_id")))
timings.append(time.time())

# Start the read loop
frames = 0
while True:
	frames += 1

	# Grab a single frame of video
	# Don't remove ret, it doesn't work without it
	ret, frame = video_capture.read()

	# Get all faces from that frame as encodings
	face_encodings = face_recognition.face_encodings(frame)

	# Loop through each face
	for face_encoding in face_encodings:
		# Match this found face against a known face
		matches = face_recognition.face_distance(encodings, face_encoding)

		# Check if any match is certain enough to be the user we're looking for
		match_index = 0
		for match in matches:
			match_index += 1

			# Try to find a match that's confident enough
			if match * 10 < float(config.get("video", "certainty")) and match > 0:
				timings.append(time.time())

				# If set to true in the config, print debug text
				if config.get("debug", "end_report") == "true":
					print("DEBUG END REPORT\n")

					print("Time spend")
					print("  Importing face_recognition: " + str(round((timings[1] - timings[0]) * 1000)) + "ms")
					print("  Opening the camera: " + str(round((timings[2] - timings[1]) * 1000)) + "ms")
					print("  Searching for known face: " + str(round((timings[3] - timings[2]) * 1000)) + "ms\n")

					print("Frames searched: " + str(frames))
					print("Certainty winning frame: " + str(round(match * 10, 3)))

					exposures = ["long", "medium", "short"]
					model_id = math.floor(float(match_index) / 3)

					print("Winning model: " + str(model_id) + " (\"" + models[model_id]["label"] + "\") using " + exposures[match_index % 3] + " exposure\n")

				# End peacegully
				stop(0)

	# Stop if we've exceded the maximum retry count
	if tries > int(config.get("video", "frame_count")):
		stop(11)

	tries += 1

# Compare incomming video with known faces
# Running in a local python instance to get around PATH issues

# Import required modules
import face_recognition
import cv2
import sys
import os
import json
import configparser

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
# List of known faces, encoded by face_recognition
encodings = []
# Amount of frames already matched
tries = 0

# Try to load the face model from the models folder
try:
	encodings = json.load(open(os.path.dirname(os.path.abspath(__file__)) + "/models/" + user + ".dat"))
except FileNotFoundError:
	sys.exit(10)

# Verify that we have a valid model file
if len(encodings) < 3:
	sys.exit(1)

# Start video capture on the IR camera
video_capture = cv2.VideoCapture(int(config.get("video", "device_id")))

while True:
	# Grab a single frame of video
	ret, frame = video_capture.read()

	# Get all faces from that frame as encodings
	face_encodings = face_recognition.face_encodings(frame)

	# Loop through each face
	for face_encoding in face_encodings:
		# Match this found face against a known face
		matches = face_recognition.face_distance(encodings, face_encoding)

		# Check if any match is certain enough to be the user we're looking for
		for match in matches:
			if match < int(config.get("video", "certainty")) and match > 0:
				stop(0)

	# Stop if we've exceded the maximum retry count
	if tries > int(config.get("video", "frame_count")):
		stop(11)

	tries += 1

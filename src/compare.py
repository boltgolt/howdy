# Compare incomming video with known faces
# Running in a local python instance to get around PATH issues

# Import time so we can start timing asap
import time

# Start timing
timings = [time.time()]

# Import required modules
import cv2
import sys
import os
import json
import math
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
# The model file contents
models = []
# Encoded face models
encodings = []
# Amount of ingnored dark frames
dark_tries = 0

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

# Add the time needed to start the script
timings.append(time.time())

# Start video capture on the IR camera
video_capture = cv2.VideoCapture(int(config.get("video", "device_id")))

# Force MJPEG decoding if true
if config.get("video", "force_mjpeg") == "true":
	# Set a magic number, will enable MJPEG but is badly documentated
	video_capture.set(cv2.CAP_PROP_FOURCC, 1196444237)

# Set the frame width and height if requested
if int(config.get("video", "frame_width")) != -1:
	video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, int(config.get("video", "frame_width")))

if int(config.get("video", "frame_height")) != -1:
	video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, int(config.get("video", "frame_height")))

# Capture a single frame so the camera becomes active
# This will let the camera adjust its light levels while we're importing for faster scanning
video_capture.read()

# Note the time it took to open the camera
timings.append(time.time())

# Import face recognition, takes some time
import face_recognition
timings.append(time.time())

# Fetch the max frame height
max_height = int(config.get("video", "max_height"))

# Start the read loop
frames = 0
while True:
	# Increment the frame count every loop
	frames += 1

	# Stop if we've exceded the time limit
	if time.time() - timings[3] > int(config.get("video", "timout")):
		stop(11)

	# Grab a single frame of video
	# Don't remove ret, it doesn't work without it
	ret, frame = video_capture.read()

	# Create a histogram of the image with 8 values
	hist = cv2.calcHist([frame], [0], None, [8], [0, 256])
	# All values combined for percentage calculation
	hist_total = int(sum(hist)[0])

	# If the image is fully black, skip to the next frame
	if hist_total == 0:
		dark_tries += 1
		continue

	# Scrip the frame if it exceeds the threshold
	if float(hist[0]) / hist_total * 100 > float(config.get("video", "dark_threshold")):
		dark_tries += 1
		continue

	# Get the height and with of the image
	height, width = frame.shape[:2]

	# If the hight is too high
	if max_height < height:
		# Calculate the amount the image has to shrink
		scaling_factor = max_height / float(height)
		# Apply that factor to the frame
		frame = cv2.resize(frame, None, fx=scaling_factor, fy=scaling_factor, interpolation=cv2.INTER_AREA)

	# Save the new size for diagnostics
	scale_height, scale_width = frame.shape[:2]

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
					def print_timing(label, offset):
						"""Helper function to print a timing from the list"""
						print("  " + label + ": " + str(round((timings[1 + offset] - timings[offset]) * 1000)) + "ms")

					print("Time spend")
					print_timing("Starting up", 0)
					print_timing("Opening the camera", 1)
					print_timing("Importing face_recognition", 2)
					print_timing("Searching for known face", 3)

					print("\nResolution")
					print("  Native: " + str(height) + "x" + str(width))
					print("  Used: " + str(scale_height) + "x" + str(scale_width))

					# Show the total number of frames and calculate the FPS by deviding it by the total scan time
					print("\nFrames searched: " + str(frames) + " (" + str(round(float(frames) / (timings[4] - timings[3]), 2)) + " fps)")
					print("Dark frames ignored: " + str(dark_tries))
					print("Certainty of winning frame: " + str(round(match * 10, 3)))

					# Catch older 3-encoding models
					if not match_index in models:
						match_index = 0

					print("Winning model: " + str(match_index) + " (\"" + models[match_index]["label"] + "\")")

				# End peacefully
				stop(0)

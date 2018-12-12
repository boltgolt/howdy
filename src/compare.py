# Compare incomming video with known faces
# Running in a local python instance to get around PATH issues

# Import time so we can start timing asap
import time

# Start timing
timings = {
	'st': time.time()
}

# Import required modules
import sys
import os
import json
import configparser
from threading import Thread
import cv2
import dlib
import numpy as np

# Get the absolute path to the current directory
PATH = os.path.abspath(__file__ + '/..')

# Read config from disk
config = configparser.ConfigParser()
config.read(PATH + "/config.ini")

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
	models = json.load(open(PATH + "/models/" + user + ".dat"))

	# Put all models together into 1 array
	for model in models:
		encodings += model["data"]
except FileNotFoundError:
	sys.exit(10)

# Check if the file contains a model
if not encodings:
	sys.exit(10)

# Add the time needed to start the script
timings['st'] = time.time() - timings['st']

timings['ic'] = time.time()

# Start video capture on the IR camera
video_capture = cv2.VideoCapture(config.get("video", "device_path"))

# Force MJPEG decoding if true
if config.getboolean("video", "force_mjpeg", fallback=False):
	# Set a magic number, will enable MJPEG but is badly documentated
	video_capture.set(cv2.CAP_PROP_FOURCC, 1196444237)

# Set the frame width and height if requested
fw = config.getint("video", "frame_width", fallback=-1)
fh = config.getint("video", "frame_height", fallback=-1)
if fw != -1:
	video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, fw)

if fh != -1:
	video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, fh)

# Capture a single frame so the camera becomes active
# This will let the camera adjust its light levels while we're importing for faster scanning
video_capture.grab()

# Note the time it took to open the camera
timings['ic'] = time.time() - timings['ic']

timings['ll'] = time.time()

face_detector = None
pose_predictor = None
face_encoder = None
use_cnn = config.getboolean('core', 'use_cnn', fallback=False)

def init_detector():
	global face_detector
	if use_cnn:
		face_detector = dlib.cnn_face_detection_model_v1(
			PATH + '/dlib-data/mmod_human_face_detector.dat'
		)
	else:
		face_detector = dlib.get_frontal_face_detector()

def init_predictor():
	global pose_predictor
	pose_predictor = dlib.shape_predictor(
		PATH + '/dlib-data/shape_predictor_5_face_landmarks.dat'
	)

def init_encoder():
	global face_encoder
	face_encoder = dlib.face_recognition_model_v1(
		PATH + '/dlib-data/dlib_face_recognition_resnet_model_v1.dat'
	)


init_thread1 = Thread(target=init_encoder)
init_thread2 = Thread(target=init_predictor)
init_thread3 = Thread(target=init_detector)
init_thread3.start()
init_thread1.start()
init_thread2.start()

init_thread3.join()
init_thread2.join()
init_thread1.join()
del init_thread1, init_thread2, init_thread3
timings['ll'] = time.time() - timings['ll']

# Fetch the max frame height
max_height = config.getfloat("video", "max_height", fallback=0.0)
# Get the height of the image
height = video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT) or 1

# Calculate the amount the image has to shrink
scaling_factor = (max_height / height) or 1

# Start the read loop
timings['fr'] = time.time()
frames = 0
timeout = config.getint("video", "timout")
dark_threshold = config.getfloat("video", "dark_threshold")
end_report = config.getboolean("debug", "end_report")
video_certainty = config.getfloat("video", "certainty") / 10
while True:
	# Increment the frame count every loop
	frames += 1

	# Stop if we've exceded the time limit
	if time.time() - timings['fr'] > timeout:
		stop(11)

	# Grab a single frame of video
	_, frame = video_capture.read()
	gsframe = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

	# Create a histogram of the image with 8 values
	hist = cv2.calcHist([gsframe], [0], None, [8], [0, 256])
	# All values combined for percentage calculation
	hist_total = np.sum(hist)

	# If the image is fully black or the frame exceeds threshold,
	# skip to the next frame
	if hist_total == 0 or (hist[0] / hist_total * 100 > dark_threshold):
		dark_tries += 1
		continue

	# If the hight is too high
	if scaling_factor != 1:
		# Apply that factor to the frame
		frame = cv2.resize(frame, None, fx=scaling_factor, fy=scaling_factor, interpolation=cv2.INTER_AREA)
		gsframe = cv2.resize(gsframe, None, fx=scaling_factor, fy=scaling_factor, interpolation=cv2.INTER_AREA)

	# Get all faces from that frame as encodings
	face_locations = face_detector(gsframe, 1) # upsample 1 time

	# Loop through each face
	for fl in face_locations:
		if use_cnn:
			fl = fl.rect

		face_landmark = pose_predictor(frame, fl)
		face_encoding = np.array(
			face_encoder.compute_face_descriptor(frame, face_landmark, 1) # num_jitters=1
		)
		# Match this found face against a known face
		matches = np.linalg.norm(encodings - face_encoding, axis=1)

		# Get best match
		match_index = np.argmin(matches)
		match = matches[match_index]

		# Check if a match that's confident enough
		if 0 < match < video_certainty:
			timings['fr'] = time.time() - timings['fr']

			# If set to true in the config, print debug text
			if end_report:
				def print_timing(label, k):
					"""Helper function to print a timing from the list"""
					print("  %s: %dms" % (label, round(timings[k] * 1000)))

				print("Time spent")
				print_timing("Starting up", 'st')
				print("  Open cam + load libs: %dms" % (round(max(timings['ll'], timings['ic']) * 1000, )))
				print_timing("  Opening the camera", 'ic')
				print_timing("  Importing recognition libs", 'll')
				print_timing("Searching for known face", 'fr')

				print("\nResolution")
				width = video_capture.get(cv2.CAP_PROP_FRAME_WIDTH) or 1
				print("  Native: %dx%d" % (height, width))
				# Save the new size for diagnostics
				scale_height, scale_width = frame.shape[:2]
				print("  Used: %dx%d" % (scale_height, scale_width))

				# Show the total number of frames and calculate the FPS by deviding it by the total scan time
				print("\nFrames searched: %d (%.2f fps)" % (frames, frames / timings['fr']))
				print("Dark frames ignored: %d " % (dark_tries, ))
				print("Certainty of winning frame: %.3f" % (match * 10, ))

				print("Winning model: %d (\"%s\")" % (match_index, models[match_index]["label"]))

			# End peacefully
			stop(0)

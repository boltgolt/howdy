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
import cv2
import dlib
import numpy as np
import _thread as thread


def init_detector(lock):
	global face_detector, pose_predictor, face_encoder
	if use_cnn:
		face_detector = dlib.cnn_face_detection_model_v1(
			PATH + '/dlib-data/mmod_human_face_detector.dat'
		)
	else:
		face_detector = dlib.get_frontal_face_detector()

	pose_predictor = dlib.shape_predictor(
		PATH + '/dlib-data/shape_predictor_5_face_landmarks.dat'
	)

	face_encoder = dlib.face_recognition_model_v1(
		PATH + '/dlib-data/dlib_face_recognition_resnet_model_v1.dat'
	)
	# Note the time it took to initialize detectors
	timings['ll'] = time.time() - timings['ll']
	lock.release()


def stop(status):
	"""Stop the execution and close video stream"""
	video_capture.release()
	sys.exit(status)


# Make sure we were given an username to tast against
if len(sys.argv) < 2:
	sys.exit(12)

# Get the absolute path to the current directory
PATH = os.path.abspath(__file__ + '/..')

# The username of the user being authenticated
user = sys.argv[1]
# The model file contents
models = []
# Encoded face models
encodings = []
# Amount of ingnored dark frames
dark_tries = 0
# Total amount of frames captured
frames = 0
# face recognition/detection instances
face_detector = None
pose_predictor = None
face_encoder = None

# Try to load the face model from the models folder
try:
	models = json.load(open(PATH + "/models/" + user + ".dat"))

	for model in models:
		encodings += model["data"]
except FileNotFoundError:
	sys.exit(10)

# Check if the file contains a model
if len(models) < 1:
	sys.exit(10)

# Read config from disk
config = configparser.ConfigParser()
config.read(PATH + "/config.ini")

# CNN usage flag
use_cnn = config.getboolean('core', 'use_cnn', fallback=False)
timeout = config.getint("video", "timout", fallback=5)
dark_threshold = config.getfloat("video", "dark_threshold", fallback=50.0)
video_certainty = config.getfloat("video", "certainty", fallback=3.5) / 10
end_report = config.getboolean("debug", "end_report", fallback=False)

# Save the time needed to start the script
timings['in'] = time.time() - timings['st']

# Import face recognition, takes some time
timings['ll'] = time.time()

lock = thread.allocate_lock()
lock.acquire()
thread.start_new_thread(init_detector, (lock, ))

# Start video capture on the IR camera
timings['ic'] = time.time()

# Check if the user explicitly set ffmpeg as recorder
if config.get("video", "recording_plugin") == "ffmpeg":
	from ffmpeg_reader import ffmpeg_reader

	# Set the capture source for ffmpeg
	video_capture = ffmpeg_reader(config.get("video", "device_path"), config.get("video", "device_format"))

else:
	# Start video capture on the IR camera through OpenCV
	video_capture = cv2.VideoCapture(config.get("video", "device_path"))

# Force MJPEG decoding if true
if config.getboolean("video", "force_mjpeg", fallback=False):
	# Set a magic number, will enable MJPEG but is badly documented
	video_capture.set(cv2.CAP_PROP_FOURCC, 1196444237) # 1196444237 is 'GPJM' in ASCII

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

# wait for thread to finish
lock.acquire()
lock.release()
del lock


# Fetch the max frame height
max_height = config.getfloat("video", "max_height", fallback=0.0)
# Get the height of the image
height = video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT) or 1

# Calculate the amount the image has to shrink
scaling_factor = (max_height / height) or 1

# Fetch config settings out of the loop
timeout = config.getint("video", "timeout")
dark_threshold = config.getfloat("video", "dark_threshold")
end_report = config.getboolean("debug", "end_report")

# Start the read loop
frames = 0
timings['fr'] = time.time()

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
			timings['tt'] = time.time() - timings['st']
			timings['fr'] = time.time() - timings['fr']

			# If set to true in the config, print debug text
			if end_report:
				def print_timing(label, k):
					"""Helper function to print a timing from the list"""
					print("  %s: %dms" % (label, round(timings[k] * 1000)))

				print("Time spent")
				print_timing("Starting up", 'in')
				print("  Open cam + load libs: %dms" % (round(max(timings['ll'], timings['ic']) * 1000, )))
				print_timing("  Opening the camera", 'ic')
				print_timing("  Importing recognition libs", 'll')
				print_timing("Searching for known face", 'fr')
				print_timing("Total time", 'tt')

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

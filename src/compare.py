# Compare incomming video with known faces
# Running in a local python instance to get around PATH issues

# Import time so we can start timing asap
import time

# Start timing
timings = {
	"st": time.time()
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
from recorders.video_capture import VideoCapture


def init_detector(lock):
	"""Start face detector, encoder and predictor in a new thread"""
	global face_detector, pose_predictor, face_encoder

	# Test if at lest 1 of the data files is there and abort if it's not
	if not os.path.isfile(PATH + "/dlib-data/shape_predictor_5_face_landmarks.dat"):
		print("Data files have not been downloaded, please run the following commands:")
		print("\n\tcd " + PATH + "/dlib-data")
		print("\tsudo ./install.sh\n")
		lock.release()
		sys.exit(1)

	# Use the CNN detector if enabled
	if use_cnn:
		face_detector = dlib.cnn_face_detection_model_v1(PATH + "/dlib-data/mmod_human_face_detector.dat")
	else:
		face_detector = dlib.get_frontal_face_detector()

	# Start the others regardless
	pose_predictor = dlib.shape_predictor(PATH + "/dlib-data/shape_predictor_5_face_landmarks.dat")
	face_encoder = dlib.face_recognition_model_v1(PATH + "/dlib-data/dlib_face_recognition_resnet_model_v1.dat")

	# Note the time it took to initialize detectors
	timings["ll"] = time.time() - timings["ll"]
	lock.release()

# Make sure we were given an username to tast against
if len(sys.argv) < 2:
	sys.exit(12)

# Get the absolute path to the current directory
PATH = os.path.abspath(__file__ + "/..")

# The username of the user being authenticated
user = sys.argv[1]
# The model file contents
models = []
# Encoded face models
encodings = []
# Amount of ignored 100% black frames
black_tries = 0
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

# Get all config values needed
use_cnn = config.getboolean("core", "use_cnn", fallback=False)
timeout = config.getint("video", "timeout", fallback=5)
dark_threshold = config.getfloat("video", "dark_threshold", fallback=50.0)
video_certainty = config.getfloat("video", "certainty", fallback=3.5) / 10
end_report = config.getboolean("debug", "end_report", fallback=False)

# Save the time needed to start the script
timings["in"] = time.time() - timings["st"]

# Import face recognition, takes some time
timings["ll"] = time.time()

# Start threading and wait for init to finish
lock = thread.allocate_lock()
lock.acquire()
thread.start_new_thread(init_detector, (lock, ))

# Start video capture on the IR camera
timings["ic"] = time.time()

video_capture = VideoCapture(config)

# Read exposure from config to use in the main loop
exposure = config.getint("video", "exposure", fallback=-1)

# Note the time it took to open the camera
timings["ic"] = time.time() - timings["ic"]

# wait for thread to finish
lock.acquire()
lock.release()
del lock

# Fetch the max frame height
max_height = config.getfloat("video", "max_height", fallback=0.0)
# Get the height of the image
height = video_capture.internal.get(cv2.CAP_PROP_FRAME_HEIGHT) or 1

# Calculate the amount the image has to shrink
scaling_factor = (max_height / height) or 1

# Fetch config settings out of the loop
timeout = config.getint("video", "timeout")
dark_threshold = config.getfloat("video", "dark_threshold")
end_report = config.getboolean("debug", "end_report")

# Start the read loop
frames = 0
valid_frames = 0
timings["fr"] = time.time()
dark_running_total = 0

clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

while True:
	# Increment the frame count every loop
	frames += 1

	# Stop if we've exceded the time limit
	if time.time() - timings["fr"] > timeout:
		if (dark_tries == valid_frames ):
			print("All frames were too dark, please check dark_threshold in config")
			print("Average darkness: " + str(dark_running_total / valid_frames) + ", Threshold: " + str(dark_threshold))
      sys.exit(13)
		else:
      sys.exit(11)

	# Grab a single frame of video
	frame, gsframe = video_capture.read_frame()

	gsframe = clahe.apply(gsframe)	

	# Create a histogram of the image with 8 values
	hist = cv2.calcHist([gsframe], [0], None, [8], [0, 256])
	# All values combined for percentage calculation
	hist_total = np.sum(hist)

	# Calculate frame darkness
	darkness = (hist[0] / hist_total * 100)

	# If the image is fully black due to a bad camera read,
	# skip to the next frame
	if (hist_total == 0) or (darkness == 100):
		black_tries += 1
		continue

	dark_running_total += darkness
	valid_frames += 1
	# If the image exceeds darkness threshold due to subject distance,
	# skip to the next frame
	if (darkness > dark_threshold):
		dark_tries += 1
		continue

	# If the hight is too high
	if scaling_factor != 1:
		# Apply that factor to the frame
		frame = cv2.resize(frame, None, fx=scaling_factor, fy=scaling_factor, interpolation=cv2.INTER_AREA)
		gsframe = cv2.resize(gsframe, None, fx=scaling_factor, fy=scaling_factor, interpolation=cv2.INTER_AREA)

	# Get all faces from that frame as encodings
	# Upsamples 1 time
	face_locations = face_detector(gsframe, 1)

	# Loop through each face
	for fl in face_locations:
		if use_cnn:
			fl = fl.rect

		# Fetch the faces in the image
		face_landmark = pose_predictor(frame, fl)
		face_encoding = np.array(face_encoder.compute_face_descriptor(frame, face_landmark, 1))

		# Match this found face against a known face
		matches = np.linalg.norm(encodings - face_encoding, axis=1)

		# Get best match
		match_index = np.argmin(matches)
		match = matches[match_index]

		# Check if a match that's confident enough
		if 0 < match < video_certainty:
			timings["tt"] = time.time() - timings["st"]
			timings["fr"] = time.time() - timings["fr"]

			# If set to true in the config, print debug text
			if end_report:
				def print_timing(label, k):
					"""Helper function to print a timing from the list"""
					print("  %s: %dms" % (label, round(timings[k] * 1000)))

				# Print a nice timing report
				print("Time spent")
				print_timing("Starting up", "in")
				print("  Open cam + load libs: %dms" % (round(max(timings["ll"], timings["ic"]) * 1000, )))
				print_timing("  Opening the camera", "ic")
				print_timing("  Importing recognition libs", "ll")
				print_timing("Searching for known face", "fr")
				print_timing("Total time", "tt")

				print("\nResolution")
				width = video_capture.fw or 1
				print("  Native: %dx%d" % (height, width))
				# Save the new size for diagnostics
				scale_height, scale_width = frame.shape[:2]
				print("  Used: %dx%d" % (scale_height, scale_width))

				# Show the total number of frames and calculate the FPS by deviding it by the total scan time
				print("\nFrames searched: %d (%.2f fps)" % (frames, frames / timings["fr"]))
				print("Black frames ignored: %d " % (black_tries, ))
				print("Dark frames ignored: %d " % (dark_tries, ))
				print("Certainty of winning frame: %.3f" % (match * 10, ))

				print("Winning model: %d (\"%s\")" % (match_index, models[match_index]["label"]))

			# End peacefully
			sys.exit(0)

	if exposure != -1:
		# For a strange reason on some cameras (e.g. Lenoxo X1E)
		# setting manual exposure works only after a couple frames
		# are captured and even after a delay it does not
		# always work. Setting exposure at every frame is
		# reliable though.
		video_capture.intenal.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1.0)  # 1 = Manual
		video_capture.intenal.set(cv2.CAP_PROP_EXPOSURE, float(exposure))

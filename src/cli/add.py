# Save the face of the user in encoded form

# Import required modules
import time
import os
import sys
import json
import configparser
import builtins
import cv2
import numpy as np

# Try to import dlib and give a nice error if we can't
# Add should be the first point where import issues show up
try:
	import dlib
except ImportError as err:
	print(err)

	print("\nCan't import the dlib module, check the output of")
	print("pip3 show dlib")
	sys.exit(1)

# Get the absolute path to the current directory
path = os.path.abspath(__file__ + "/..")

# Test if at lest 1 of the data files is there and abort if it's not
if not os.path.isfile(path + "/../dlib-data/shape_predictor_5_face_landmarks.dat"):
	print("Data files have not been downloaded, please run the following commands:")
	print("\n\tcd " + os.path.realpath(path + "/../dlib-data"))
	print("\tsudo ./install.sh\n")
	sys.exit(1)

# Read config from disk
config = configparser.ConfigParser()
config.read(path + "/../config.ini")

if not os.path.exists(config.get("video", "device_path")):
	print("Camera path is not configured correctly, please edit the 'device_path' config value.")
	sys.exit(1)

use_cnn = config.getboolean("core", "use_cnn", fallback=False)
if use_cnn:
	face_detector = dlib.cnn_face_detection_model_v1(path + "/../dlib-data/mmod_human_face_detector.dat")
else:
	face_detector = dlib.get_frontal_face_detector()

pose_predictor = dlib.shape_predictor(path + "/../dlib-data/shape_predictor_5_face_landmarks.dat")
face_encoder = dlib.face_recognition_model_v1(path + "/../dlib-data/dlib_face_recognition_resnet_model_v1.dat")

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
	print("NOTICE: Each additional model slows down the face recognition engine slightly")
	print("Press Ctrl+C to cancel\n")

print("Adding face model for the user " + user)

# Set the default label
label = "Initial model"

# If models already exist, set that default label
if encodings:
	label = "Model #" + str(len(encodings) + 1)

# Keep de default name if we can't ask questions
if builtins.howdy_args.y:
	print('Using default label "%s" because of -y flag' % (label, ))
else:
	# Ask the user for a custom label
	label_in = input("Enter a label for this new model [" + label + "] (max 24 characters): ")

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

# Check if the user explicitly set ffmpeg as recorder
if config.get("video", "recording_plugin") == "ffmpeg":
	# Set the capture source for ffmpeg
	from recorders.ffmpeg_reader import ffmpeg_reader
	video_capture = ffmpeg_reader(config.get("video", "device_path"), config.get("video", "device_format"))
elif config.get("video", "recording_plugin") == "pyv4l2":
	# Set the capture source for pyv4l2
	from recorders.pyv4l2_reader import pyv4l2_reader
	video_capture = pyv4l2_reader(config.get("video", "device_path"), config.get("video", "device_format"))
else:
	# Start video capture on the IR camera through OpenCV
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

# Request a frame to wake the camera up
video_capture.grab()

print("\nPlease look straight into the camera")

# Give the user time to read
time.sleep(2)

# Will contain found face encodings
enc = []
# Count the amount or read frames
frames = 0
dark_threshold = config.getfloat("video", "dark_threshold")

clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

# Loop through frames till we hit a timeout
while frames < 60:
	# Grab a single frame of video
	# Don't remove ret, it doesn't work without it
	ret, frame = video_capture.read()
	gsframe = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gsframe = clahe.apply(gsframe)

	# Create a histogram of the image with 8 values
	hist = cv2.calcHist([gsframe], [0], None, [8], [0, 256])
	# All values combined for percentage calculation
	hist_total = np.sum(hist)

	# If the image is fully black or the frame exceeds threshold,
	# skip to the next frame
	if hist_total == 0 or (hist[0] / hist_total * 100 > dark_threshold):
		continue

	frames += 1

	# Get all faces from that frame as encodings
	face_locations = face_detector(gsframe, 1)

	# If we've found at least one, we can continue
	if face_locations:
		break

video_capture.release()

# If more than 1 faces are detected we can't know wich one belongs to the user
if len(face_locations) > 1:
	print("Multiple faces detected, aborting")
	sys.exit(1)
elif not face_locations:
	print("No face detected, aborting")
	sys.exit(1)

face_location = face_locations[0]
if use_cnn:
	face_location = face_location.rect

# Get the encodings in the frame
face_landmark = pose_predictor(frame, face_location)
face_encoding = np.array(face_encoder.compute_face_descriptor(frame, face_landmark, 1))

insert_model["data"].append(face_encoding.tolist())

# Insert full object into the list
encodings.append(insert_model)

# Save the new encodings to disk
with open(enc_file, "w") as datafile:
	json.dump(encodings, datafile)

# Give let the user know how it went
print("""Scan complete

Added a new model to """ + user)

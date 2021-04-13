# Save the face of the user in encoded form

import builtins
import configparser
import json
import os
import sys
# Import required modules
import time

import numpy as np

from recorders.video_capture import VideoCapture

# Try to import dlib and give a nice error if we can't
# Add should be the first point where import issues show up
try:
    import dlib
except ImportError as err:
    print(err)

    print("\nCan't import the dlib module, check the output of")
    print("pip3 show dlib")
    sys.exit(1)

# OpenCV needs to be imported after dlib
import cv2

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
    print('Using default label "%s" because of -y flag' % (label,))
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

# Set up video_capture
video_capture = VideoCapture(config)

print("\nPlease look straight into the camera")

# Give the user time to read
time.sleep(2)

# Will contain found face encodings
enc = []
# Count the number of read frames
frames = 0
# Count the number of illuminated read frames
valid_frames = 0
# Count the number of illuminated frames that
# were rejected for being too dark
dark_tries = 0
# Track the running darkness total
dark_running_total = 0
face_locations = None

dark_threshold = config.getfloat("video", "dark_threshold")

clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

# Loop through frames till we hit a timeout
while frames < 60:
    frames += 1
    # Grab a single frame of video
    frame, gsframe = video_capture.read_frame()
    gsframe = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
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
        continue

    # Include this frame in calculating our average session brightness
    dark_running_total += darkness
    valid_frames += 1

    # If the image exceeds darkness threshold due to subject distance,
    # skip to the next frame
    if (darkness > dark_threshold):
        dark_tries += 1
        continue

    # Get all faces from that frame as encodings
    face_locations = face_detector(gsframe, 1)

    # If we've found at least one, we can continue
    if face_locations:
        break

video_capture.release()

# If we've found no faces, try to determine why
if face_locations is None or not face_locations:
    if valid_frames == 0:
        print("Camera saw only black frames - is IR emitter working?")
    elif valid_frames == dark_tries:
        print("All frames were too dark, please check dark_threshold in config")
        print("Average darkness: " + str(dark_running_total / valid_frames) + ", Threshold: " + str(dark_threshold))
    else:
        print("No face detected, aborting")
    sys.exit(1)

# If more than 1 faces are detected we can't know wich one belongs to the user
elif len(face_locations) > 1:
    print("Multiple faces detected, aborting")
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
    json.dump(encodings, datafile, indent=2)

# Give let the user know how it went
print("""Scan complete

Added a new model to """ + user)

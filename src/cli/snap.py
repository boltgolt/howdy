# Create a snapshot

import configparser
import datetime
# Import required modules
import os

import snapshot
from recorders.video_capture import VideoCapture

# Get the absolute path to the current directory
path = os.path.abspath(__file__ + "/..")

# Read the config
config = configparser.ConfigParser()
config.read(path + "/../config.ini")

# Start video capture
video_capture = VideoCapture(config)

# Read a frame to activate emitters
video_capture.read_frame()

# Read exposure and dark_thresholds from config to use in the main loop
exposure = config.getint("video", "exposure", fallback=-1)
dark_threshold = config.getfloat("video", "dark_threshold")

# COllection of recorded frames
frames = []

while True:
    # Grab a single frame of video
    frame, gsframe = video_capture.read_frame()

    # Add the frame to the list
    frames.append(frame)

    # Stop the loop if we have 4 frames
    if len(frames) >= 4:
        break

# Generate a snapshot image from the frames
file = snapshot.generate(frames, [
    "GENERATED SNAPSHOT",
    "Date: " + datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S UTC"),
    "Dark threshold config: " + str(config.getfloat("video", "dark_threshold", fallback=50.0)),
    "Certainty config: " + str(config.getfloat("video", "certainty", fallback=3.5))
])

# Show the file location in console
print("Generated snapshot saved as")
print(file)

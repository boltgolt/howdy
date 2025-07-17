# Create a snapshot

# Import required modules
import os
import configparser
from datetime import timezone, datetime
import snapshot
import paths_factory
from recorders.video_capture import VideoCapture

from i18n import _

# Read the config
config = configparser.ConfigParser()
config.read(paths_factory.config_file_path())

# Start video capture
video_capture = VideoCapture(config)

# Read a frame to activate emitters
video_capture.read_frame()

# Read exposure and dark_thresholds from config to use in the main loop
exposure = config.getint("video", "exposure", fallback=-1)
dark_threshold = config.getfloat("video", "dark_threshold", fallback=60)

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
	_("GENERATED SNAPSHOT"),
	_("Date: ") + datetime.now(timezone.utc).strftime("%Y/%m/%d %H:%M:%S UTC"),
	_("Dark threshold config: ") + str(config.getfloat("video", "dark_threshold", fallback=60.0)),
	_("Certainty config: ") + str(config.getfloat("video", "certainty", fallback=3.5))
])

# Show the file location in console
print(_("Generated snapshot saved as"))
print(file)

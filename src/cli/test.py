# Show a window with the video stream and testing information

# Import required modules
import configparser
import os
import sys
import time
import cv2
import dlib

# Get the absolute path to the current file
path = os.path.dirname(os.path.abspath(__file__))

# Read config from disk
config = configparser.ConfigParser()
config.read(path + "/../config.ini")

if config.get("video", "recording_plugin") != "opencv":
	print("Howdy has been configured to use a recorder which doesn't support the test command yet")
	print("Aborting")
	sys.exit(12)

# Start capturing from the configured webcam
video_capture = cv2.VideoCapture(config.get("video", "device_path"), cv2.CAP_V4L)

# Force MJPEG decoding if true
if config.getboolean("video", "force_mjpeg", fallback=False):
	# Set a magic number, will enable MJPEG but is badly documented
	video_capture.set(cv2.CAP_PROP_FOURCC, 1196444237)

# Set the frame width and height if requested
fw = config.getint("video", "frame_width", fallback=-1)
fh = config.getint("video", "frame_height", fallback=-1)
if fw != -1:
	video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, fw)

if fh != -1:
	video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, fh)

# Read exposure and dark_thresholds from config to use in the main loop
exposure = config.getint("video", "exposure", fallback=-1)
dark_threshold = config.getfloat("video", "dark_threshold")

# Let the user know what's up
print("""
Opening a window with a test feed

Press ctrl+C in this terminal to quit
Click on the image to enable or disable slow mode
""")


def mouse(event, x, y, flags, param):
	"""Handle mouse events"""
	global slow_mode

	# Toggle slowmode on click
	if event == cv2.EVENT_LBUTTONDOWN:
		slow_mode = not slow_mode


def print_text(line_number, text):
	"""Print the status text by line number"""
	cv2.putText(overlay, text, (10, height - 10 - (10 * line_number)), cv2.FONT_HERSHEY_SIMPLEX, .3, (0, 255, 0), 0, cv2.LINE_AA)

use_cnn = config.getboolean('core', 'use_cnn', fallback=False)
if use_cnn:
	face_detector = dlib.cnn_face_detection_model_v1(
		path + '/../dlib-data/mmod_human_face_detector.dat'
	)
else:
	face_detector = dlib.get_frontal_face_detector()

clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

# Open the window and attach a a mouse listener
cv2.namedWindow("Howdy Test")
cv2.setMouseCallback("Howdy Test", mouse)

# Enable a delay in the loop
slow_mode = False
# Count all frames ever
total_frames = 0
# Count all frames per second
sec_frames = 0
# Last secands FPS
fps = 0
# The current second we're counting
sec = int(time.time())
# recognition time
rec_tm = 0

# Wrap everything in an keyboard interupt handler
try:
	while True:
		frame_tm = time.time()

		# Increment the frames
		total_frames += 1
		sec_frames += 1

		# Id we've entered a new second
		if sec != int(frame_tm):
			# Set the last seconds FPS
			fps = sec_frames

			# Set the new second and reset the counter
			sec = int(frame_tm)
			sec_frames = 0

		# Grab a single frame of video
		ret, frame = video_capture.read()

		try:
			# Convert from color to grayscale
			# First processing of frame, so frame errors show up here
			frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		except RuntimeError:
			pass
		except cv2.error:
			print("\nUnknown camera, please check your 'device_path' config value.\n")
			raise

		frame = clahe.apply(frame)
		# Make a frame to put overlays in
		overlay = frame.copy()

		# Fetch the frame height and width
		height, width = frame.shape[:2]

		# Create a histogram of the image with 8 values
		hist = cv2.calcHist([frame], [0], None, [8], [0, 256])
		# All values combined for percentage calculation
		hist_total = int(sum(hist)[0])
		# Fill with the overal containing percentage
		hist_perc = []

		# Loop though all values to calculate a percentage and add it to the overlay
		for index, value in enumerate(hist):
			value_perc = float(value[0]) / hist_total * 100
			hist_perc.append(value_perc)

			# Top left pont, 10px margins
			p1 = (20 + (10 * index), 10)
			# Bottom right point makes the bar 10px thick, with an height of half the percentage
			p2 = (10 + (10 * index), int(value_perc / 2 + 10))
			# Draw the bar in green
			cv2.rectangle(overlay, p1, p2, (0, 200, 0), thickness=cv2.FILLED)

		# Print the statis in the bottom left
		print_text(0, "RESOLUTION: %dx%d" % (height, width))
		print_text(1, "FPS: %d" % (fps, ))
		print_text(2, "FRAMES: %d" % (total_frames, ))
		print_text(3, "RECOGNITION: %dms" % (round(rec_tm * 1000), ))

		# Show that slow mode is on, if it's on
		if slow_mode:
			cv2.putText(overlay, "SLOW MODE", (width - 66, height - 10), cv2.FONT_HERSHEY_SIMPLEX, .3, (0, 0, 255), 0, cv2.LINE_AA)

		# Ignore dark frames
		if hist_perc[0] > dark_threshold:
			# Show that this is an ignored frame in the top right
			cv2.putText(overlay, "DARK FRAME", (width - 68, 16), cv2.FONT_HERSHEY_SIMPLEX, .3, (0, 0, 255), 0, cv2.LINE_AA)
		else:
			# SHow that this is an active frame
			cv2.putText(overlay, "SCAN FRAME", (width - 68, 16), cv2.FONT_HERSHEY_SIMPLEX, .3, (0, 255, 0), 0, cv2.LINE_AA)

			rec_tm = time.time()
			# Get the locations of all faces and their locations
			# Upsample it once
			face_locations = face_detector(frame, 1)
			rec_tm = time.time() - rec_tm

			# Loop though all faces and paint a circle around them
			for loc in face_locations:
				if use_cnn:
					loc = loc.rect

				# Get the center X and Y from the rectangular points
				x = int((loc.right() - loc.left()) / 2) + loc.left()
				y = int((loc.bottom() - loc.top()) / 2) + loc.top()

				# Get the raduis from the with of the square
				r = (loc.right() - loc.left()) / 2
				# Add 20% padding
				r = int(r + (r * 0.2))

				# Draw the Circle in green
				cv2.circle(overlay, (x, y), r, (0, 0, 230), 2)

		# Add the overlay to the frame with some transparency
		alpha = 0.65
		cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

		# Show the image in a window
		cv2.imshow("Howdy Test", frame)

		# Quit on any keypress
		if cv2.waitKey(1) != -1:
			raise KeyboardInterrupt()

		frame_time = time.time() - frame_tm

		# Delay the frame if slowmode is on
		if slow_mode:
			time.sleep(.5 - frame_time)

		if exposure != -1:
			# For a strange reason on some cameras (e.g. Lenoxo X1E)
			# setting manual exposure works only after a couple frames
			# are captured and even after a delay it does not
			# always work. Setting exposure at every frame is
			# reliable though.
			video_capture.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1.0)  # 1 = Manual
			video_capture.set(cv2.CAP_PROP_EXPOSURE, float(exposure))

# On ctrl+C
except KeyboardInterrupt:
	# Let the user know we're stopping
	print("\nClosing window")

	# Release handle to the webcam
	video_capture.release()
	cv2.destroyAllWindows()

# Top level class for a video capture providing simplified API's for common
# functions

# Import required modules
import configparser
import cv2
import os
import sys


# Class to provide boilerplate code to build a video recorder with the
# correct settings from the config file.
#
# The internal recorder can be accessed with 'video_capture.internal'


class VideoCapture:
	def __init__(self, config):
		"""
		Creates a new VideoCapture instance depending on the settings in the
		provided config file.

		Config can either be a string to the path, or a pre-setup configparser.
		"""

		# Parse config from string if nedded
		if isinstance(config, str):
			self.config = configparser.ConfigParser()
			self.config.read(config)
		else:
			self.config = config

		# Check device path
		if not os.path.exists(self.config.get("video", "device_path")):
			print("Camera path is not configured correctly, please edit the 'device_path' config value.")
			sys.exit(1)

		# Create reader
		# The internal video recorder
		self.internal = None
		# The frame width
		self.fw = None
		# The frame height
		self.fh = None
		self._create_reader()

		# Request a frame to wake the camera up
		self.internal.grab()

	def __del__(self):
		"""
		Frees resources when destroyed
		"""
		if self is not None:
			self.internal.release()

	def release(self):
		"""
		Release cameras
		"""
		if self is not None:
			self.internal.release()

	def read_frame(self):
		"""
		Reads a frame, returns the frame and an attempted grayscale conversion of
		the frame in a tuple:

		(frame, grayscale_frame)

		If the grayscale conversion fails, both items in the tuple are identical.
		"""

		# Grab a single frame of video
		# Don't remove ret, it doesn't work without it
		ret, frame = self.internal.read()
		if not ret:
			print("Failed to read camera specified in your 'device_path', aborting")
			sys.exit(1)

		try:
			# Convert from color to grayscale
			# First processing of frame, so frame errors show up here
			gsframe = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		except RuntimeError:
			gsframe = frame
		except cv2.error:
			print("\nAn error occurred in OpenCV\n")
			raise
		return frame, gsframe

	def _create_reader(self):
		"""
		Sets up the video reader instance
		"""

		if self.config.get("video", "recording_plugin") == "ffmpeg":
			# Set the capture source for ffmpeg
			from recorders.ffmpeg_reader import ffmpeg_reader
			self.internal = ffmpeg_reader(
				self.config.get("video", "device_path"),
				self.config.get("video", "device_format")
			)

		elif self.config.get("video", "recording_plugin") == "pyv4l2":
			# Set the capture source for pyv4l2
			from recorders.pyv4l2_reader import pyv4l2_reader
			self.internal = pyv4l2_reader(
				self.config.get("video", "device_path"),
				self.config.get("video", "device_format")
			)

		else:
			# Start video capture on the IR camera through OpenCV
			self.internal = cv2.VideoCapture(
				self.config.get("video", "device_path")
			)

		# Force MJPEG decoding if true
		if self.config.getboolean("video", "force_mjpeg", fallback=False):
			# Set a magic number, will enable MJPEG but is badly documentated
			self.internal.set(cv2.CAP_PROP_FOURCC, 1196444237)

		# Set the frame width and height if requested
		self.fw = self.config.getint("video", "frame_width", fallback=-1)
		self.fh = self.config.getint("video", "frame_height", fallback=-1)
		if self.fw != -1:
			self.internal.set(cv2.CAP_PROP_FRAME_WIDTH, self.fw)
		if self.fh != -1:
			self.internal.set(cv2.CAP_PROP_FRAME_HEIGHT, self.fh)

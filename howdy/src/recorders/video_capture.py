# Top level class for a video capture providing simplified API's for common
# functions

# Import required modules
import configparser
import cv2
import numpy as np
import os
import sys

from i18n import _

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

		# Parse config from string if needed
		if isinstance(config, str):
			self.config = configparser.ConfigParser()
			self.config.read(config)
		else:
			self.config = config

		# Check device path
		if not os.path.exists(self.config.get("video", "device_path")):
			if self.config.getboolean("video", "warn_no_device", fallback=True):
				print(_("Howdy could not find a camera device at the path specified in the config file."))
				print(_("It is very likely that the path is not configured correctly, please edit the 'device_path' config value by running:"))
				print("\n\tsudo howdy config\n")
			sys.exit(14)

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
			try:
				self.internal.release()
			except AttributeError as err:
				pass

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
			print(_("Failed to read camera specified in the 'device_path' config option, aborting"))
			sys.exit(14)

		# Single channel frames come from grayscale or raw formats, see the
		# pixel_format option. Deeper than 8 bits gets scaled down first.
		if frame.ndim == 2:
			if frame.dtype != np.uint8:
				frame = self._scale_raw(frame)
			return cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR), frame

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

	def _scale_raw(self, frame):
		"""
		Scales a raw 10 to 16 bit grayscale frame down to 8 bits. The black
		level is removed and the brightest 0.5% of pixels are clipped, so a
		dim IR image still uses the full range.
		"""
		black = self.config.getint("video", "raw_black_level", fallback=0)
		f = np.clip(frame.astype(np.float32) - black, 0, None)
		top = max(float(np.percentile(f, 99.5)), 1.0)
		return np.clip(f * (255.0 / top), 0, 255).astype(np.uint8)

	def _create_reader(self):
		"""
		Sets up the video reader instance
		"""
		recording_plugin = self.config.get("video", "recording_plugin", fallback="opencv")

		if recording_plugin == "ffmpeg":
			# Set the capture source for ffmpeg
			from recorders.ffmpeg_reader import ffmpeg_reader
			self.internal = ffmpeg_reader(
				self.config.get("video", "device_path"),
				self.config.get("video", "device_format", fallback="v4l2")
			)

		elif recording_plugin == "pyv4l2":
			# Set the capture source for pyv4l2
			from recorders.pyv4l2_reader import pyv4l2_reader
			self.internal = pyv4l2_reader(
				self.config.get("video", "device_path"),
				self.config.get("video", "device_format", fallback="v4l2")
			)

		else:
			# Start video capture on the IR camera through OpenCV
			self.internal = cv2.VideoCapture(
				self.config.get("video", "device_path"),
				cv2.CAP_V4L
			)
			# Set the capture frame rate
			# Without this the first detected (and possibly lower) frame rate is used, -1 seems to select the highest
			# Use 0 as a fallback to avoid breaking an existing setup, new installs should default to -1
			self.fps = self.config.getint("video", "device_fps", fallback=0)
			if self.fps != 0:
				self.internal.set(cv2.CAP_PROP_FPS, self.fps)

		# Force MJPEG decoding if true
		if self.config.getboolean("video", "force_mjpeg", fallback=False):
			# Set a magic number, will enable MJPEG but is badly documentated
			self.internal.set(cv2.CAP_PROP_FOURCC, 1196444237)

		# Request a specific pixel format, for IR sensors that only offer raw
		# formats OpenCV does not choose on its own (Y10 for example)
		pixel_format = self.config.get("video", "pixel_format", fallback="").strip()
		if pixel_format:
			self.internal.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*pixel_format.ljust(4)[:4]))
			# Keep the raw samples, read_frame() scales them down itself
			self.internal.set(cv2.CAP_PROP_CONVERT_RGB, 0)

		# Set the frame width and height if requested
		self.fw = self.config.getint("video", "frame_width", fallback=-1)
		self.fh = self.config.getint("video", "frame_height", fallback=-1)
		if self.fw != -1:
			self.internal.set(cv2.CAP_PROP_FRAME_WIDTH, self.fw)
		if self.fh != -1:
			self.internal.set(cv2.CAP_PROP_FRAME_HEIGHT, self.fh)

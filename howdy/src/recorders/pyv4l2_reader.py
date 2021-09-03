# Class that simulates the functionality of opencv so howdy can use v4l2 devices seamlessly

# Import required modules. lib4l-dev package is also required.
import fcntl
import numpy
import sys

from recorders import v4l2
from cv2 import cvtColor, COLOR_GRAY2BGR, CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT
from i18n import _

try:
	from pyv4l2.frame import Frame
except ImportError:
	print(_("Missing pyv4l2 module, please run:"))
	print(" pip3 install pyv4l2\n")
	sys.exit(13)


class pyv4l2_reader:
	""" This class was created to look as similar to the openCV features used in Howdy as possible for overall code cleanliness. """

	# Init
	def __init__(self, device_name, device_format):
		self.device_name = device_name
		self.device_format = device_format
		self.height = 0
		self.width = 0
		self.probe()
		self.frame = ""

	def set(self, prop, setting):
		""" Setter method for height and width """
		if prop == CAP_PROP_FRAME_WIDTH:
			self.width = setting
		elif prop == CAP_PROP_FRAME_HEIGHT:
			self.height = setting

	def get(self, prop):
		""" Getter method for height and width """
		if prop == CAP_PROP_FRAME_WIDTH:
			return self.width
		elif prop == CAP_PROP_FRAME_HEIGHT:
			return self.height

	def probe(self):
		""" Probe the video device to get height and width info """

		vd = open(self.device_name, 'r')
		fmt = v4l2.v4l2_format()
		fmt.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
		ret = fcntl.ioctl(vd, v4l2.VIDIOC_G_FMT, fmt)
		vd.close()
		if ret == 0:
			height = fmt.fmt.pix.height
			width = fmt.fmt.pix.width
		else:
			# Could not determine the resolution from ioctl call. Reverting to slower ffmpeg.probe() method
			import ffmpeg
			probe = ffmpeg.probe(self.device_name)
			height = int(probe['streams'][0]['height'])
			width = int(probe['streams'][0]['width'])

		if self.get(CAP_PROP_FRAME_HEIGHT) == 0:
			self.set(CAP_PROP_FRAME_HEIGHT, int(height))

		if self.get(CAP_PROP_FRAME_WIDTH) == 0:
			self.set(CAP_PROP_FRAME_WIDTH, int(width))

	def record(self):
		""" Start recording """
		self.frame = Frame(self.device_name)

	def grab(self):
		""" Read a sigle frame from the IR camera. """
		self.read()

	def read(self):
		""" Read a sigle frame from the IR camera. """

		if not self.frame:
			self.record()

		# Grab a raw frame from the camera
		frame_data = self.frame.get_frame()

		# Convert the raw frame_date to a numpy array
		img = (numpy.frombuffer(frame_data, numpy.uint8))

		# Convert the numpy array to a proper grayscale image array
		img_bgr = cvtColor(img, COLOR_GRAY2BGR)

		# Convert the grayscale image array into a proper RGB style numpy array
		img2 = (numpy.frombuffer(img_bgr, numpy.uint8).reshape([352, 352, 3]))

		# Return a single frame of video
		return 0, img2

	def release(self):
		""" Empty our array. If we had a hold on the camera, we would give it back here. """
		self.video = ()
		self.num_frames_read = 0
		if self.frame:
			self.frame.close()

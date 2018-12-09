import ffmpeg
import numpy
from cv2 import CAP_PROP_FRAME_WIDTH
from cv2 import CAP_PROP_FRAME_HEIGHT
from cv2 import CAP_PROP_FOURCC
import sys

class ffmpeg_reader:
	""" This class was created to look as similar to the openCV features used in Howdy as possible for overall code cleanliness. """

	# Init
	def __init__(self, device_name, device_format, numframes):
		self.device_name = device_name
		self.device_format = device_format
		self.numframes = numframes
		self.video = ()
		self.num_frames_read = 0
		self.height = 0
		self.width = 0
		self.init_camera = True
		self.force_jpeg = 0

	def set(self, prop, setting):
		""" Setter method for height and width """
		if prop == CAP_PROP_FRAME_WIDTH:
			self.width = setting
		elif prop == CAP_PROP_FRAME_HEIGHT:
			self.height = setting
		elif prop == CAP_PROP_FOURCC:
			self.force_jpeg = setting


	def get(self, prop):
		""" Getter method for height and width """
		if prop == CAP_PROP_FRAME_WIDTH:
			return self.width
		elif prop == CAP_PROP_FRAME_HEIGHT:
			return self.height
		elif prop == CAP_PROP_FOURCC:
			return self.force_jpeg
			
	def probe(self):
		""" Probe the video device to get height and width info """
		probe = ffmpeg.probe(self.device_name)

		if self.get(CAP_PROP_FRAME_WIDTH) == 0 or self.get(CAP_PROP_FRAME_WIDTH) > int(probe['streams'][0]['width']):
			self.set(CAP_PROP_FRAME_WIDTH, probe['streams'][0]['width'])
		if self.get(CAP_PROP_FRAME_HEIGHT) == 0  or self.get(CAP_PROP_FRAME_HEIGHT) > int(probe['streams'][0]['height']):
			self.set(CAP_PROP_FRAME_HEIGHT, probe['streams'][0]['height'])

	def record(self, numframes):
		""" Record a video, saving it to self.video array for processing later """

		# Eensure we have set our width and height before we record, otherwise our numpy call will fail
		if self.get(CAP_PROP_FRAME_WIDTH) == 0 or self.get(CAP_PROP_FRAME_HEIGHT) == 0:
			self.probe()

		# Ensure num_frames_read is reset to 0
		self.num_frames_read = 0

		stream, ret = (
			ffmpeg
			.input(self.device_name, format=self.device_format)
			.output('pipe:', format='rawvideo', pix_fmt='rgb24', vframes=numframes)
			.run(capture_stdout=True, quiet=True)
		)
		self.video = (
			numpy
			.frombuffer(stream, numpy.uint8)
			.reshape([-1, self.width, self.height, 3])
		)


	def read(self):
		""" Read a sigle frame from the self.video array. Will record a video if array is empty. """

		# First time we are called, we want to initialize the camera by probing it, to ensure we have height/width
		# and then take numframes of video to fill the buffer for faster recognition.
		if self.init_camera:
			self.init_camera = False
			self.video = ()
			self.record(self.numframes)
			return 0, self.video

		# If we are called and self.video is empty, we should record self.numframes to fill the video buffer
		if self.video == ():
			self.record(self.numframes)

		# If we've read max frames, but still are being requested to read more, we simply record another batch.
		# Note, the video array is 0 based, so if numframes is 10, we must subtract 1 or run into an array index
		# error.
		if self.num_frames_read >= (self.numframes - 1):
			self.record(self.numframes)

		# Add one to num_frames_read. If we were at 0, that's fine as frame 0 is almost 100% going to be black
		# as the IR lights aren't fully active yet anyways. Saves us one iteration in the while loop ni add/compare.py.
		self.num_frames_read += 1

		# Return a single frame of video
		return 0, self.video[self.num_frames_read]

	def release(self):
		""" Empty our array. If we had a hold on the camera, we would give it back here. """
		self.video = ()
		self.num_frames_read = 0

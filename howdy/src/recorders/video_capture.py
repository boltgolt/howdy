# Top level class for a video capture providing simplified API's for common
# functions

# Import required modules
import configparser
import cv2
import os
import sys
import time
import subprocess
import shlex  # Import shlex for safer command splitting

from howdy.src.i18n import _


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

        # The gstreamer pipeline process
        self.gst_process = None

        # Parse config from string if needed
        if isinstance(config, str):
            self.config = configparser.ConfigParser()
            self.config.read(config)
        else:
            self.config = config

        # Check device path
        if not os.path.exists(self.config.get("video", "device_path")):
            # If we're using GStreamer, the device might be created by the pipeline
            # so we skip this check in that case.
            if not self.config.getboolean("video", "use_gstreamer", fallback=False):
                if self.config.getboolean("video", "warn_no_device", fallback=True):
                    print(_("Howdy could not find a camera device at the path specified in the config file."))
                    print(
                        _("It is very likely that the path is not configured correctly, please edit the 'device_path' config value by running:"))
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
        # Don't try to grab if the reader wasn't created
        if self.internal:
            self.internal.grab()

    def __del__(self):
        """
		Frees resources when destroyed
		"""
        # The 'if self is not None' check is redundant here, __del__ is only called on objects
        self.release()

    def release(self):
        """
		Release cameras and kill the GStreamer subprocess if it exists.
		"""
        # Stop the gstreamer process if it's running
        if self.gst_process:
            try:
                # Try to terminate gracefully first
                self.gst_process.terminate()
                # Wait up to 1 second for it to terminate
                self.gst_process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                # If it doesn't respond, force kill it
                self.gst_process.kill()
            self.gst_process = None

        # Release the OpenCV capture object
        if self.internal:
            self.internal.release()
            self.internal = None

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
        recording_plugin = self.config.get("video", "recording_plugin", fallback="opencv")
        use_gstreamer = self.config.getboolean("video", "use_gstreamer", fallback=False)

        # If enabled, start the GStreamer pipeline as a subprocess
        if use_gstreamer:
            pipeline = self.config.get("video", "gstreamer_pipeline", fallback=None)
            if not pipeline:
                print(_("use_gstreamer is true but no gstreamer_pipeline is configured"))
                sys.exit(15)

            # Safer way to run subprocess without shell=True
            command = shlex.split(pipeline)

            try:
                # Start the pipeline as a subprocess, redirecting output
                self.gst_process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                # Give the pipeline some time to start up
                time.sleep(self.config.getint("video", "gstreamer_startup_delay", fallback=2))
            except FileNotFoundError:
                print(_("GStreamer command not found: {}").format(command[0]))
                print(_("Please ensure GStreamer is installed correctly."))
                sys.exit(16)
            except Exception as e:
                print(_("Failed to start GStreamer pipeline: {}").format(e))
                sys.exit(17)

        if recording_plugin == "ffmpeg":
            # Set the capture source for ffmpeg
            from howdy.src.recorders.ffmpeg_reader import ffmpeg_reader
            self.internal = ffmpeg_reader(
                self.config.get("video", "device_path"),
                self.config.get("video", "device_format", fallback="v4l2")
            )

        elif recording_plugin == "pyv4l2":
            # Set the capture source for pyv4l2
            from howdy.src.recorders.pyv4l2_reader import pyv4l2_reader
            self.internal = pyv4l2_reader(
                self.config.get("video", "device_path"),
                self.config.get("video", "device_format", fallback="v4l2")
            )

        else:
            # Start video capture on the IR camera through OpenCV
            self.internal = cv2.VideoCapture(
                self.config.get("video", "device_path"),
                cv2.CAP_V4L2
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

        # Set the frame width and height if requested
        self.fw = self.config.getint("video", "frame_width", fallback=-1)
        self.fh = self.config.getint("video", "frame_height", fallback=-1)
        if self.fw != -1:
            self.internal.set(cv2.CAP_PROP_FRAME_WIDTH, self.fw)
        if self.fh != -1:
            self.internal.set(cv2.CAP_PROP_FRAME_HEIGHT, self.fh)
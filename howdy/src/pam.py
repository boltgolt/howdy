# PAM interface in python, launches compare.py

# Import required modules
import subprocess
import os
import glob
import syslog

# pam-python is running python 2, so we use the old module here
import ConfigParser

# Read config from disk
config = ConfigParser.ConfigParser()
config.read(os.path.dirname(os.path.abspath(__file__)) + "/config.ini")


def doAuth(pamh):
	"""Starts authentication in a seperate process"""

	# Abort if Howdy is disabled
	if config.getboolean("core", "disabled"):
		return pamh.PAM_AUTHINFO_UNAVAIL

	# Abort if we're in a remote SSH env
	if config.getboolean("core", "ignore_ssh"):
		if "SSH_CONNECTION" in os.environ or "SSH_CLIENT" in os.environ or "SSHD_OPTS" in os.environ:
			return pamh.PAM_AUTHINFO_UNAVAIL

	# Abort if lid is closed
	if config.getboolean("core", "ignore_closed_lid"):
		if any("closed" in open(f).read() for f in glob.glob("/proc/acpi/button/lid/*/state")):
			return pamh.PAM_AUTHINFO_UNAVAIL

	# Abort if the video device does not exist
	if not os.path.exists(config.get("video", "device_path")):
		if config.getboolean("video", "warn_no_device"):
			print("Camera path is not configured correctly, please edit the 'device_path' config value.")
		return pamh.PAM_AUTHINFO_UNAVAIL

	# Set up syslog
	syslog.openlog("[HOWDY]", 0, syslog.LOG_AUTH)

	# Alert the user that we are doing face detection
	if config.getboolean("core", "detection_notice"):
		pamh.conversation(pamh.Message(pamh.PAM_TEXT_INFO, "Attempting face detection"))

	syslog.syslog(syslog.LOG_INFO, "Attempting facial authentication for user " + pamh.get_user())

	# Run compare as python3 subprocess to circumvent python version and import issues
	status = subprocess.call(["/usr/bin/python3", os.path.dirname(os.path.abspath(__file__)) + "/compare.py", pamh.get_user()])

	# Status 10 means we couldn't find any face models
	if status == 10:
		if not config.getboolean("core", "suppress_unknown"):
			pamh.conversation(pamh.Message(pamh.PAM_ERROR_MSG, "No face model known"))

		syslog.syslog(syslog.LOG_NOTICE, "Failure, no face model known")
		syslog.closelog()
		return pamh.PAM_USER_UNKNOWN

	# Status 11 means we exceded the maximum retry count
	elif status == 11:
		if config.getboolean("core", "timeout_notice"):
			pamh.conversation(pamh.Message(pamh.PAM_ERROR_MSG, "Face detection timeout reached"))
		syslog.syslog(syslog.LOG_INFO, "Failure, timeout reached")
		syslog.closelog()
		return pamh.PAM_AUTH_ERR

	# Status 12 means we aborted
	elif status == 12:
		syslog.syslog(syslog.LOG_INFO, "Failure, general abort")
		syslog.closelog()
		return pamh.PAM_AUTH_ERR

	# Status 13 means the image was too dark
	elif status == 13:
		pamh.conversation(pamh.Message(pamh.PAM_ERROR_MSG, "Face detection image too dark"))
		syslog.syslog(syslog.LOG_INFO, "Failure, image too dark")
		syslog.closelog()
		return pamh.PAM_AUTH_ERR

	# Status 14 means a rubberstamp could not be given
	elif status == 14:
		pamh.conversation(pamh.Message(pamh.PAM_ERROR_MSG, "Rubberstamp denied"))
		syslog.syslog(syslog.LOG_INFO, "Failure, rubberstamp did not succeed")
		syslog.closelog()
		return pamh.PAM_AUTH_ERR

	# Status 1 is probably a python crash
	elif status == 1:
		pamh.conversation(pamh.Message(pamh.PAM_ERROR_MSG, "Howdy encountered error, check stderr"))
		syslog.syslog(syslog.LOG_INFO, "Failure, process crashed while authenticating")
		syslog.closelog()
		return pamh.PAM_SYSTEM_ERR

	# Status 0 is a successful exit
	elif status == 0:
		# Show the success message if it isn't suppressed
		if not config.getboolean("core", "no_confirmation"):
			pamh.conversation(pamh.Message(pamh.PAM_TEXT_INFO, "Identified face as " + pamh.get_user()))

		syslog.syslog(syslog.LOG_INFO, "Login approved")
		syslog.closelog()
		return pamh.PAM_SUCCESS

	# Otherwise, we can't discribe what happend but it wasn't successful
	pamh.conversation(pamh.Message(pamh.PAM_ERROR_MSG, "Unknown error: " + str(status)))
	syslog.syslog(syslog.LOG_INFO, "Failure, unknown error" + str(status))
	syslog.closelog()
	return pamh.PAM_SYSTEM_ERR


def pam_sm_authenticate(pamh, flags, args):
	"""Called by PAM when the user wants to authenticate, in sudo for example"""
	return doAuth(pamh)


def pam_sm_open_session(pamh, flags, args):
	"""Called when starting a session, such as su"""
	return doAuth(pamh)


def pam_sm_close_session(pamh, flags, argv):
	"""We don't need to clean anyting up at the end of a session, so returns true"""
	return pamh.PAM_SUCCESS


def pam_sm_setcred(pamh, flags, argv):
	"""We don't need set any credentials, so returns true"""
	return pamh.PAM_SUCCESS

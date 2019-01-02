# PAM interface in python, launches compare.py

# Import required modules
import subprocess
import sys
import os

# pam-python is running python 2, so we use the old module here
import ConfigParser

# Read config from disk
config = ConfigParser.ConfigParser()
config.read(os.path.dirname(os.path.abspath(__file__)) + "/config.ini")

def doAuth(pamh):
	"""Starts authentication in a seperate process"""

	# Abort is Howdy is disabled
	if config.get("core", "disabled") == "true":
		sys.exit(0)

	# Abort if we're in a remote SSH env
	if config.get("core", "ignore_ssh") == "true":
		if "SSH_CONNECTION" in os.environ or "SSH_CLIENT" in os.environ or "SSHD_OPTS" in os.environ:
			sys.exit(0)

	# Alert the user that we are doing face detection	
	pamh.conversation(pamh.Message(pamh.PAM_TEXT_INFO, "Attempting face detection"))

	# Run compare as python3 subprocess to circumvent python version and import issues
	status = subprocess.call(["/usr/bin/python3", os.path.dirname(os.path.abspath(__file__)) + "/compare.py", pamh.get_user()])

	# Status 10 means we couldn't find any face models
	if status == 10:
		if config.get("core", "suppress_unknown") != "true":
			pamh.conversation(pamh.Message(pamh.PAM_ERROR_MSG, "No face model known"))
		return pamh.PAM_USER_UNKNOWN
	# Status 11 means we exceded the maximum retry count
	if status == 11:
		pamh.conversation(pamh.Message(pamh.PAM_ERROR_MSG, "Face detection timeout reached"))
		return pamh.PAM_AUTH_ERR
	# Status 0 is a successful exit
	if status == 0:
		# Show the success message if it isn't suppressed
		if config.get("core", "no_confirmation") != "true":
			pamh.conversation(pamh.Message(pamh.PAM_TEXT_INFO, "Identified face as " + pamh.get_user()))

		# Try to dismiss the lock screen if enabled
		if config.get("core", "dismiss_lockscreen") == "true":
			# Run it as root with a timeout of 1s, and never ask for a password through the UI
			subprocess.Popen(["sudo", "timeout", "1", "loginctl", "unlock-sessions", "--no-ask-password"])

		return pamh.PAM_SUCCESS

	# Otherwise, we can't discribe what happend but it wasn't successful
	pamh.conversation(pamh.Message(pamh.PAM_ERROR_MSG, "Unknown error: " + str(status)))
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

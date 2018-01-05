# PAM interface in python, launches compair.py

# Import required modules
import subprocess
import sys
import os

def doAuth(pamh):
	"""Start authentication in a seperate process"""

	# Run compair as python3 subprocess to circumvent python version and import issues
	status = subprocess.call(["python3", os.path.dirname(__file__) + "/compair.py", pamh.get_user()])

	# Status 10 means we couldn't find any face models
	if status == 10:
		print("No face model is known for this user, skiping")
		return pamh.PAM_SYSTEM_ERR
	# Status 11 means we exceded the maximum retry count
	if status == 11:
		print("Timeout reached, could not find a known face")
		return pamh.PAM_SYSTEM_ERR
	# Status 0 is a successful exit
	if status == 0:
		print("Identified face as " + os.environ.get("USER"))
		return pamh.PAM_SUCCESS

	# Otherwise, we can't discribe what happend but it wasn't successful
	print("Unknown error: " + str(status))
	return pamh.PAM_SYSTEM_ERR

def pam_sm_authenticate(pamh, flags, args):
	"""Called by PAM when the user wants to authenticate, in sudo for example"""
	return doAuth(pamh)

def pam_sm_open_session(pamh, flags, args):
	"""Called when starting a session, such as su"""
	return doAuth(pamh)

def pam_sm_close_session(pamh, flags, argv):
	"""We don't need to clean anyting up at the end of a session, so return true"""
	return pamh.PAM_SUCCESS

def pam_sm_setcred(pamh, flags, argv):
	"""We don't need set any credentials, so return true"""
	return pamh.PAM_SUCCESS

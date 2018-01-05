import subprocess
import sys
import os

def doAuth(pamh):
	status = subprocess.call(["python3", os.path.dirname(__file__) + "/compair.py", pamh.get_user()])

	if status == 10:
		print("No face model is known for this user, skiping")
		return pamh.PAM_SYSTEM_ERR
	if status == 11:
		print("Timeout reached, ould not find a known face")
		return pamh.PAM_SYSTEM_ERR
	if status == 0:
		print("Identified face as " + os.environ.get("USER"))
		return pamh.PAM_SUCCESS

	print("Unknown error: " + str(status))
	return pamh.PAM_SYSTEM_ERR

def pam_sm_authenticate(pamh, flags, args):
	return doAuth(pamh)

def pam_sm_open_session(pamh, flags, args):
	return doAuth(pamh)

def pam_sm_close_session(pamh, flags, argv):
	return pamh.PAM_SUCCESS

def pam_sm_setcred(pamh, flags, argv):
	return pamh.PAM_SUCCESS

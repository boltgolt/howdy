import subprocess
import sys
import os

def pam_sm_authenticate(pamh, flags, args):
	status = subprocess.call(["python3", "compair.py", pamh.get_user()])

	if status == 801:
		print("Timeout reached, ould not find a known face")
		return pamh.PAM_SYSTEM_ERR
	if status == 34:
		print("No face model is known for this user")
		return pamh.PAM_SYSTEM_ERR
	if status == 0:
		print("Identified face as " + os.environ.get("USER"))
		return pamh.PAM_SUCCESS

	return pamh.PAM_SYSTEM_ERR

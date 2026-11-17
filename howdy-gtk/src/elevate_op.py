# Helper module to run privileged operations from the unprivileged GUI.
#
# howdy-gtk itself no longer re-executes itself as root (which broke on
# Wayland, where the root process has no access to the user's display).
# Instead the GUI stays unprivileged and only the howdy CLI calls that
# write to /etc/howdy are elevated per-operation, preferring pkexec.

import os
import shutil
import subprocess


def _howdy_path():
	"""Return the path of the howdy CLI"""
	return shutil.which("howdy") or "/usr/bin/howdy"


def _prefix():
	"""Return an argv prefix that executes a command as root, or an empty
	list when we already run as root. Prefers pkexec because it works in
	graphical sessions and keeps track of the invoking user."""
	if os.geteuid() == 0:
		return []

	if shutil.which("pkexec") is not None:
		return ["pkexec"]

	return ["sudo"]


def run(argv, **kwargs):
	"""Run a command as root, arguments are passed safely as a list"""
	return subprocess.run(_prefix() + list(argv), **kwargs)


def popen(argv, **kwargs):
	"""Start a command as root, arguments are passed safely as a list"""
	return subprocess.Popen(_prefix() + list(argv), **kwargs)


def howdy_run(args, **kwargs):
	"""Run the howdy CLI as root, arguments are passed safely as a list"""
	return run([_howdy_path()] + list(args), **kwargs)


def howdy_popen(args, **kwargs):
	"""Start the howdy CLI as root, arguments are passed safely as a list"""
	return popen([_howdy_path()] + list(args), **kwargs)


def howdy_getstatusoutput(args):
	"""Run the howdy CLI as root and return a (status, output) tuple"""
	try:
		proc = howdy_run(list(args), capture_output=True, text=True)
		return proc.returncode, (proc.stdout or "") + (proc.stderr or "")
	except OSError as err:
		return 1, str(err)

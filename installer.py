# Installation script to install howdy
# Runs completely independent of the others

# Import required modules
import subprocess
import time
import sys
import os
import re
import signal
import fileinput
import urllib.parse

def log(text):
	"""Print a nicely formatted line to stdout"""
	print("\n>>> \033[32m" + text + "\033[0m\n")

def handleStatus(status):
	"""Abort if a command fails"""
	if (status != 0):
		print("\033[31mError while running last command\033[0m")
		sys.exit()

# Check if we're running as root
user = os.getenv("SUDO_USER")
if user is None:
	print("Please run this script as a sudo user")
	sys.exit()

# Print some nice intro text
print("\n\033[33m   HOWDY INSTALLER FOR UBUNTU\033[0m")
print("   Version 1, 2016/02/05\n")

# Let it sink in
time.sleep(.5)
log("Installing required apt packages")

# Install packages though apt
handleStatus(subprocess.call(["apt", "install", "-y", "git",
													  "python3-pip",
													  "python3-dev",
													  "python3-setuptools",
													  "build-essential",
													  "libpam-python",
													  "fswebcam",
													  "libopencv-dev",
													  "python-opencv",
													  "cmake"]))

# Update pip
handleStatus(subprocess.call(["pip install --upgrade pip"], shell=True))

log("Starting camera check")

# Get all devices
devices = os.listdir("/dev")
# The picked video device id
picked = False

# Loop though all devices
for dev in devices:
	# Only use the video devices
	if (dev[:5] == "video"):
		time.sleep(.5)

		# The full path to the device is the default name
		device_name = "/dev/" + dev
		# Get the udevadm details to try to get a better name
		udevadm = subprocess.check_output(["udevadm info -r --query=all -n " + device_name], shell=True).decode("utf-8")

		# Loop though udevadm to search for a better name
		for line in udevadm.split("\n"):
			# Match it and encase it in quotes
			re_name = re.search('product.*=(.*)$', line, re.IGNORECASE)
			if re_name:
				device_name = '"' + re_name.group(1) + '"'

		# Show what device we're using
		print("Trying " + device_name)

		# Let fswebcam keep the camera open in the background
		sub = subprocess.Popen(["fswebcam -S 9999999999 -d /dev/" + dev + " /dev/null 2>/dev/null"], shell=True, preexec_fn=os.setsid)

		# Ask the user if this is the right one
		print("\033[33mOne of your cameras should now be on.\033[0m")
		ans = input("Did your IR emitters turn on? [y/N]: ")

		# The user has answered, kill fswebcam
		os.killpg(os.getpgid(sub.pid), signal.SIGTERM)

		# Set this camera as picked if the answer was yes, go to the next one if no
		if (ans.lower() == "y"):
			picked = dev[5:]
			break
		else:
			print("Inerpeting as a \"NO\"\n")

# Abort if no camera was picked
if (picked == False):
	print("\033[31mNo suitable IR camera found\033[0m")
	sys.exit()

log("Cloning dlib")

# Clone the git to /tmp
handleStatus(subprocess.call(["git", "clone", "https://github.com/davisking/dlib.git", "/tmp/dlib_clone"]))

log("Building dlib")

# Start the build without GPU
handleStatus(subprocess.call(["cd /tmp/dlib_clone/; python3 setup.py install --yes USE_AVX_INSTRUCTIONS --no DLIB_USE_CUDA"], shell=True))

log("Cleaning up dlib")

# Remove the no longer needed git clone
handleStatus(subprocess.call(["rm", "-rf", "/tmp/dlib_clone"]))

log("Installing face_recognition")

# Install face_recognition though pip
handleStatus(subprocess.call(["pip3", "install", "face_recognition"]))

log("Cloning howdy")

# Make sure /lib/security exists
if not os.path.exists("/lib/security"):
	os.makedirs("/lib/security")

# Clone howdy into it
handleStatus(subprocess.call(["git", "clone", "https://github.com/Boltgolt/howdy.git", "/lib/security/howdy"]))

# Manually change the camera id to the one picked
for line in fileinput.input(["/lib/security/howdy/config.ini"], inplace = 1):
	print(line.replace("device_id = 1", "device_id = " + picked), end="")

# Secure the howdy folder
handleStatus(subprocess.call(["chmod 600 -R /lib/security/howdy/"], shell=True))

# Make the CLI executable as howdy
handleStatus(subprocess.call(["ln -s /lib/security/howdy/cli.py /usr/bin/howdy"], shell=True))
handleStatus(subprocess.call(["chmod +x /usr/bin/howdy"], shell=True))

# Install the command autocomplete, don't error on failure
subprocess.call(["sudo cp /lib/security/howdy/autocomplete.sh /etc/bash_completion.d/howdy"], shell=True)

log("Adding howdy as PAM module")

# Will be filled with the actual output lines
outlines = []
# Will be fillled with lines that contain coloring
printlines = []
# Track if the new lines have been insterted yet
inserted = False

# Open the PAM config file
with open("/etc/pam.d/common-auth") as fp:
	# Read the first line
	line = fp.readline()

	while line:
		# Add the line to the output directly, we're not deleting anything
		outlines.append(line)

		# Print the comments in gray and don't insert into comments
		if line[:1] == "#":
			printlines.append("\033[37m" + line + "\033[0m")
		else:
			printlines.append(line)

			# If it's not a comment and we haven't inserted yet
			if not inserted:
				# Set both the comment and the linking line
				line_comment = "# Howdy IR face recognition\n"
				line_link	= "auth	sufficient			pam_python.so /lib/security/howdy/pam.py\n\n"

				# Add them to the output without any markup
				outlines.append(line_comment)
				outlines.append(line_link)

				# Make the print orange to make it clear what's being added
				printlines.append("\033[33m" + line_comment + "\033[0m")
				printlines.append("\033[33m" + line_link + "\033[0m")

				# Mark as inserted
				inserted = True

		# Go to the next line
		line = fp.readline()

# Print a file Header
print("\033[33m" + ">>> START OF /etc/pam.d/common-auth" + "\033[0m")

# Loop though all printing lines and use the enters from the file
for line in printlines:
	print(line, end="")

# Print a footer
print("\033[33m" + ">>> END OF /etc/pam.d/common-auth" + "\033[0m" + "\n")

# Ask the user if this change is okay
print("Lines will be insterted in /etc/pam.d/common-auth as shown above")
ans = input("Apply this change? [y/N]: ")

# Abort the whole thing if it's not
if (ans.lower() != "y"):
	print("Inerpeting as a \"NO\", aborting")
	sys.exit()

print("Adding lines to PAM\n")

# Write to PAM
common_auth = open("/etc/pam.d/common-auth", "w")
common_auth.write("".join(outlines))
common_auth.close()

# From here onwards the installation is complete
# We want to gather more information about the types or IR camera's
# used though, and the following lines are data collection

# List all video devices
diag_out = "Video devices [IR=" + picked + "]\n"
diag_out += "```\n"
diag_out += subprocess.check_output(['ls /dev/ | grep video'], shell=True).decode("utf-8")
diag_out += "```\n"

# Get some info from the USB kernel listings
diag_out += "Lsusb output\n"
diag_out += "```\n"
diag_out += subprocess.check_output(['lsusb -vvvv | grep -i "Camera\|iFunction"'], shell=True).decode("utf-8")
diag_out += "```\n"

# Get camera information from video4linux
diag_out += "Udevadm\n"
diag_out += "```\n"
diag_out += subprocess.check_output(['udevadm info -r --query=all -n /dev/video' + picked + ' | grep -i "ID_BUS\|ID_MODEL_ID\|ID_VENDOR_ID\|ID_V4L_PRODUCT\|ID_MODEL"'], shell=True).decode("utf-8")
diag_out += "```"

# Print it all as a clickable link to a new github issue
print("https://github.com/Boltgolt/howdy-reports/issues/new?title=Post-installation%20camera%20information&body=" + urllib.parse.quote_plus(diag_out) + "\n")

# Let the user know what to do with the link
print("Installation complete.")
print("If you want to help the development, please use the link above to post some camera-related information to github")

# Remove the installer if it was downloaded to /tmp
if os.path.exists("/tmp/howdy_install.py"):
	os.remove("/tmp/howdy_install.py")

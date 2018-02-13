import subprocess
import time
import sys
import os
import re
import signal
import fileinput
import urllib.parse

def log(text):
	print("\n>>> \033[32m" + text + "\033[0m\n")

def handleStatus(status):
	if (status != 0):
		print("\033[31mError while running last command\033[0m")
		sys.exit()

user = os.getenv("SUDO_USER")

if user is None:
	print("Please run this script as a sudo user")
	sys.exit()

print("\n\033[33m   HOWDY INSTALLER FOR UBUNTU\033[0m")
print("   Version 1, 2016/02/05\n")

time.sleep(.5)
log("Installing required apt packages")

handleStatus(subprocess.call(["apt", "install", "-y", "libpam-python", "fswebcam", "libopencv-dev", "python-opencv"]))

log("Starting camera check")

devices = os.listdir("/dev")
picked = False

for dev in devices:
	if (dev[:5] == "video"):
		time.sleep(.5)

		device_name = "/dev/" + dev
		udevadm = subprocess.check_output(["udevadm info -r --query=all -n " + device_name], shell=True).decode("utf-8")

		for line in udevadm.split("\n"):
			re_name = re.search('product.*=(.*)$', line, re.IGNORECASE)

			if re_name:
				device_name = '"' + re_name.group(1) + '"'

		print("Trying " + device_name)

		sub = subprocess.Popen(["fswebcam -S 9999999999 -d /dev/" + dev + " /dev/null 2>/dev/null"], shell=True, preexec_fn=os.setsid)

		print("\033[33mOne of your cameras should now be on.\033[0m")
		ans = input("Did your IR emitters turn on? [y/N]: ")

		os.killpg(os.getpgid(sub.pid), signal.SIGTERM)

		if (ans.lower() == "y"):
			picked = dev[5:]
			break
		else:
			print("Inerpeting as a \"NO\"\n")

if (picked == False):
	print("\033[31mNo suitable IR camera found\033[0m")
	sys.exit()

log("Cloning dlib")

handleStatus(subprocess.call(["git", "clone", "https://github.com/davisking/dlib.git", "/tmp/dlib_clone"]))

log("Building dlib")

handleStatus(subprocess.call(["cd /tmp/dlib_clone/; python3 setup.py install --yes USE_AVX_INSTRUCTIONS --no DLIB_USE_CUDA"], shell=True))

log("Cleaning up dlib")

handleStatus(subprocess.call(["rm", "-rf", "/tmp/dlib_clone"]))

log("Installing face_recognition")

handleStatus(subprocess.call(["pip3", "install", "face_recognition"]))

log("Cloning howdy")

if not os.path.exists("/lib/security"):
	os.makedirs("/lib/security")

handleStatus(subprocess.call(["git", "clone", "https://github.com/Boltgolt/howdy.git", "/lib/security/howdy"]))

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

outlines = []
printlines = []
inserted = False

with open("/etc/pam.d/common-auth") as fp:
	line = fp.readline()
	cnt = 1
	while line:
		outlines.append(line)

		if line[:1] != "#":
			printlines.append(line)

			if not inserted:
				line_comment = "# Howdy IR face recognition\n"
				line_Link	= "auth	sufficient			pam_python.so /lib/security/howdy/pam.py\n\n"

				outlines.append(line_comment)
				outlines.append(line_Link)

				printlines.append("\033[33m" + line_comment + "\033[0m")
				printlines.append("\033[33m" + line_Link + "\033[0m")

				inserted = True
		else:
			printlines.append("\033[37m" + line + "\033[0m")

		line = fp.readline()
		cnt += 1

print("\033[33m" + ">>> START OF /etc/pam.d/common-auth" + "\033[0m")

for line in printlines:
	print(line, end="")

print("\033[33m" + ">>> END OF /etc/pam.d/common-auth" + "\033[0m" + "\n")

print("Lines will be insterted in /etc/pam.d/common-auth as shown above")
ans = input("Apply this change? [y/N]: ")

if (ans.lower() != "y"):
	print("Inerpeting as a \"NO\", aborting")
	sys.exit()

print("Adding lines to PAM\n")

common_auth = open("/etc/pam.d/common-auth", "w")
common_auth.write("".join(outlines))
common_auth.close()

diag_out = "Video devices [IR=" + picked + "]\n"
diag_out += "```\n"
diag_out += subprocess.check_output(['ls /dev/ | grep video'], shell=True).decode("utf-8")
diag_out += "```\n"

diag_out += "Lsusb output\n"
diag_out += "```\n"
diag_out += subprocess.check_output(['lsusb -vvvv | grep -i "Camera\|iFunction"'], shell=True).decode("utf-8")
diag_out += "```\n"

diag_out += "Udevadm\n"
diag_out += "```\n"
diag_out += subprocess.check_output(['udevadm info -r --query=all -n /dev/video' + picked + ' | grep -i "ID_BUS\|ID_MODEL_ID\|ID_VENDOR_ID\|ID_V4L_PRODUCT\|ID_MODEL"'], shell=True).decode("utf-8")
diag_out += "```"

print("https://github.com/Boltgolt/howdy-reports/issues/new?title=Post-installation%20camera%20information&body=" + urllib.parse.quote_plus(diag_out) + "\n")

print("Installation complete.")
print("If you want to help the development, please use the link above to post some camera-related information to github")

# Remove the installer if downloaded to tmp
if os.path.exists("/tmp/howdy_install.py"):
	os.remove("/tmp/howdy_install.py")

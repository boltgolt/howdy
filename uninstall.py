# Completely remove howdy from the system

# Import required modules
import subprocess
import sys
import os

# Check if we're running as root
user = os.getenv("SUDO_USER")
if user is None:
	print("Please run the uninstaller as a sudo user")
	sys.exit()

# Double check with the user for the last time
print("This will remove Howdy and all models generated with it")
ans = input("Do you want to continue? [y/N]: ")

# Abort if they don't say yes
if (ans.lower() != "y"):
	sys.exit()

# Remove files and symlinks
subprocess.call(["rm -rf /lib/security/howdy/"], shell=True)
subprocess.call(["rm /usr/bin/howdy"], shell=True)
subprocess.call(["rm /etc/bash_completion.d/howdy"], shell=True)

# Remove face_recognition and dlib
subprocess.call(["pip3 uninstall face_recognition dlib -y"], shell=True)

# Print a tearbending message
print("""
Howdy has been uninstalled :'(

There are still lines in /etc/pam.d/common-auth that can't be removed automatically
Run "nano /etc/pam.d/common-auth" to remove them by hand\
""")

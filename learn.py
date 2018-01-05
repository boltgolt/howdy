import subprocess
import time
import os

user = os.environ.get("USER")

if not os.path.exists("models"):
	os.makedirs("models")

if not os.path.exists("models/" + user):
	print("No face model folder found, creating one")
	os.makedirs("models/" + user)

print("Learning face for the user account " + os.environ.get("USER"))
print("Please look straigt into the camera for 5 seconds")

time.sleep(2.5)

subprocess.call(["fswebcam", "-S", "30", "--no-banner", "-d", "/dev/video1", "./models/" + user + "/L.jpg"], stderr=open(os.devnull, "wb"))

time.sleep(.3)

subprocess.call(["fswebcam", "-S", "6", "--no-banner", "-d", "/dev/video1", "./models/" + user + "/M.jpg"], stderr=open(os.devnull, "wb"))

time.sleep(.3)

subprocess.call(["fswebcam", "--no-banner", "-d", "/dev/video1", "./models/" + user + "/S.jpg"], stderr=open(os.devnull, "wb"))

print("Done.")

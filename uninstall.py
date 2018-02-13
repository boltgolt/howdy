import subprocess

subprocess.call(["rm -rf /lib/security/howdy/"], shell=True)
subprocess.call(["rm /usr/bin/howdy"], shell=True)

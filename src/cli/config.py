# Open the config file in gedit

# Import required modules
import os
import time
import subprocess

# Let the user know what we're doing
print("Opening config.ini in gedit")

# Open gedit as a subprocess and fork it
subprocess.Popen(["gedit", os.path.dirname(os.path.realpath(__file__))  + "/../config.ini"],
                  cwd="/",
                  stdout=subprocess.PIPE,
                  stderr=subprocess.STDOUT)

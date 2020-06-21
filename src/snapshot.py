# Create and save snapshots of auth attemtps

# Import modules
import cv2
import os
import datetime
import numpy as np


def generate(frames, text_lines):
	"""Generate a shapshot from given frames"""

	# Don't execute if no frames were given
	if len(frames) == 0:
		return

	# Get the path to the containing folder
	abpath = os.path.dirname(os.path.abspath(__file__))
	# Get frame dimentions
	frame_height, frame_width, cc = frames[0].shape
	# Spread the given frames out horizontally
	snap = np.concatenate(frames, axis=1)

	# Create colors
	pad_color = [44, 44, 44]
	text_color = [255, 255, 255]

	# Add a gray square at the bottom of the image
	snap = cv2.copyMakeBorder(snap, 0, len(text_lines) * 20 + 40, 0, 0, cv2.BORDER_CONSTANT, value=pad_color)

	# Add the Howdy logo if there's space to do so
	if len(frames) > 1:
		# Load the logo from file
		logo = cv2.imread(abpath + "/logo.png")
		# Calculate the position of the logo
		logo_y = frame_height + 20
		logo_x = frame_width * len(frames) - 210

		# Overlay the logo on top of the image
		snap[logo_y:logo_y+57, logo_x:logo_x+180] = logo

	# Go through each line
	line_number = 0
	for line in text_lines:
		# Calculate how far the line should be from the top
		padding_top = frame_height + 30 + (line_number * 20)
		# Print the line onto the image
		cv2.putText(snap, line, (30, padding_top), cv2.FONT_HERSHEY_SIMPLEX, .4, text_color, 0, cv2.LINE_AA)

		line_number += 1

	# Made sure a snapshot folder exist
	if not os.path.exists(abpath + "/snapshots"):
		os.makedirs(abpath + "/snapshots")

	# Generate a filename based on the current time
	filename = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%S.jpg")
	# Write the image to that file
	cv2.imwrite(abpath + "/snapshots/" + filename, snap)

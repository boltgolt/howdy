# Rotation of captured frames, see the "rotate" option in config.ini

import cv2


def rotate_frame(frame, rotate, frame_number):
	"""
	Returns the frame turned the way the rotate option asks for. Modes 1 and 2
	try several orientations, so they depend on the frame number.
	"""
	code = None
	# Check landscape and both portrait orientations
	if rotate == 1:
		if frame_number % 3 == 1:
			code = cv2.ROTATE_90_COUNTERCLOCKWISE
		elif frame_number % 3 == 2:
			code = cv2.ROTATE_90_CLOCKWISE
	# Check both portrait orientations
	elif rotate == 2:
		if frame_number % 2 == 0:
			code = cv2.ROTATE_90_COUNTERCLOCKWISE
		else:
			code = cv2.ROTATE_90_CLOCKWISE
	# Fixed portrait orientations, for cameras that are mounted sideways
	elif rotate == 3:
		code = cv2.ROTATE_90_COUNTERCLOCKWISE
	elif rotate == 4:
		code = cv2.ROTATE_90_CLOCKWISE

	if code is None:
		return frame
	return cv2.rotate(frame, code)

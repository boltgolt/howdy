import face_recognition
import cv2
import sys
import os
import json

import config

def stop(status):
	video_capture.release()
	sys.exit(status)

try:
	if not isinstance(sys.argv[1], str):
		sys.exit(1)
except IndexError:
	sys.exit(1)

user = sys.argv[1]
encodings = []
tries = 0

try:
	encodings = json.load(open(os.path.dirname(__file__) + "/models/" + user + ".dat"))
except FileNotFoundError:
	stop(10)

if len(encodings) < 3:
	stop(1)

video_capture = cv2.VideoCapture(config.device_id)

while True:
	# Grab a single frame of video
	ret, frame = video_capture.read()

	face_encodings = face_recognition.face_encodings(frame)

	# Loop through each face in this frame of video
	for face_encoding in face_encodings:
		matches = face_recognition.face_distance(encodings, face_encoding)

		for match in matches:
			if match < config.certainty:
				stop(0)

	if tries > config.frame_count:
		stop(11)

	tries += 1

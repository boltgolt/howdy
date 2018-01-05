import face_recognition
import cv2
import sys
import os

def stop(status):
	video_capture.release()
	sys.exit(status)

path = ""
distance = 3

try:
	if not isinstance(sys.argv[1], str):
		sys.exit(1)
except IndexError:
	sys.exit(1)

user = sys.argv[1]

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(1)

encodings = []

try:
	for exposure in ["L", "M", "S"]:
		ref = face_recognition.load_image_file(path + "/" + user + "/" + exposure + ".jpg")
		enc = face_recognition.face_encodings(ref)[0]
		encodings.append(enc)
except FileNotFoundError:
	stop(802)

tries = 0

while True:
	# Grab a single frame of video
	ret, frame = video_capture.read()

	face_encodings = face_recognition.face_encodings(frame)

	# Loop through each face in this frame of video
	for face_encoding in face_encodings:
		matches = face_recognition.face_distance(encodings, face_encoding)

		for match in matches:
			if match < distance:
				stop(0)

	if tries => 100:
		stop(801)

	tries += 1

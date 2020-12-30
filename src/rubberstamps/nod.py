import time

from rubberstamps import RubberStamp


class nod(RubberStamp):
	def declare_config(self):
		self.options["min_distance"] = 10
		self.options["min_directions"] = 3

	def run(self):
		last_reldist = -1
		last_nosepoint = {"x": -1, "y": -1}
		recorded_nods = {"x": [], "y": []}

		starttime = time.time()

		while True:
			if time.time() > starttime + self.options["timeout"]:
				return not self.options["failsafe"]

			ret, frame = self.video_capture.read_frame()

			frame = self.clahe.apply(frame)

			face_locations = self.face_detector(frame, 1)

			if len(face_locations) != 1:
				continue

			face_landmarks = self.pose_predictor(frame, face_locations[0])

			reldist = face_landmarks.part(0).x - face_landmarks.part(2).x
			avg_reldist = (last_reldist + reldist) / 2

			for axis in ["x", "y"]:
				nosepoint = getattr(face_landmarks.part(4), axis)

				if last_nosepoint[axis] == -1:
					last_nosepoint[axis] = nosepoint
					last_reldist = reldist

				mindist = self.options["min_distance"]
				movement = (nosepoint - last_nosepoint[axis]) * 100 / avg_reldist

				if movement < -mindist or movement > mindist:
					if len(recorded_nods[axis]) == 0:
						recorded_nods[axis].append(movement < 0)

					elif recorded_nods[axis][-1] != (movement < 0):
						recorded_nods[axis].append(movement < 0)

				if len(recorded_nods[axis]) >= self.options["min_directions"]:
					return axis == "y"

				last_reldist = reldist
				last_nosepoint[axis] = nosepoint

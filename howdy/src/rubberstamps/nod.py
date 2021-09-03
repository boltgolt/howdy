import time

from i18n import _

# Import the root rubberstamp class
from rubberstamps import RubberStamp


class nod(RubberStamp):
	def declare_config(self):
		"""Set the default values for the optional arguments"""
		self.options["min_distance"] = 6
		self.options["min_directions"] = 2

	def run(self):
		"""Track a users nose to see if they nod yes or no"""
		self.set_ui_text(_("Nod to confirm"), self.UI_TEXT)
		self.set_ui_text(_("Shake your head to abort"), self.UI_SUBTEXT)

		# Stores relative distance between the 2 eyes in the last frame
		# Used to calculate the distance of the nose traveled in relation to face size in the frame
		last_reldist = -1
		# Last point the nose was at
		last_nosepoint = {"x": -1, "y": -1}
		# Contans booleans recording successful nods and their directions
		recorded_nods = {"x": [], "y": []}

		starttime = time.time()

		# Keep running the loop while we have not hit timeout yet
		while time.time() < starttime + self.options["timeout"]:
			# Read a frame from the camera
			ret, frame = self.video_capture.read_frame()

			# Apply CLAHE to get a better picture
			frame = self.clahe.apply(frame)

			# Detect all faces in the frame
			face_locations = self.face_detector(frame, 1)

			# Only continue if exacty 1 face is visible in the frame
			if len(face_locations) != 1:
				continue

			# Get the position of the eyes and tip of the nose
			face_landmarks = self.pose_predictor(frame, face_locations[0])

			# Calculate the relative distance between the 2 eyes
			reldist = face_landmarks.part(0).x - face_landmarks.part(2).x
			# Avarage this out with the distance found in the last frame to smooth it out
			avg_reldist = (last_reldist + reldist) / 2

			# Calulate horizontal movement (shaking head) and vertical movement (nodding)
			for axis in ["x", "y"]:
				# Get the location of the nose on the active axis
				nosepoint = getattr(face_landmarks.part(4), axis)

				# If this is the first frame set the previous values to the current ones
				if last_nosepoint[axis] == -1:
					last_nosepoint[axis] = nosepoint
					last_reldist = reldist

				mindist = self.options["min_distance"]
				# Get the relative movement by taking the distance traveled and deviding it by eye distance
				movement = (nosepoint - last_nosepoint[axis]) * 100 / max(avg_reldist, 1)

				# If the movement is over the minimal distance threshold
				if movement < -mindist or movement > mindist:
					# If this is the first recorded nod, add it to the array
					if len(recorded_nods[axis]) == 0:
						recorded_nods[axis].append(movement < 0)

					# Otherwise, only add this nod if the previous nod with in the other direction
					elif recorded_nods[axis][-1] != (movement < 0):
						recorded_nods[axis].append(movement < 0)

				# Check if we have nodded enough on this axis
				if len(recorded_nods[axis]) >= self.options["min_directions"]:
					# If nodded yes, show confirmation in ui
					if (axis == "y"):
						self.set_ui_text(_("Confirmed authentication"), self.UI_TEXT)
					# If shaken no, show abort message
					else:
						self.set_ui_text(_("Aborted authentication"), self.UI_TEXT)

					# Remove subtext
					self.set_ui_text("", self.UI_SUBTEXT)

					# Return true for nodding yes and false for shaking no
					time.sleep(0.8)
					return axis == "y"

				# Save the relative distance and the nosepoint for next loop
				last_reldist = reldist
				last_nosepoint[axis] = nosepoint

		# We've fallen out of the loop, so timeout has been hit
		return not self.options["failsafe"]

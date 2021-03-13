import time
import sys

from i18n import _
from rubberstamps import RubberStamp


class hotkey(RubberStamp):
	pressed_key = "none"

	def declare_config(self):
		self.options["abort_key"] = "esc"
		self.options["confirm_key"] = "enter"

	def run(self):
		time_left = self.options["timeout"]
		time_string = _("Aborting authorisation in {}") if self.options["failsafe"] else _("Authorising in {}")

		self.set_ui_text(time_string.format(int(time_left)), self.UI_TEXT)
		self.set_ui_text(_("Hold {abort_key} to abort, hold {confirm_key} to authorise").format(abort_key=self.options["abort_key"], confirm_key=self.options["confirm_key"]), self.UI_SUBTEXT)

		try:
			import keyboard
		except Exception:
			print("\nMissing module for rubber stamp keyboard!")
			print("Please run:")
			print("\t pip3 install keyboard")
			sys.exit(1)

		keyboard.add_hotkey(self.options["abort_key"], self.on_key, args=["abort"])
		keyboard.add_hotkey(self.options["confirm_key"], self.on_key, args=["confirm"])

		while time_left > 0:
			time_left -= 0.1
			self.set_ui_text(time_string.format(str(int(time_left) + 1)), self.UI_TEXT)

			if self.pressed_key == "abort":
				self.set_ui_text(_("Authentication aborted"), self.UI_TEXT)
				self.set_ui_text("", self.UI_SUBTEXT)

				time.sleep(1)
				return False

			elif self.pressed_key == "confirm":
				return True

			time.sleep(0.1)

		return not self.options["failsafe"]

	def on_key(self, type):
		self.pressed_key = type

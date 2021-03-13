import sys
import os
import re

from i18n import _

from importlib.machinery import SourceFileLoader


class RubberStamp:
	UI_TEXT = "ui_text"
	UI_SUBTEXT = "ui_subtext"

	def set_ui_text(self, text, type=None):
		typedec = "M"

		if type == self.UI_SUBTEXT:
			typedec = "S"

		return self.send_ui_raw(typedec + "=" + text)

	def send_ui_raw(self, command):
		if self.config.getboolean("debug", "verbose_stamps", fallback=False):
			print("Sending command to howdy-gtk: " + command)

		command += " \n"

		if self.gtk_proc:
			self.gtk_proc.stdin.write(bytearray(command.encode("utf-8")))
			self.gtk_proc.stdin.flush()

			# Write a padding line to force the command through any buffers
			self.gtk_proc.stdin.write(bytearray("P=_PADDING \n".encode("utf-8")))
			self.gtk_proc.stdin.flush()


def execute(config, gtk_proc, opencv):
	verbose = config.getboolean("debug", "verbose_stamps", fallback=False)
	dir_path = os.path.dirname(os.path.realpath(__file__))
	installed_stamps = []

	for filename in os.listdir(dir_path):
		if not os.path.isfile(dir_path + "/" + filename):
			continue

		if filename in ["__init__.py", ".gitignore"]:
			continue

		installed_stamps.append(filename.split(".")[0])

	if verbose: print("Installed rubberstamps: " + ", ".join(installed_stamps))

	raw_rules = config.get("rubberstamps", "stamp_rules")
	rules = raw_rules.split("\n")

	for rule in rules:
		rule = rule.strip()

		if len(rule) <= 1:
			continue

		regex_result = re.search("^(\w+)\s+([\w\.]+)\s+([a-z]+)(.*)?$", rule, re.IGNORECASE)

		if not regex_result:
			print(_("Error parsing rubberstamp rule: {}").format(rule))
			continue

		type = regex_result.group(1)

		if type not in installed_stamps:
			print(_("Stamp not installed: {}").format(type))
			continue

		module = SourceFileLoader(type, dir_path + "/" + type + ".py").load_module()

		try:
			constructor = getattr(module, type)
		except AttributeError:
			print(_("Stamp error: Class {} not found").format(type))
			continue

		instance = constructor()
		instance.verbose = verbose
		instance.config = config
		instance.gtk_proc = gtk_proc
		instance.opencv = opencv

		instance.video_capture = opencv["video_capture"]
		instance.face_detector = opencv["face_detector"]
		instance.pose_predictor = opencv["pose_predictor"]
		instance.clahe = opencv["clahe"]

		instance.options = {
			"timeout": float(re.sub("[a-zA-Z]", "", regex_result.group(2))),
			"failsafe": regex_result.group(3) != "faildeadly"
		}

		try:
			instance.declare_config()
		except Exception:
			print(_("Internal error in rubberstamp configuration declaration:"))

			import traceback
			traceback.print_exc()
			continue

		raw_options = regex_result.group(4).split()

		for option in raw_options:
			key, value = option.split("=")

			if key not in instance.options:
				print("Unknow config option for rubberstamp " + type + ": " + key)
				continue

			if isinstance(instance.options[key], int):
				value = int(value)
			elif isinstance(instance.options[key], float):
				value = float(value)

			instance.options[key] = value

		if verbose:
			print("Stamp \"" + type + "\" options parsed:")
			print(instance.options)
			print("Executing stamp")

		result = False

		try:
			result = instance.run()
		except Exception:
			print(_("Internal error in rubberstamp:"))

			import traceback
			traceback.print_exc()
			continue

		if verbose: print("Stamp \"" + type + "\" returned: " + str(result))

		if result is False:
			if verbose: print("Authentication aborted by rubber stamp")
			sys.exit(14)

	# This is outside the for loop, so we've run all the rules
	if verbose: print("All rubberstamps processed, authentication successful")

	# Exit with no errors
	sys.exit(0)

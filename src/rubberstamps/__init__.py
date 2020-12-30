import sys
import os
import re

from importlib.machinery import SourceFileLoader


class RubberStamp:
	def create_shorthands(self):
		self.video_capture = self.opencv["video_capture"]
		self.face_detector = self.opencv["face_detector"]
		self.pose_predictor = self.opencv["pose_predictor"]
		self.clahe = self.opencv["clahe"]


def execute(config, opencv):
	verbose = config.getboolean("debug", "verbose_stamps", fallback=False)
	dir_path = os.path.dirname(os.path.realpath(__file__))
	installed_stamps = []

	for filename in os.listdir(dir_path):
		if not os.path.isfile(dir_path + "/" + filename):
			continue

		if filename in ["__init__.py", ".gitignore"]:
			continue

		installed_stamps.append(filename.split(".")[0])

	if verbose:
		print("Installed rubberstamps: " + " ".join(installed_stamps))

	raw_rules = config.get("rubberstamps", "stamp_rules")
	rules = raw_rules.split("\n")

	for rule in rules:
		rule = rule.strip()

		if len(rule) <= 1:
			continue

		regex_result = re.search("^(\w+)\s+(\w+)\s+([a-z]+)(.*)?$", rule, re.IGNORECASE)

		if not regex_result:
			print("Error parsing rubberstamp rule: " + rule)
			continue

		type = regex_result.group(1)

		if type not in installed_stamps:
			print("Stamp not installed: " + type)
			continue

		module = SourceFileLoader(type, dir_path + "/" + type + ".py").load_module()
		constructor = getattr(module, type)

		instance = constructor()
		instance.config = config
		instance.opencv = opencv
		print(regex_result.group(3))

		instance.options = {
			"timeout": int(re.sub("[a-zA-Z]", "", regex_result.group(2))),
			"failsafe": regex_result.group(3) != "faildeadly"
		}

		instance.declare_config()

		raw_options = regex_result.group(4).split()

		for option in raw_options:
			key, value = option.split("=")

			if key not in instance.options:
				print("Unknow config option for rubberstamp " + type + ": " + key)
				continue

			if isinstance(instance.options[key], int):
				value = int(value)

			instance.options[key] = value

		if verbose:
			print("Stamp \"" + type + "\" options parsed:")
			print(instance.options)
			print("Executing stamp")

		instance.create_shorthands()
		result = instance.run()

		if verbose:
			print("Stamp \"" + type + "\" returned: " + str(result))

		if not result:
			sys.exit(14)

	# This is outside the for loop, so we've run all the rules
	if verbose:
		print("All rubberstamps processed, authentication successful")

	# Exit with no errors
	sys.exit(0)

import os

from importlib.machinery import SourceFileLoader


class RubberStamp:
	def create_shorthands(self):
		self.video_capture = self.opencv["video_capture"]
		self.face_detector = self.opencv["face_detector"]
		self.pose_predictor = self.opencv["pose_predictor"]
		self.clahe = self.opencv["clahe"]


def execute(config, opencv):
	dir_path = os.path.dirname(os.path.realpath(__file__))

	for filename in os.listdir(dir_path):
		if not os.path.isfile(dir_path + "/" + filename):
			continue

		if filename in ["__init__.py", ".gitignore"]:
			continue

		class_name = filename.split(".")[0]
		module = SourceFileLoader(class_name, dir_path + "/" + filename).load_module()
		constructor = getattr(module, class_name)

		instance = constructor()
		instance.config = config
		instance.opencv = opencv

		instance.create_shorthands()
		result = instance.run()

		print(result)

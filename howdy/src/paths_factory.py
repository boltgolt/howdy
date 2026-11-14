from pathlib import PurePath
import paths

models = [
    "shape_predictor_5_face_landmarks.dat",
    "mmod_human_face_detector.dat",
    "dlib_face_recognition_resnet_model_v1.dat",
]


def dlib_data_dir_path() -> str:
    return str(paths.dlib_data_dir)


def shape_predictor_5_face_landmarks_path() -> str:
    return str(paths.dlib_data_dir / models[0])


def mmod_human_face_detector_path() -> str:
    return str(paths.dlib_data_dir / models[1])


def dlib_face_recognition_resnet_model_v1_path() -> str:
    return str(paths.dlib_data_dir / models[2])


def user_model_path(user: str) -> str:
    return str(paths.user_models_dir / f"{user}.dat")


def config_file_path() -> str:
    return str(paths.config_dir / "config.ini")


def snapshots_dir_path(kind: str | None = None) -> PurePath:
	base = paths.log_path / "snapshots"

	if kind is None:
	    return base

	kind = kind.lower()

	if kind in ("failed", "fail", "failed login"):
	    return base / "failed"

	if kind in ("successful", "success", "successful login"):
	    return base / "success"

	return base / kind

def snapshot_path(snapshot: str, kind: str | None = None) -> str:
	return str(snapshots_dir_path(kind) / snapshot)


def user_models_dir_path() -> PurePath:
    return paths.user_models_dir


def logo_path() -> str:
    return str(paths.data_dir / "logo.png")

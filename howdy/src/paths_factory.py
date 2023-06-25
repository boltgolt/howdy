from pathlib import PurePath
import paths

models = [
    "shape_predictor_5_face_landmarks.dat",
    "mmod_human_face_detector.dat",
    "dlib_face_recognition_resnet_model_v1.dat",
]


def shape_predictor_5_face_landmarks_path() -> PurePath:
    return paths.dlib_data_dir / models[0]


def mmod_human_face_detector_path() -> PurePath:
    return paths.dlib_data_dir / models[1]


def dlib_face_recognition_resnet_model_v1_path() -> PurePath:
    return paths.dlib_data_dir / models[2]


def user_model_path(user: str) -> PurePath:
    return paths.user_models_dir / f"{user}.dat"


def config_file_path() -> PurePath:
    return paths.config_dir / "config.ini"


def snapshots_dir_path() -> PurePath:
    return paths.log_path / "snapshots"


def snapshot_path(snapshot: str) -> PurePath:
    return snapshots_dir_path() / snapshot

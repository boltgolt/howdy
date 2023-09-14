from pathlib import PurePath
import paths


def config_file_path() -> str:
    """Return the path to the config file"""
    return str(paths.config_dir / "config.ini")


def user_models_dir_path() -> PurePath:
    """Return the path to the user models directory"""
    return paths.user_models_dir


def logo_path() -> str:
    """Return the path to the logo file"""
    return str(paths.data_dir / "logo.png")


def onboarding_wireframe_path() -> str:
    """Return the path to the onboarding wireframe file"""
    return str(paths.data_dir / "onboarding.glade")


def main_window_wireframe_path() -> str:
    """Return the path to the main window wireframe file"""
    return str(paths.data_dir / "main.glade")


def dlib_data_dir_path() -> PurePath:
    """Return the path to the dlib data directory"""
    return paths.dlib_data_dir

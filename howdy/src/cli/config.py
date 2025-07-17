# Open the config file in an editor

# Import required modules
import os
import subprocess
import shutil
import paths_factory

from i18n import _

# Determine the editor to use
editor = None
preferred_editor = os.environ.get("EDITOR")
nano_path = shutil.which("nano")
vi_path = shutil.which("vi")

# Use the user preferred editor if available
if preferred_editor:
    if shutil.which(preferred_editor):
        editor = preferred_editor

if not editor:
    if nano_path:
        editor = nano_path
    elif vi_path:
        editor = vi_path

if editor:
    editor_name = os.path.basename(editor)

    # Let the user know what we're doing
    print(_("Opening config.ini in {editor}").format(editor=editor_name))

    # Open the editor as a subprocess and fork it
    try:
        subprocess.call([editor, paths_factory.config_file_path()])
    except Exception as e:
        print(_("Failed to open editor: {error}").format(error=e))
else:
    print(_("Error: Could not find a suitable text editor."))
    print(_("Please install 'nano' or 'vi', or set the EDITOR environment variable."))
    print(_("If you are running this command with sudo, try 'sudo -E howdy config' to preserve your EDITOR variable."))

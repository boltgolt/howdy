# Opens auth ui if requested, otherwise starts normal ui
import sys

from gi.repository import GLib as glib

# Identify as howdy-gtk instead of init.py, so desktops can match our windows to the desktop entry
glib.set_prgname("howdy-gtk")

if "--start-auth-ui" in sys.argv:
	import authsticky
else:
	import window

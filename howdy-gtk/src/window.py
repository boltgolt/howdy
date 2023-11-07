# Opens and controls main ui window
import gi
import signal
import sys
import os
import elevate
import subprocess

from i18n import _
import paths_factory

# Make sure we have the libs we need
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")

# Import them
from gi.repository import Gtk as gtk


class MainWindow(gtk.Window):
	def __init__(self):
		"""Initialize the sticky window"""
		# Make the class a GTK window
		gtk.Window.__init__(self)

		self.builder = gtk.Builder()
		self.builder.add_from_file(paths_factory.main_window_wireframe_path())
		self.builder.connect_signals(self)

		self.window = self.builder.get_object("mainwindow")
		self.userlist = self.builder.get_object("userlist")
		self.modellistbox = self.builder.get_object("modellistbox")
		self.opencvimage = self.builder.get_object("opencvimage")

		self.window.connect("destroy", self.exit)
		self.window.connect("delete_event", self.exit)

		# Init capture for video tab
		self.capture = None

		# Create a treeview that will list the model data
		self.treeview = gtk.TreeView()
		self.treeview.set_vexpand(True)

		# Set the columns
		for i, column in enumerate([_("ID"), _("Created"), _("Label")]):
			col = gtk.TreeViewColumn(column, gtk.CellRendererText(), text=i)
			self.treeview.append_column(col)

		# Add the treeview
		self.modellistbox.add(self.treeview)

		filelist = os.listdir(paths_factory.user_models_dir_path())
		self.active_user = ""

		self.userlist.items = 0

		for file in filelist:
			self.userlist.append_text(file[:-4])
			self.userlist.items += 1

			if not self.active_user:
				self.active_user = file[:-4]

		self.userlist.set_active(0)

		self.window.show_all()

		# Start GTK main loop
		gtk.main()

	def load_model_list(self):
		"""(Re)load the model list"""

		# Get username and default to none if there are no models at all yet
		user = 'none'
		if self.active_user: user = self.active_user

		# Execute the list command to get the models
		status, output = subprocess.getstatusoutput(["howdy list --plain -U " + user])

		# Create a datamodel
		self.listmodel = gtk.ListStore(str, str, str)

		# If there was no error
		if status == 0:
			# Split the output per line
			lines = output.split("\n")

			# Add the models to the datamodel
			for i in range(len(lines)):
				items = lines[i].split(",")
				if len(items) < 3: continue
				self.listmodel.append(items)

		self.treeview.set_model(self.listmodel)

	def on_about_link(self, label, uri):
		"""Open links on about page as a non-root user"""
		try:
			user = os.getlogin()
		except Exception:
			user = os.environ.get("SUDO_USER")

		status, output = subprocess.getstatusoutput(["sudo -u " + user + " timeout 10 xdg-open " + uri])
		return True

	def exit(self, widget=None, context=None):
		"""Cleanly exit"""
		if self.capture is not None:
			self.capture.release()

		gtk.main_quit()
		sys.exit(0)


# Make sure we quit on a SIGINT
signal.signal(signal.SIGINT, signal.SIG_DFL)

# Make sure we run as sudo
elevate.elevate()

# If no models have been created yet or when it is forced, start the onboarding
if "--force-onboarding" in sys.argv or not os.path.exists(paths_factory.user_models_dir_path()):
	import onboarding
	onboarding.OnboardingWindow()

	sys.exit(0)

# Class is split so it isn't too long, import split functions
import tab_models
MainWindow.on_user_add = tab_models.on_user_add
MainWindow.on_user_change = tab_models.on_user_change
MainWindow.on_model_add = tab_models.on_model_add
MainWindow.on_model_delete = tab_models.on_model_delete
import tab_video
MainWindow.on_page_switch = tab_video.on_page_switch
MainWindow.capture_frame = tab_video.capture_frame

# Open the GTK window
window = MainWindow()

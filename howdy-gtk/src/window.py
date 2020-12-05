# Opens and controls main ui window
import cairo
import gi
import signal
import sys
import os
import subprocess

# Make sure we have the libs we need
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")

# Import them
from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk


class MainWindow(gtk.Window):
	def __init__(self):
		"""Initialize the sticky window"""
		# Make the class a GTK window
		gtk.Window.__init__(self)

		self.connect("destroy", self.exit)

		self.builder = gtk.Builder()
		self.builder.add_from_file("./ui.glade")
		self.builder.connect_signals(self)

		self.window = self.builder.get_object("mainwindow")
		self.userlist = self.builder.get_object("userlist")
		self.modellistbox = self.builder.get_object("modellistbox")

		filelist = os.listdir("/lib/security/howdy/models")
		self.active_user = ""

		for file in filelist:
			self.userlist.append_text(file[:-4])

			if not self.active_user:
				self.active_user = file[:-4]

		self.userlist.set_active(0)

		self.load_model_list()

		self.window.show_all()
		# self.resize(300, 300)

		# Start GTK main loop
		gtk.main()

	def load_model_list(self):
		output = subprocess.check_output(["howdy", "list", "-U", self.active_user])

		lines = output.decode("utf-8") .split("\n")[3:-2]
		print(lines)

		newrow = self.builder.get_object("modelrow")

		print(newrow.set_name("wat"))

		self.modellistbox.add(newrow)
		newrow2 = self.builder.get_object("modelrow")

		# print(newrow.get_object("modelrowname"))

		self.modellistbox.add(newrow2)

	def exit(self, widget, context):
		"""Cleanly exit"""
		gtk.main_quit()
		sys.exit()


# Make sure we quit on a SIGINT
signal.signal(signal.SIGINT, signal.SIG_DFL)

# Open the GTK window
window = MainWindow()

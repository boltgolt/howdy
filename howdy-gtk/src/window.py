# Opens and controls main ui window
import cairo
import gi
import signal
import sys
import os
import subprocess
import elevate

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

		# Create a treeview that will list the model data
		self.treeview = gtk.TreeView()

		# Set the coloums
		for i, column in enumerate(["ID", "Created", "Label"]):
			cell = gtk.CellRendererText()
			col = gtk.TreeViewColumn(column, cell, text=i)

			self.treeview.append_column(col)

		# Add the treeview
		self.modellistbox.add(self.treeview)

		filelist = os.listdir("/lib/security/howdy/models")
		self.active_user = ""

		for file in filelist:
			self.userlist.append_text(file[:-4])

			if not self.active_user:
				self.active_user = file[:-4]

		self.userlist.set_active(0)

		self.window.show_all()
		# self.resize(300, 300)

		# Start GTK main loop
		gtk.main()

	def load_model_list(self):
		"""(Re)load the model list"""

		# Execute the list commond to get the models
		output = subprocess.check_output(["howdy", "list", "--plain", "-U", self.active_user])

		# Split the output per line
		# lines = output.decode("utf-8").split("\n")
		lines = output.split("\n")

		# Create a datamodel
		self.listmodel = gtk.ListStore(str, str, str)

		# Add the models to the datamodel
		for i in range(len(lines)):
			self.listmodel.append(lines[i].split(","))

		self.treeview.set_model(self.listmodel)

	def on_user_change(self, select):
		self.active_user = select.get_active_text()
		self.load_model_list()

	def on_model_add(self, select):
		dialog = gtk.MessageDialog(parent=self, flags=gtk.DialogFlags.MODAL, type=gtk.MessageType.QUESTION, buttons=gtk.ButtonsType.OK_CANCEL)
		dialog.props.text = "Please enter a name for the new model, 24 characters max"
		dialog.set_title("Confirm Model Creation")
		# create the text input field
		entry = gtk.Entry()
		# create a horizontal box to pack the entry and a label
		hbox = gtk.HBox()
		hbox.pack_start(gtk.Label("Model name:"), False, 5, 5)
		hbox.pack_end(entry, True, True, 5)
		# some secondary text
		# add it and show it
		dialog.vbox.pack_end(hbox, True, True, 0)
		dialog.show_all()
		# go go go
		response = dialog.run()

		text = entry.get_text()
		dialog.destroy()

		if response == gtk.ResponseType.OK:
			dialog = gtk.MessageDialog(parent=self, flags=gtk.DialogFlags.MODAL)
			dialog.props.text = "Please look directly into the camera"
			dialog.set_title("Creating Model")
			dialog.show_all()

			status, output = subprocess.getstatusoutput(["howdy add -y -U " + self.active_user])

			dialog.destroy()

			if status != 1:
				dialog = gtk.MessageDialog(parent=self, flags=gtk.DialogFlags.MODAL, type=gtk.MessageType.ERROR, buttons=gtk.ButtonsType.CLOSE)
				dialog.props.text = "Error while adding model, error code " + str(status) + ": \n\n"
				dialog.format_secondary_text(output)
				dialog.set_title("Howdy Error")
				dialog.run()
				dialog.destroy()

			self.load_model_list()

	def on_model_delete(self, select):
		selection = self.treeview.get_selection()
		(listmodel, rowlist) = selection.get_selected_rows()

		if len(rowlist) == 1:
			id = listmodel.get_value(listmodel.get_iter(rowlist[0]), 0)
			name = listmodel.get_value(listmodel.get_iter(rowlist[0]), 2)

			dialog = gtk.MessageDialog(parent=self, flags=gtk.DialogFlags.MODAL, buttons=gtk.ButtonsType.OK_CANCEL)
			dialog.props.text = "Are you sure you want to delete model " + id + " (" + name + ")?"
			dialog.set_title("Confirm Model Deletion")
			response = dialog.run()
			dialog.destroy()

			if response == gtk.ResponseType.OK:
				status, output = subprocess.getstatusoutput(["howdy remove " + id + " -y -U " + self.active_user])

				if status != 0:
					dialog = gtk.MessageDialog(parent=self, flags=gtk.DialogFlags.MODAL, type=gtk.MessageType.ERROR, buttons=gtk.ButtonsType.CLOSE)
					dialog.props.text = "Error while deleting model, error code " + str(status) + ": \n\n"
					dialog.format_secondary_text(output)
					dialog.set_title("Howdy Error")
					dialog.run()
					dialog.destroy()

				self.load_model_list()

	def exit(self, widget, context):
		"""Cleanly exit"""
		gtk.main_quit()
		sys.exit()


# Make sure we quit on a SIGINT
signal.signal(signal.SIGINT, signal.SIG_DFL)

# Make sure we run as sudo
elevate.elevate()

# Open the GTK window
window = MainWindow()

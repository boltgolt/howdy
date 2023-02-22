import subprocess
import time

from i18n import _
from gi.repository import Gtk as gtk


def on_user_change(self, select):
	self.active_user = select.get_active_text()
	self.load_model_list()


def on_user_add(self, button):
	# Open question dialog
	dialog = gtk.MessageDialog(parent=self, flags=gtk.DialogFlags.MODAL, type=gtk.MessageType.QUESTION, buttons=gtk.ButtonsType.OK_CANCEL)
	dialog.set_title(_("Confirm User Creation"))
	dialog.props.text = _("Please enter the username of the user you want to add to Howdy")

	# Create the input field
	entry = gtk.Entry()

	# Add a label to ask for a model name
	hbox = gtk.HBox()
	hbox.pack_start(gtk.Label(_("Username:")), False, 5, 5)
	hbox.pack_end(entry, True, True, 5)

	# Add the box and show the dialog
	dialog.vbox.pack_end(hbox, True, True, 0)
	dialog.show_all()

	# Show dialog
	response = dialog.run()

	entered_user = entry.get_text()
	dialog.destroy()

	if response == gtk.ResponseType.OK:
		self.userlist.append_text(entered_user)
		self.userlist.set_active(self.userlist.items)
		self.userlist.items += 1

		self.active_user = entered_user
		self.load_model_list()


def on_model_add(self, button):
	# Open question dialog
	dialog = gtk.MessageDialog(parent=self, flags=gtk.DialogFlags.MODAL, type=gtk.MessageType.QUESTION, buttons=gtk.ButtonsType.OK_CANCEL)
	dialog.set_title(_("Confirm Model Creation"))
	dialog.props.text = _("Please enter a name for the new model, 24 characters max")

	# Create the input field
	entry = gtk.Entry()

	# Add a label to ask for a model name
	hbox = gtk.HBox()
	hbox.pack_start(gtk.Label(_("Model name:")), False, 5, 5)
	hbox.pack_end(entry, True, True, 5)

	# Add the box and show the dialog
	dialog.vbox.pack_end(hbox, True, True, 0)
	dialog.show_all()

	# Show dialog
	response = dialog.run()

	entered_name = entry.get_text()
	dialog.destroy()

	if response == gtk.ResponseType.OK:
		dialog = gtk.MessageDialog(parent=self, flags=gtk.DialogFlags.MODAL, buttons=gtk.ButtonsType.NONE)
		dialog.set_title(_("Creating Model"))
		dialog.props.text = _("Please look directly into the camera")
		dialog.get_child().connect("map", lambda w: execute_add(self, dialog, entered_name, self.active_user))
		dialog.show_all()


def execute_add(box, dialog, entered_name, user):

	time.sleep(1)

	status, output = subprocess.getstatusoutput(["howdy add '" + entered_name + "' -y -U " + box.active_user])

	dialog.destroy()

	if status != 0:
		dialog = gtk.MessageDialog(parent=box, flags=gtk.DialogFlags.MODAL, type=gtk.MessageType.ERROR, buttons=gtk.ButtonsType.CLOSE)
		dialog.set_title(_("Howdy Error"))
		dialog.props.text = _("Error while adding model, error code {}: \n\n").format(str(status))
		dialog.format_secondary_text(output)
		dialog.run()
		dialog.destroy()

	box.load_model_list()

def on_model_delete(self, button):
	selection = self.treeview.get_selection()
	(listmodel, rowlist) = selection.get_selected_rows()

	if len(rowlist) == 1:
		id = listmodel.get_value(listmodel.get_iter(rowlist[0]), 0)
		name = listmodel.get_value(listmodel.get_iter(rowlist[0]), 2)

		dialog = gtk.MessageDialog(parent=self, flags=gtk.DialogFlags.MODAL, buttons=gtk.ButtonsType.OK_CANCEL)
		dialog.set_title(_("Confirm Model Deletion"))
		dialog.props.text = _("Are you sure you want to delete model {id} ({name})?").format(id=id, name=name)
		response = dialog.run()
		dialog.destroy()

		if response == gtk.ResponseType.OK:
			status, output = subprocess.getstatusoutput(["howdy remove " + id + " -y -U " + self.active_user])

			if status != 0:
				dialog = gtk.MessageDialog(parent=self, flags=gtk.DialogFlags.MODAL, type=gtk.MessageType.ERROR, buttons=gtk.ButtonsType.CLOSE)
				dialog.set_title(_("Howdy Error"))
				dialog.props.text = _("Error while deleting model, error code {}: \n\n").format(status)
				dialog.format_secondary_text(output)
				dialog.run()
				dialog.destroy()

			self.load_model_list()

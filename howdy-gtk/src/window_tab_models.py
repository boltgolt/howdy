import subprocess

from gi.repository import Gtk as gtk


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

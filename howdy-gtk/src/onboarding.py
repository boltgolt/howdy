import sys
import os
import re
import time
import subprocess
import paths_factory

from i18n import _

from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk
from gi.repository import GObject as gobject
from gi.repository import Pango as pango


class OnboardingWindow(gtk.Window):
	def __init__(self):
		"""Initialize the sticky window"""
		# Make the class a GTK window
		gtk.Window.__init__(self)

		self.connect("destroy", self.exit)
		self.connect("delete_event", self.exit)

		self.builder = gtk.Builder()
		self.builder.add_from_file(paths_factory.onboarding_wireframe_path())
		self.builder.connect_signals(self)

		self.window = self.builder.get_object("onboardingwindow")
		self.slidecontainer = self.builder.get_object("slidecontainer")
		self.nextbutton = self.builder.get_object("nextbutton")

		self.slides = [
			self.builder.get_object("slide0"),
			self.builder.get_object("slide1"),
			self.builder.get_object("slide2"),
			self.builder.get_object("slide3"),
			self.builder.get_object("slide4"),
			self.builder.get_object("slide5"),
			self.builder.get_object("slide6")
		]

		self.window.show_all()
		self.window.resize(500, 400)

		self.window.current_slide = 0

		# Start GTK main loop
		gtk.main()

	def go_next_slide(self, button=None):
		self.nextbutton.set_sensitive(False)

		self.slides[self.window.current_slide].hide()
		self.slides[self.window.current_slide + 1].show()
		self.window.current_slide += 1
		# the shown child may have zero/wrong dimensions
		self.slidecontainer.queue_resize()

		if self.window.current_slide == 1:
			self.execute_slide1()
		elif self.window.current_slide == 2:
			gobject.timeout_add(10, self.execute_slide2)
		elif self.window.current_slide == 3:
			self.execute_slide3()
		elif self.window.current_slide == 4:
			self.execute_slide4()
		elif self.window.current_slide == 5:
			self.execute_slide5()
		elif self.window.current_slide == 6:
			self.execute_slide6()

	def execute_slide1(self):
		self.downloadoutputlabel = self.builder.get_object("downloadoutputlabel")
		eventbox = self.builder.get_object("downloadeventbox")
		eventbox.modify_bg(gtk.StateType.NORMAL, gdk.Color(red=0, green=0, blue=0))

		# TODO: Better way to do this?
		if os.path.exists(paths_factory.dlib_data_dir_path() / "shape_predictor_5_face_landmarks.dat"):
			self.downloadoutputlabel.set_text(_("Datafiles have already been downloaded!\nClick Next to continue"))
			self.enable_next()
			return

		self.proc = subprocess.Popen("./install.sh", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, cwd=paths_factory.dlib_data_dir_path())

		self.download_lines = []
		self.read_download_line()

	def read_download_line(self):
		line = self.proc.stdout.readline()
		self.download_lines.append(line.decode("utf-8"))

		print("install.sh output:")
		print(line.decode("utf-8"))

		if len(self.download_lines) > 10:
			self.download_lines.pop(0)

		self.downloadoutputlabel.set_text(" ".join(self.download_lines))

		if line:
			gobject.timeout_add(10, self.read_download_line)
			return

		# Wait for the process to finish and check the status code
		if self.proc.wait(5) != 0:
			self.show_error(_("Error while downloading datafiles"), " ".join(self.download_lines))

		self.downloadoutputlabel.set_text(_("Done!\nClick Next to continue"))
		self.enable_next()

	def execute_slide2(self):
		def is_gray(frame):
			for row in frame:
				for pixel in row:
					if not pixel[0] == pixel[1] == pixel[2]:
						return False
			return True

		try:
			import cv2
		except Exception:
			self.show_error(_("Error while importing OpenCV2"), _("Try reinstalling cv2"))

		device_ids = os.listdir("/dev/v4l/by-path")
		device_rows = []

		if not device_ids:
			self.show_error(_("No webcams found on system"), _("Please configure your camera yourself if you are sure a compatible camera is connected"))

		# Loop though all devices
		for dev in device_ids:
			time.sleep(.5)

			# The full path to the device is the default name
			device_path = "/dev/v4l/by-path/" + dev
			device_name = dev

			# Get the udevadm details to try to get a better name
			udevadm = subprocess.check_output(["udevadm info -r --query=all -n " + device_path], shell=True).decode("utf-8")

			# Loop though udevadm to search for a better name
			for line in udevadm.split("\n"):
				# Match it and encase it in quotes
				re_name = re.search('product.*=(.*)$', line, re.IGNORECASE)
				if re_name:
					device_name = re_name.group(1)

			capture = cv2.VideoCapture(device_path)
			is_open, frame = capture.read()
			if not is_open:
				device_rows.append([device_name, device_path, -9, _("No, camera can't be opened")])
				continue

			try:
				if not is_gray(frame):
					raise Exception()
			except Exception:
				device_rows.append([device_name, device_path, -5, _("No, not an infrared camera")])
				capture.release()
				continue

			device_rows.append([device_name, device_path, 5, _("Yes, compatible infrared camera")])
			capture.release()

		device_rows = sorted(device_rows, key=lambda k: -k[2])

		self.loadinglabel = self.builder.get_object("loadinglabel")
		self.devicelistbox = self.builder.get_object("devicelistbox")

		self.treeview = gtk.TreeView()
		self.treeview.set_vexpand(True)

		# Set the columns
		for i, column in enumerate([_("Camera identifier or path"), _("Recommended")]):
			cell = gtk.CellRendererText()
			cell.set_property("ellipsize", pango.EllipsizeMode.END)
			col = gtk.TreeViewColumn(column, cell, text=i)
			self.treeview.append_column(col)

		# Add the treeview
		self.devicelistbox.add(self.treeview)

		# Create a datamodel
		self.listmodel = gtk.ListStore(str, str, str, bool)

		for device in device_rows:
			is_gray = device[2] == 5
			self.listmodel.append([device[0], device[3], device[1], is_gray])

		self.treeview.set_model(self.listmodel)
		self.treeview.set_cursor(0)

		self.treeview.show()
		self.loadinglabel.hide()
		self.enable_next()

	def execute_slide3(self):
		try:
			import cv2
		except Exception:
			self.show_error(_("Error while importing OpenCV2"), _("Try reinstalling cv2"))

		selection = self.treeview.get_selection()
		(listmodel, rowlist) = selection.get_selected_rows()
		
		if len(rowlist) != 1:
			self.show_error(_("Error selecting camera"))
   
		device_path = listmodel.get_value(listmodel.get_iter(rowlist[0]), 2)
		is_gray = listmodel.get_value(listmodel.get_iter(rowlist[0]), 3)

		if is_gray:
			# test if linux-enable-ir-emitter help should be displayed, 
			# the user must click on the yes/no button which calls the method slide3_button_yes|no
			self.capture = cv2.VideoCapture(device_path)
			if not self.capture.isOpened():
				self.show_error(_("The selected camera cannot be opened"), _("Try to select another one"))
			self.capture.read()
		else:  
			# skip, the selected camera is not infrared
			self.go_next_slide()

	def slide3_button_yes(self, button):
		self.capture.release()
		self.go_next_slide()

	def slide3_button_no(self, button):
		self.capture.release()
		self.builder.get_object("leiestatus").set_markup(_("Please visit\n<a href=\"https://github.com/EmixamPP/linux-enable-ir-emitter\">https://github.com/EmixamPP/linux-enable-ir-emitter</a>\nto enable your ir emitter"))
		self.builder.get_object("leieyesbutton").hide()
		self.builder.get_object("leienobutton").hide()

	def execute_slide4(self):
		selection = self.treeview.get_selection()
		(listmodel, rowlist) = selection.get_selected_rows()

		if len(rowlist) != 1:
			self.show_error(_("Error selecting camera"))

		device_path = listmodel.get_value(listmodel.get_iter(rowlist[0]), 2)
		self.proc = subprocess.Popen("howdy set device_path " + device_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

		self.window.set_focus(self.builder.get_object("scanbutton"))

	def on_scanbutton_click(self, button):
		status = self.proc.wait(2)

		# if status != 0:
		# 	self.show_error(_("Error setting camera path"), _("Please set the camera path manually"))

		self.dialog = gtk.MessageDialog(parent=self, flags=gtk.DialogFlags.MODAL)
		self.dialog.set_title(_("Creating Model"))
		self.dialog.props.text = _("Please look directly into the camera")
		self.dialog.show_all()

		# Wait a bit to allow the user to read the dialog
		gobject.timeout_add(600, self.run_add)

	def run_add(self):
		status, output = subprocess.getstatusoutput(["howdy add -y"])

		print("howdy add output:")
		print(output)

		self.dialog.destroy()

		if status != 0:
			self.show_error(_("Can't save face model"), output)

		gobject.timeout_add(10, self.go_next_slide)

	def execute_slide5(self):
		self.enable_next()

	def execute_slide6(self):
		radio_buttons = self.builder.get_object("radiobalanced").get_group()
		radio_selected = False
		radio_certanty = 5.0

		for button in radio_buttons:
			if button.get_active():
				radio_selected = gtk.Buildable.get_name(button)

		if not radio_selected:
			self.show_error(_("Error reading radio buttons"))
		elif radio_selected == "radiofast":
			radio_certanty = 4.2
		elif radio_selected == "radiobalanced":
			radio_certanty = 3.5
		elif radio_selected == "radiosecure":
			radio_certanty = 2.2

		self.proc = subprocess.Popen("howdy set certainty " + str(radio_certanty), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

		self.nextbutton.hide()
		self.builder.get_object("cancelbutton").hide()

		finishbutton = self.builder.get_object("finishbutton")
		finishbutton.show()
		self.window.set_focus(finishbutton)

		status = self.proc.wait(2)

		if status != 0:
			self.show_error(_("Error setting certainty"), _("Certainty is set to the default value, Howdy setup is complete"))

	def enable_next(self):
		self.nextbutton.set_sensitive(True)
		self.window.set_focus(self.nextbutton)

	def show_error(self, error, secon=""):
		dialog = gtk.MessageDialog(parent=self, flags=gtk.DialogFlags.MODAL, type=gtk.MessageType.ERROR, buttons=gtk.ButtonsType.CLOSE)
		dialog.set_title(_("Howdy Error"))
		dialog.props.text = error
		dialog.format_secondary_text(secon)

		dialog.run()

		dialog.destroy()
		self.exit()

	def exit(self, widget=None):
		"""Cleanly exit"""
		gtk.main_quit()
		sys.exit(0)

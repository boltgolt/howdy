# Shows a floating window when authenticating
import cairo
import gi
import signal
import sys
import os

# Make sure we have the libs we need
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")

# Import them
from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk
from gi.repository import GObject as gobject

# Set window size constants
windowWidth = 400
windowHeight = 100

# Set default messages to show in the popup
message = "Starting up...  "
subtext = ""


class StickyWindow(gtk.Window):
	def __init__(self):
		"""Initialize the sticky window"""
		# Make the class a GTK window
		gtk.Window.__init__(self)

		# Set the title of the window
		self.set_title("Howdy Authentication UI")

		# Set a bunch of options to make the window stick and be on top of everything
		self.stick()
		self.set_gravity(gdk.Gravity.STATIC)
		self.set_resizable(False)
		self.set_keep_above(True)
		self.set_app_paintable(True)
		self.set_skip_pager_hint(True)
		self.set_skip_taskbar_hint(True)
		self.set_can_focus(False)
		self.set_can_default(False)
		self.set_focus(None)
		self.set_type_hint(gdk.WindowTypeHint.NOTIFICATION)
		self.set_decorated(False)

		# Listen for a window redraw
		self.connect("draw", self.draw)
		# Listen for a force close or click event and exit
		self.connect("destroy", self.exit)
		self.connect("delete_event", self.exit)
		self.connect("button-press-event", self.exit)

		# Create a GDK drawing, restricts the window size
		darea = gtk.DrawingArea()
		darea.set_size_request(windowWidth, windowHeight)
		self.add(darea)

		# Get the default screen
		screen = gdk.Screen.get_default()
		visual = screen.get_rgba_visual()
		if visual and screen.is_composited():
			self.set_visual(visual)

		# Move the window to the center top of the default window, where a webcam usually is
		self.move((screen.get_width() / 2) - (windowWidth / 2), 0)

		# Show window and force a resize again
		self.show_all()
		self.resize(windowWidth, windowHeight)

		# Add a timeout to catch input passed from compare.py
		gobject.timeout_add(100, self.catch_stdin)

		# Start GTK main loop
		gtk.main()

	def draw(self, widget, ctx):
		"""Draw the UI"""
		# Change cursor to the kill icon
		self.get_window().set_cursor(gdk.Cursor(gdk.CursorType.PIRATE))

		# Draw a semi transparent background
		ctx.set_source_rgba(0, 0, 0, .7)
		ctx.set_operator(cairo.OPERATOR_SOURCE)
		ctx.paint()
		ctx.set_operator(cairo.OPERATOR_OVER)

		# Get absolute or relative logo path
		path = "/usr/lib/howdy-gtk/logo.png"
		if not os.access(path, os.R_OK):
			path = "./logo.png"

		# Create image and calculate scale size based on image size
		image_surface = cairo.ImageSurface.create_from_png(path)
		ratio = float(windowHeight - 20) / float(image_surface.get_height())

		# Position and draw the logo
		ctx.translate(15, 10)
		ctx.scale(ratio, ratio)
		ctx.set_source_surface(image_surface)
		ctx.paint()

		# Calculate main message positioning, as the text is heigher if there's a subtext
		if subtext:
			ctx.move_to(380, 145)
		else:
			ctx.move_to(380, 170)

		# Draw the main message
		ctx.set_source_rgba(255, 255, 255, .9)
		ctx.set_font_size(80)
		ctx.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
		ctx.show_text(message)

		# Draw the subtext if there is one
		if subtext:
			ctx.move_to(380, 210)
			ctx.set_source_rgba(230, 230, 230, .8)
			ctx.set_font_size(40)
			ctx.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
			ctx.show_text(subtext)

	def catch_stdin(self):
		"""Catch input from stdin and redraw"""
		global message, subtext

		# Wait for a line on stdin
		comm = sys.stdin.readline()[:-1]

		# If the line is not empty
		if comm:
			# Parse a message
			if comm[0] == "M":
				message = comm[2:].strip()
			# Parse subtext
			if comm[0] == "S":
				subtext = comm[2:].strip()

			# Redraw the ui
			self.queue_draw()

		# Fire this function again in 10ms, as we're waiting on IO in readline anyway
		gobject.timeout_add(10, self.catch_stdin)

	def exit(self, widget, context):
		"""Cleanly exit"""
		gtk.main_quit()


# Make sure we quit on a SIGINT
signal.signal(signal.SIGINT, signal.SIG_DFL)

# Open the GTK window
window = StickyWindow()

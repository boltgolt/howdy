#!/usr/bin/env python3

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

message = "Starting up...  "
subtext = ""


class StickyWindow(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)

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

        # Draw
        self.connect("draw", self.draw)
        self.connect("destroy", self.exit)
        self.connect("button-press-event", self.exit)

        darea = gtk.DrawingArea()
        darea.set_size_request(windowWidth, windowHeight)
        self.add(darea)

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)

        # TODO: handle more than 1 screen
        self.move((screen.get_width() / 2) - (windowWidth / 2), 0)

        self.show_all()
        self.resize(windowWidth, windowHeight)

        gobject.timeout_add(100, self.test)

        gtk.main()

    def draw(self, widget, ctx):
        # Change cursor to the kill icon
        self.get_window().set_cursor(gdk.Cursor(gdk.CursorType.PIRATE))

        ctx.set_source_rgba(0, 0, 0, .9)
        ctx.set_operator(cairo.OPERATOR_SOURCE)
        ctx.paint()
        ctx.set_operator(cairo.OPERATOR_OVER)

        dir = os.path.dirname(os.path.abspath(__file__))

        image_surface = cairo.ImageSurface.create_from_png("/usr/lib/howdy-gtk/logo.png")
        ratio = float(windowHeight - 20) / float(image_surface.get_height())

        ctx.translate(15, 10)
        ctx.scale(ratio, ratio)
        ctx.set_source_surface(image_surface)
        ctx.paint()

        ctx.set_source_rgba(255, 255, 255, .9)
        ctx.set_font_size(80)

        if subtext:
            ctx.move_to(380, 145)
        else:
            ctx.move_to(380, 170)

        ctx.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.show_text(message)

        ctx.set_source_rgba(230, 230, 230, .8)
        ctx.set_font_size(40)
        ctx.move_to(380, 210)
        ctx.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.show_text(subtext)

    def exit(self, widget, context):
        gtk.main_quit()

    def test(self):
        global message, subtext

        comm = sys.stdin.readline()[:-1]

        if comm:
            if comm[0] == "M":
                message = comm[2:]
            if comm[0] == "S":
                subtext = comm[2:]

        self.queue_draw()
        gobject.timeout_add(100, self.test)


signal.signal(signal.SIGINT, signal.SIG_DFL)

window = StickyWindow()

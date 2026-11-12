import configparser
import subprocess

from i18n import _
import paths_factory

from gi.repository import Gtk as gtk


def load_settings(self):
	"""Fill the settings tab with the values from the config file"""
	config = configparser.ConfigParser()
	config.read(paths_factory.config_file_path())

	# Setting the widgets triggers the changed handler, ignore it while loading
	self.settings_loading = True

	# Fallbacks are the same as the ones used in compare.py
	self.builder.get_object("settingsenabled").set_active(not config.getboolean("core", "disabled", fallback=False))
	self.builder.get_object("settingscertainty").set_value(config.getfloat("video", "certainty", fallback=3.5))
	self.builder.get_object("settingstimeout").set_value(config.getint("video", "timeout", fallback=4))
	self.builder.get_object("settingsdarkthreshold").set_value(config.getfloat("video", "dark_threshold", fallback=60))
	self.builder.get_object("settingsabortssh").set_active(config.getboolean("core", "abort_if_ssh", fallback=True))
	self.builder.get_object("settingsabortlid").set_active(config.getboolean("core", "abort_if_lid_closed", fallback=True))

	self.settings_loading = False

	# Nothing to save until something has been changed
	self.builder.get_object("settingssave").set_sensitive(False)


def on_settings_changed(self, widget, *args):
	"""Allow saving once a setting has been changed"""
	if not self.settings_loading:
		self.builder.get_object("settingssave").set_sensitive(True)


def on_settings_save(self, button):
	"""Write the settings to the config file through the howdy cli"""
	settings = {
		# The switch enables Howdy, the config option disables it
		"disabled": "false" if self.builder.get_object("settingsenabled").get_active() else "true",
		"certainty": str(round(self.builder.get_object("settingscertainty").get_value(), 1)),
		"timeout": str(int(self.builder.get_object("settingstimeout").get_value())),
		"dark_threshold": str(int(self.builder.get_object("settingsdarkthreshold").get_value())),
		"abort_if_ssh": "true" if self.builder.get_object("settingsabortssh").get_active() else "false",
		"abort_if_lid_closed": "true" if self.builder.get_object("settingsabortlid").get_active() else "false"
	}

	for name, value in settings.items():
		status, output = subprocess.getstatusoutput(["howdy set " + name + " " + value])

		if status != 0:
			dialog = gtk.MessageDialog(transient_for=self, modal=True, message_type=gtk.MessageType.ERROR, buttons=gtk.ButtonsType.CLOSE)
			dialog.set_title(_("Howdy Error"))
			dialog.props.text = _("Error while saving setting {}, error code {}: \n\n").format(name, str(status))
			dialog.format_secondary_text(output)
			dialog.run()
			dialog.destroy()
			break

	# Reload so the tab shows what has actually been saved
	self.load_settings()

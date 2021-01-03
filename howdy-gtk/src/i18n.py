# Support file for translations

# Import modules
import gettext
import os

# Get the right translation based on locale, falling back to base if none found
translation = gettext.translation("gtk", localedir=os.path.join(os.path.dirname(__file__), "locales"), fallback=True)
translation.install()

# Export translation function as _
_ = translation.gettext

# PAM interface in python, launches compare.py

import glob
import os
# Import required modules
import subprocess
import syslog

# pam-python is running python 2, so we use the old module here
try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser  # compatible for future

# Read config from disk
config = ConfigParser.ConfigParser()
config.read(os.path.dirname(os.path.abspath(__file__)) + "/config.ini")


def on_face_not_found(pam_context):
    if not config.getboolean("core", "suppress_unknown"):
        pam_context.conversation(pam_context.Message(pam_context.PAM_ERROR_MSG, "No face model known"))

    syslog.syslog(syslog.LOG_NOTICE, "Failure, no face model known")
    syslog.closelog()
    return pam_context.PAM_USER_UNKNOWN


def on_timeout(pam_context):
    pam_context.conversation(pam_context.Message(pam_context.PAM_ERROR_MSG, "Face detection timeout reached"))
    syslog.syslog(syslog.LOG_INFO, "Failure, timeout reached")
    syslog.closelog()
    return pam_context.PAM_AUTH_ERR


def on_abort(pam_context):
    syslog.syslog(syslog.LOG_INFO, "Failure, general abort")
    syslog.closelog()
    return pam_context.PAM_AUTH_ERR


def on_env_too_dark(pam_context):
    syslog.syslog(syslog.LOG_INFO, "Failure, image too dark")
    syslog.closelog()
    pam_context.conversation(pam_context.Message(pam_context.PAM_ERROR_MSG, "Face detection image too dark"))
    return pam_context.PAM_AUTH_ERR


def on_success(pam_context):
    # Show the success message if it isn't suppressed
    if not config.getboolean("core", "no_confirmation"):
        pam_context.conversation(
            pam_context.Message(pam_context.PAM_TEXT_INFO, "Identified face as " + pam_context.get_user()))

    syslog.syslog(syslog.LOG_INFO, "Login approved")
    syslog.closelog()
    return pam_context.PAM_SUCCESS


def on_device_not_found(pam_context):
    pam_context.conversation(pam_context.Message(pam_context.PAM_ERROR_MSG, "Camera not found"))
    return pam_context.PAM_SYSTEM_ERR


def on_unknown(pam_context, status):
    pam_context.conversation(pam_context.Message(pam_context.PAM_ERROR_MSG, "Unknown error: " + str(status)))
    syslog.syslog(syslog.LOG_INFO, "Failure, unknown error" + str(status))
    syslog.closelog()
    return pam_context.PAM_SYSTEM_ERR


method_mapper = {
    0: on_success,
    10: on_face_not_found,
    11: on_timeout,
    12: on_abort,
    13: on_env_too_dark,
    14: on_device_not_found
}


def doAuth(pam_context):
    """Starts authentication in a seperate process"""

    # Abort is Howdy is disabled
    if config.getboolean("core", "disabled"):
        return pam_context.PAM_AUTHINFO_UNAVAIL

    # Abort if we're in a remote SSH env
    if config.getboolean("core", "ignore_ssh"):
        if "SSH_CONNECTION" in os.environ or "SSH_CLIENT" in os.environ or "SSHD_OPTS" in os.environ:
            return pam_context.PAM_AUTHINFO_UNAVAIL

    # Abort if lid is closed
    if config.getboolean("core", "ignore_closed_lid"):
        if any("closed" in open(f).read() for f in glob.glob("/proc/acpi/button/lid/*/state")):
            return pam_context.PAM_AUTHINFO_UNAVAIL

    # Set up syslog
    syslog.openlog("[HOWDY]", 0, syslog.LOG_AUTH)

    # Alert the user that we are doing face detection
    if config.getboolean("core", "detection_notice"):
        pam_context.conversation(pam_context.Message(pam_context.PAM_TEXT_INFO, "Attempting face detection"))

    syslog.syslog(syslog.LOG_INFO, "Attempting facial authentication for user " + pam_context.get_user())

    # Run compare as python3 subprocess to circumvent python version and import issues
    status = subprocess.call(
        ["/usr/bin/python3", os.path.dirname(os.path.abspath(__file__)) + "/compare.py", pam_context.get_user()])

    if status in method_mapper:
        return method_mapper[status](pam_context)
    else:
        return on_unknown(pam_context, status)


def pam_sm_authenticate(pamh, flags, args):
    """Called by PAM when the user wants to authenticate, in sudo for example"""
    return doAuth(pamh)


def pam_sm_open_session(pamh, flags, args):
    """Called when starting a session, such as su"""
    return doAuth(pamh)


def pam_sm_close_session(pamh, flags, argv):
    """We don't need to clean anyting up at the end of a session, so returns true"""
    return pamh.PAM_SUCCESS


def pam_sm_setcred(pamh, flags, argv):
    """We don't need set any credentials, so returns true"""
    return pamh.PAM_SUCCESS

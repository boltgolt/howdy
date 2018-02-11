# Howdy for Ubuntu

Windows Hello™ style authentication for Ubuntu. Use your built-in IR emitters and camera in combination with face recognition to prove who you are.

Using the central authentication system in Linux (PAM), this works everywhere you would otherwise need your password: Login, lock screen, sudo, su, etc.

### Installation

Run the installer by pasting (`ctrl+shift+V`) the following command into the terminal:

`wget -O /tmp/howdy_install.py https://raw.githubusercontent.com/Boltgolt/howdy/master/installer.py && sudo python3 /tmp/howdy_install.py`

This will guide you through the installation. When that's done run `howdy add` to add a face model for the current user.

If nothing went wrong we should be able to run sudo by just showing your face. Open a new terminal and run `sudo -i` to see it in action.

### Command line

The installer adds a `howdy` command to manage face models for the current user. Use `howdy help` to list the available options.

### Troubleshooting

Any python errors get logged directly into the console and should indicate what went wrong. If authentication still fails but no errors are printed you could take a look at the last lines in `/var/log/auth.log` to see if anything has been reported there.

If you encounter an error that hasn't been reported yet, don't be afraid to open a new issue.

### A note on security

This script is in no way as secure as a password and will never be. Although it's harder to fool than normal face recognition, a person who looks similar to you or well-printed photo of you could be enough to do it.

To minimize the chance of this script being compromised, it's recommend to leave this repo in /lib/security and to keep it read only.

DO NOT USE HOWDY AS THE SOLE AUTHENTICATION METHOD FOR YOUR SYSTEM.

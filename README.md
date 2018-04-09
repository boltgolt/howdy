# Howdy for Ubuntu ![Build Status](https://travis-ci.org/Boltgolt/howdy.svg?branch=master)

Windows Hello™ style authentication for Ubuntu. Use your built-in IR emitters and camera in combination with face recognition to prove who you are.

Using the central authentication system in Linux (PAM), this works everywhere you would otherwise need your password: Login, lock screen, sudo, su, etc.

### Installation

Run the installer by pasting (`ctrl+shift+V`) the following commands into the terminal one at a time:

```
sudo add-apt-repository ppa:boltgolt/howdy
sudo apt update
sudo apt install howdy
```

This will guide you through the installation. When that's done run `sudo howdy USER add` and replace `USER` with your username to add a face model.

If nothing went wrong we should be able to run sudo by just showing your face. Open a new terminal and run `sudo -i` to see it in action.

**Note:** The build of dlib can hang on 100% for over a minute, give it time.

### Command line

The installer adds a `howdy` command to manage face models for the current user. Use `howdy help` to list the available options.

| Command   | Description                                   | Needs user |
|-----------|-----------------------------------------------|------------|
| `add`     | Add a new face model for the given user       | Yes        |
| `clear`   | Remove all face models for the given user     | Yes        |
| `config`  | Open the config file in nano                  | No         |
| `disable` | Disable or enable howdy                       | No         |
| `help`    | Show a help page                              | No         |
| `list`    | List all saved face models for the given user | Yes        |
| `remove`  | Remove a specific model for the given user    | Yes        |
| `test`    | Test the camera and recognition methods       | No         |

### Troubleshooting

Any python errors get logged directly into the console and should indicate what went wrong. If authentication still fails but no errors are printed you could take a look at the last lines in `/var/log/auth.log` to see if anything has been reported there.

If you encounter an error that hasn't been reported yet, don't be afraid to open a new issue.

### Uninstalling

There is an uninstaller available, run `sudo python3 /lib/security/howdy/uninstall.py` to remove Howdy from your system.

### A note on security

This script is in no way as secure as a password and will never be. Although it's harder to fool than normal face recognition, a person who looks similar to you or well-printed photo of you could be enough to do it.

To minimize the chance of this script being compromised, it's recommend to leave this repo in /lib/security and to keep it read only.

DO NOT USE HOWDY AS THE SOLE AUTHENTICATION METHOD FOR YOUR SYSTEM.

# Check if the username passthough works correctly with sudo
howdy | ack-grep --passthru --color "current active user: travis"
sudo howdy | ack-grep --passthru --color "current active user: travis"

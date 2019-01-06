# TEST USER SUDO PASSTHOUGH (NON-ROOT)
set -o xtrace
set -e

# Check if the username passthough works correctly with sudo
howdy | ack-grep --passthru --color "current active user: travis"
sudo howdy | ack-grep --passthru --color "current active user: travis"

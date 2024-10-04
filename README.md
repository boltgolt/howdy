![](https://boltgolt.nl/howdy/banner.png)

<p align="center">
	<a href="https://github.com/boltgolt/howdy/releases">
		<img src="https://img.shields.io/github/release/boltgolt/howdy.svg?colorB=4c1">
	</a>
	<a href="https://github.com/boltgolt/howdy/graphs/contributors">
		<img src="https://img.shields.io/github/contributors/boltgolt/howdy.svg?style=flat">
	</a>
	<a href="https://www.buymeacoffee.com/boltgolt">
		<img src="https://img.shields.io/badge/endpoint.svg?url=https://boltgolt.nl/howdy/shield.json">
	</a>
	<a href="https://actions-badge.atrox.dev/boltgolt/howdy/goto?ref=beta">
		<img src="https://img.shields.io/endpoint.svg?url=https%3A%2F%2Factions-badge.atrox.dev%2Fboltgolt%2Fhowdy%2Fbadge%3Fref%3Dbeta&style=flat&label=build&logo=none">
	</a>
	<a href="https://aur.archlinux.org/packages/howdy">
		<img src="https://img.shields.io/aur/votes/howdy?color=4c1&label=aur%20votes">
	</a>
</p>

Howdy provides Windows Hello™ style authentication for Linux. Use your built-in IR emitters and camera in combination with facial recognition to prove who you are.

Using the central authentication system (PAM) works in place of a password such as Login, lock screen, sudo, su, etc.

## Installation

Howdy is currently available and packaged for Debian/Ubuntu, Arch Linux, Fedora, and openSUSE. To use Howdy for your distro, open an issue.

**Note:** The build of Idlib can hang on 100% for over a minute; give it time.

### Ubuntu or Linux Mint

Run the installer by pasting (`ctrl+shift+V`) the following commands into the terminal one at a time:

```
sudo add-apt-repository ppa:boltgolt/howdy
sudo apt update
sudo apt install howdy
```

This will guide you through the installation.

### Debian

Download the .deb file from the [Releases page](https://github.com/boltgolt/howdy/releases) and install it with `gdebi`.

### Arch Linux

_Maintainer wanted._

Install the `howdy` package from the AUR. For AUR installation instructions, take a look at this [wiki page](https://wiki.archlinux.org/index.php/Arch_User_Repository#Installing_packages).

You will need to do some additional configuration steps. Please read the [ArchWiki entry](https://wiki.archlinux.org/index.php/Howdy) for more information.

### Fedora

_Maintainer: [@luyatshimbalanga](https://github.com/luyatshimbalanga)_

The `howdy` package is available as a [Fedora COPR repository](https://copr.fedorainfracloud.org/coprs/principis/howdy/). Install it by simply executing the following commands in a terminal:

```
sudo dnf copr enable principis/howdy
sudo dnf --refresh install howdy
```

See the link to the COPR repository for detailed configuration steps.

### openSUSE

_Maintainer: [@dmafanasyev](https://github.com/dmafanasyev)_

Go to the [openSUSE wiki page](https://en.opensuse.org/SDB:Facial_authentication) for detailed installation instructions.

### Building from source

If you want to build Howdy from the source, a few dependencies are required.

#### Dependencies

- Python 3.6 or higher
  * pip
  * setuptools
  * wheel
- meson version 0.64 or higher
- ninja
- INIReader (can be pulled from git automatically if not found)
- libevdev

To install them on Debian/Ubuntu, for example:

```
sudo apt-get update && sudo apt-get install -y \
python3 python3-pip python3-setuptools python3-wheel \
cmake make build-essential \
libpam0g-dev libinih-dev libevdev-dev \
python3-dev libopencv-dev
```

#### Build

```sh
meson setup build
meson compile -C build
```

You can also install Howdy on your system with `meson install -C build.`

## Setup

After installation, Howdy needs to learn what you look like so it can recognize you later. Run `sudo howdy add` to add a face model.

If nothing went wrong we should be able to run sudo by just showing your face. Open a new terminal and run `sudo -i` to see it in action. Please check [this wiki page](https://github.com/boltgolt/howdy/wiki/Common-issues) if you're experiencing problems or [search](https://github.com/boltgolt/howdy/issues) for similar issues.

If you're curious, you can run `sudo howdy config` to open the central config file and see the options Howdy offers. On most systems this will open the nano editor, where you must press `ctrl`+`x` to save your changes.

## CLI

The installer adds a `howdy` command to manage face models for the current user. Use `howdy --help` or `man howdy` to list the available options.

Usage:
```
howdy [-U user] [-y] command [argument]
```

| Command   | Description                                   |
|-----------|-----------------------------------------------|
| `add`     | Add a new face model for a user               |
| `clear`   | Remove all face models for a user             |
| `config`  | Open the config file in your default editor   |
| `disable` | Disable or enable howdy                       |
| `list`    | List all saved face models for a user         |
| `remove`  | Remove a specific model for a user            |
| `snapshot`| Take a snapshot of your camera input          |
| `test`    | Test the camera and recognition methods       |
| `version` | Print the current version number              |

## Contributing [![](https://img.shields.io/travis/boltgolt/howdy/dev.svg?label=dev%20build)](https://github.com/boltgolt/howdy/tree/dev) [![](https://img.shields.io/github/issues-raw/boltgolt/howdy/enhancement.svg?label=feature+requests&colorB=4c1)](https://github.com/boltgolt/howdy/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement)

The easiest way to contribute to Howdy is by starring the repository and opening GitHub issues for features you'd like to see. If you want to do more, you can also [buy me a coffee](https://www.buymeacoffee.com/boltgolt).

Code contributions are also very welcome. If you want to port Howdy to another distro, feel free to open an issue for that too.

## Troubleshooting

Any Python errors get logged directly into the console and should indicate what went wrong. If authentication still fails but no errors are printed, you could take a look at the last lines in `/var/log/auth.log` to see if anything has been reported there.

Please first check the [wiki on common issues](https://github.com/boltgolt/howdy/wiki/Common-issues) and 
if you encounter an error that hasn't been reported yet, don't be afraid to open a new issue.

## A note on security

This package is not as secure as a password and will never be. Although it's harder to fool than normal face recognition, a person who looks similar to you, or a well-printed photo of you could be enough to do it. Howdy is a more quick and convenient way of logging in, not a more secure one.

To minimize the chance of this program being compromised, it's recommended to leave Howdy in `/lib/security` and to keep it read-only.

DO NOT USE HOWDY AS THE SOLE AUTHENTICATION METHOD FOR YOUR SYSTEM.

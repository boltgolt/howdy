![](https://boltgolt.nl/howdy/banner.png)

<p align="center">
	<a href="https://travis-ci.org/boltgolt/howdy">
		<img src="https://img.shields.io/travis/boltgolt/howdy/master.svg">
	</a>
	<a href="https://github.com/boltgolt/howdy/releases">
		<img src="https://img.shields.io/github/release/boltgolt/howdy.svg?colorB=4c1">
	</a>
	<a href="https://github.com/boltgolt/howdy/graphs/contributors">
		<img src="https://img.shields.io/github/contributors/boltgolt/howdy.svg?style=flat">
	</a>
	<a href="https://www.buymeacoffee.com/boltgolt">
		<img src="https://img.shields.io/badge/endpoint.svg?url=https://boltgolt.nl/howdy/shield.json">
	</a>
</p>

Howdy provides Windows Hello™ style authentication for Linux. Use your built-in IR emitters and camera in combination with facial recognition to prove who you are.

Using the central authentication system (PAM), this works everywhere you would otherwise need your password: Login, lock screen, sudo, su, etc.

## Installation

Howdy is currently available and packaged for Debian/Ubuntu, Arch Linux, Fedora and openSUSE. If you’re interested in packaging Howdy for your distro, don’t hesitate to open an issue.

**Note:** The build of dlib can hang on 100% for over a minute, give it time.

### Ubuntu or Linux Mint

Run the installer by pasting (`ctrl+shift+V`) the following commands into the terminal one at a time:

```
sudo add-apt-repository ppa:boltgolt/howdy
sudo apt update
sudo apt install howdy
```

This will guide you through the installation.

### Debian

Download the .deb file from the [Releases page](https://github.com/boltgolt/howdy/releases) and install with gdebi.

### Arch Linux
_Maintainer wanted._

Install the `howdy` package from the AUR. For AUR installation instructions, take a look at this [wiki page](https://wiki.archlinux.org/index.php/Arch_User_Repository#Installing_packages).

You will need to do some additional configuration steps. Please read the [ArchWiki entry](https://wiki.archlinux.org/index.php/Howdy) for more information.

### Fedora
_Maintainer: [@luyatshimbalanga](https://github.com/luyatshimbalanga)_

The `howdy` package is available as a [Fedora COPR repository](https://copr.fedorainfracloud.org/coprs/principis/howdy/), install it by simply executing the following commands in a terminal:

```
sudo dnf copr enable principis/howdy
sudo dnf --refresh install howdy
```

See the link to the COPR repository for detailed configuration steps.

### openSUSE
_Maintainer: [@dmafanasyev](https://github.com/dmafanasyev)_

Go to the [openSUSE wiki page](https://en.opensuse.org/SDB:Facial_authentication) for detailed installation instructions.

## Setup

After installation, Howdy needs to learn what you look like so it can recognise you later. Run `sudo howdy add` to add a face model.

If nothing went wrong we should be able to run sudo by just showing your face. Open a new terminal and run `sudo -i` to see it in action. Please check [this wiki page](https://github.com/boltgolt/howdy/wiki/Common-issues) if you're experiencing problems or [search](https://github.com/boltgolt/howdy/issues) for similar issues.

If you're curious you can run `sudo howdy config` to open the central config file and see the options Howdy has to offer. On most systems this will open the nano editor, where you have to press `ctrl`+`x` to save your changes.

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

The easiest ways to contribute to Howdy is by starring the repository and opening GitHub issues for features you'd like to see. If you want to do more, you can also [buy me a coffee](https://www.buymeacoffee.com/boltgolt).

Code contributions are also very welcome. If you want to port Howdy to another distro, feel free to open an issue for that too.

## Troubleshooting

Any Python errors get logged directly into the console and should indicate what went wrong. If authentication still fails but no errors are printed, you could take a look at the last lines in `/var/log/auth.log` to see if anything has been reported there.

If you encounter an error that hasn't been reported yet, don't be afraid to open a new issue.

## A note on security

This package is in no way as secure as a password and will never be. Although it's harder to fool than normal face recognition, a person who looks similar to you, or a well-printed photo of you could be enough to do it. Howdy is a more quick and convenient way of logging in, not a more secure one.

To minimize the chance of this program being compromised, it's recommended to leave Howdy in `/lib/security` and to keep it read-only.

DO NOT USE HOWDY AS THE SOLE AUTHENTICATION METHOD FOR YOUR SYSTEM.

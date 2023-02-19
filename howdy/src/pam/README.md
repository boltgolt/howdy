# Howdy PAM module

## Prepare

This module depends on `INIReader` and `libevdev`.
They can be installed with these packages:

```
Arch Linux - libinih libevdev
Debian     - libinih-dev libevdev-dev
Fedora     - inih-devel libevdev-devel
OpenSUSE   - inih libevdev-devel
```

If your distribution doesn't provide `INIReader`,
it will be automatically pulled from git at the subproject's pinned version.

## Build

``` sh
meson setup build
meson compile -C build
```

## Install

``` sh
meson install -C build
```

Add the following line to your PAM configuration (/etc/pam.d/your-service):

``` pam
auth  sufficient  pam_howdy.so
```

# Howdy PAM module

## Prepare

This module depends on `INIReader`.
It can be installed with these packages:

```
Arch Linux - libinih
Debian     - libinih-dev
Fedora     - inih-devel
OpenSUSE   - inih
```

If your distribution doesn't provide `INIReader`,
it will be automatically pulled from the latest git version.

## Build

``` sh
meson setup build
meson compile -C build
```

## Install

``` sh
meson install -C build
```

Change PAM config line to:

``` pam
auth  sufficient  pam_howdy.so
```

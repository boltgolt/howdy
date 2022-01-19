# Howdy PAM module

## Prepare

Howdy PAM module depends on `INIReader`.

If you are building a distro package,
there is a list for it below:

```
Arch Linux - libinih
Debian     - libinih-dev
Fedora     - inih-devel
OpenSUSE   - inih
```

## Build

``` sh
meson setup build
meson compile -C build
```

## Install

``` sh
sudo meson install -C build
```

Change PAM config line to:

``` pam
auth  sufficient  pam_howdy.so
```

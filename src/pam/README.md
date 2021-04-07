# Howdy PAM module

## Build

```sh
meson setup build -Dinih:with_INIReader=true
meson compile -C build
```

## Install

```sh
sudo mv build/libpam_howdy.so /lib/security/pam_howdy.so
```

Change PAM config line to:

```pam
auth     sufficient pam_howdy.so
```

# Howdy PAM module

## Build

```sh
meson setup build -Dinih:with_INIReader=true
meson compile -C build
sudo mv build/libpam_howdy.so /lib/security/pam_howdy.so
```

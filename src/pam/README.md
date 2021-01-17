# Howdy PAM module

## Building (for now)

```sh
meson setup build -Dinih:with_INIReader=true
meson compile build
sudo mv build/libpam_howdy.so /lib/security/
```

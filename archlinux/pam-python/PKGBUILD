# Maintainer: boltgolt <boltgolt@gmail.com>
# Maintainer: Kelley McChesney <kelley@kelleymcchesney.us>
pkgname=pam-python
pkgver=1.0.6
pkgrel=1
pkgdesc="Python for PAM"
arch=('x86_64')
url="https://github.com/boltgolt/howdy"
license=('MIT')
depends=(
  'python2'
)
makedepends=(
  'python2-sphinx'
  'cmake'
)
source=(
  "https://downloads.sourceforge.net/project/pam-python/pam-python-1.0.6-1/pam-python-1.0.6.tar.gz"
  "https://sourceforge.net/p/pam-python/tickets/_discuss/thread/5dc8cfd5/5839/attachment/pam-python-1.0.6-fedora.patch"
  "https://sourceforge.net/p/pam-python/tickets/_discuss/thread/5dc8cfd5/5839/attachment/pam-python-1.0.6-gcc8.patch"
)
sha256sums=(
  '0ef4dda35da14088afb1640266415730a6e0274bea934917beb5aca90318f853'
  'acb9d1b5cf7cad73d5524334b7954431bb9b90f960980378c538907e468c34b5'
  '02dd9a4d8ec921ff9a2408183f290f08102e3f9e0151786ae7220a4d550bfe24'
)

prepare() {
  # Preparing pam-python to be installed
  cd pam-python-1.0.6
  sed -i'' 's|#!/usr/bin/python -W default|#!/usr/bin/python2 -W default|g' src/setup.py
  sed -i'' 's|#!/usr/bin/python -W default|#!/usr/bin/python2 -W default|g' src/test.py
  sed -i'' 's|LIBDIR ?= /lib/security|LIBDIR ?= /usr/lib/security|g' src/Makefile
  sed -i'' 's|sphinx-build|sphinx-build2|g' doc/Makefile
  patch -p1 < ../pam-python-1.0.6-fedora.patch
  patch -p1 < ../pam-python-1.0.6-gcc8.patch

  cd ..
}
build() {
  # Building pam-python
  cd pam-python-1.0.6
  PREFIX=/usr make
  cd ..
}
package() {
  # Installing pam-python
  cd pam-python-1.0.6
  PREFIX=/usr make DESTDIR="$pkgdir/" install
}

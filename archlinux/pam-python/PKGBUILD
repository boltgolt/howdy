# Maintainer: boltgolt <boltgolt@gmail.com>
# Maintainer: Kelley McChesney <kelley@kelleymcchesney.us>
pkgname=pam-python
pkgver=1.0.7
pkgrel=1
pkgdesc="Python for PAM"
arch=('x86_64')
url="https://github.com/boltgolt/howdy"
license=('MIT')
depends=(
  'python2'
)
makedepends=(
  'python-sphinx'
  'cmake'
)
source=(
  "https://downloads.sourceforge.net/project/pam-python/pam-python-1.0.7-1/pam-python-1.0.7.tar.gz"
)
sha256sums=('96ce72fe355b03b87c0eb540ecef06f33738f98f56581e81eb5bffbad1a47e07')

prepare() {
  # Preparing pam-python to be installed
  cd "$srcdir/pam-python-$pkgver"
  sed -i'' 's|#!/usr/bin/python -W default|#!/usr/bin/python2 -W default|g' src/setup.py
  sed -i'' 's|#!/usr/bin/python -W default|#!/usr/bin/python2 -W default|g' src/test.py
  sed -i'' 's|LIBDIR ?= /lib/security|LIBDIR ?= /usr/lib/security|g' src/Makefile
  sed -i'' 's|sphinx-build|sphinx-build|g' doc/Makefile
}

build() {
  # Building pam-python
  cd "$srcdir/pam-python-$pkgver"
  PREFIX=/usr make
}

package() {
  # Installing pam-python
  cd "$srcdir/pam-python-$pkgver"
  PREFIX=/usr make DESTDIR="$pkgdir/" install
}

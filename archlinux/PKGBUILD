# Maintainer: boltgolt <boltgolt@gmail.com>
# Maintainer: Kelley McChesney <kelley@kelleymcchesney.us>
pkgname=howdy
pkgver=2.3.1
pkgrel=1
pkgdesc="Windows Hello for Linux"
arch=('x86_64')
url="https://github.com/boltgolt/howdy"
license=('MIT')
depends=(
	'opencv'
	'hdf5'
	'python2'
	'python3'
	'python-pillow'
	'python-face_recognition_models'
	'python-click'
	'python-numpy'
)
makedepends=(
	'python2-sphinx'
	'git'
	'cmake'
	'pkgfile'
	'python-pip'
)
backup=('usr/lib/security/howdy/config.ini')
source=("https://github.com/boltgolt/howdy/archive/v2.3.1.tar.gz"
        "https://downloads.sourceforge.net/project/pam-python/pam-python-1.0.6-1/pam-python-1.0.6.tar.gz"
	"https://sourceforge.net/p/pam-python/tickets/_discuss/thread/5dc8cfd5/5839/attachment/pam-python-1.0.6-fedora.patch"
	"https://sourceforge.net/p/pam-python/tickets/_discuss/thread/5dc8cfd5/5839/attachment/pam-python-1.0.6-gcc8.patch")
sha256sums=('d4057fd4f27c1d14e30718e9412eac578b383846d70cbb7a57725d8132c90b1e'
	    '0ef4dda35da14088afb1640266415730a6e0274bea934917beb5aca90318f853'
	    'acb9d1b5cf7cad73d5524334b7954431bb9b90f960980378c538907e468c34b5'
	    '02dd9a4d8ec921ff9a2408183f290f08102e3f9e0151786ae7220a4d550bfe24')
prepare() {
	# Preparing dlib with GPU here
	git clone --depth 1 https://github.com/davisking/dlib.git dlib_clone

	# Preparing pam-python to be installed 
	cd pam-python-1.0.6
	sed -i'' 's|#!/usr/bin/python -W default|#!/usr/bin/python2 -W default|g' src/setup.py
	sed -i'' 's|#!/usr/bin/python -W default|#!/usr/bin/python2 -W default|g' src/test.py
	sed -i'' 's|LIBDIR ?= /lib/security|LIBDIR ?= /usr/lib/security|g' src/Makefile
	sed -i'' 's|sphinx-build|sphinx-build2|g' doc/Makefile
	patch -p1 < ../pam-python-1.0.6-fedora.patch
	patch -p1 < ../pam-python-1.0.6-gcc8.patch
	
	# Doing some fixes for pam-python so that it can compile
	sudo pkgfile -u
	sudo pkgfile /usr/include/sys/cdefs.h core/glibc
	cd ..
}
build() {
	# Building pam-python
	cd pam-python-1.0.6
	PREFIX=/usr make
	cd ..

	# Building dlib with GPU
	cd dlib_clone
	python setup.py build
}
package() {
	PIP_CONFIG_FILE=/dev/null pip install --isolated --root="$pkgdir" --ignore-installed --no-deps face_recognition

	# Installing dlib with GPU
	cd dlib_clone
	python3 setup.py install --yes USE_AVX_INSTRUCTIONS --no DLIB_USE_CUDA --root="$pkgdir/" --optimize=1 --skip-build
	cd ..

	# Installing pam-python
	cd pam-python-1.0.6
	PREFIX=/usr make DESTDIR="$pkgdir/" install
	cd ..

	# Installing the proper license files and the rest of howdy
	cd howdy-2.3.1
	install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
	mkdir -p "$pkgdir/usr/lib/security/howdy"
	cp -r src/* "$pkgdir/usr/lib/security/howdy"
	chmod 600 -R "$pkgdir/usr/lib/security/howdy"
	mkdir -p "$pkgdir/usr/bin"
	ln -s /lib/security/howdy/cli.py "$pkgdir/usr/bin/howdy"
	chmod +x "$pkgdir/usr/lib/security/howdy/cli.py"
	mkdir -p "$pkgdir/usr/share/bash-completion/completions"
	cp autocomplete/howdy "$pkgdir/usr/share/bash-completion/completions/howdy"
}

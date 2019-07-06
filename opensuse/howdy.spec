#
# spec file for package howdy
#
# Copyright (c) 2019 Dmitriy O. Afanasyev, <dmafanasyev@gmail.com>.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

Name:           howdy
Version:        2.5.1
Release:		0
Summary:        Windows Hello™ style authentication for Linux
License:        MIT
Url:            https://github.com/boltgolt/%{name}
Group:          System/Base
Source:			https://github.com/boltgolt/%{name}/archive/v%{version}.tar.gz

BuildRequires: wget
Requires:	python3-opencv
Requires:	ffmpeg-4
Requires:	libv4l2-0
Requires:	pam-python
Requires:	python3-dlib

#TODO: pre and post install steps, auto conf /etc/pam.d

%description
Windows Hello™ style authentication for Linux. Use your built-in IR emitters and camera in combination with face recognition to prove who you are.

%prep
%setup -q -n v%{version}

%build
## nothing to build

%install
mkdir -p %{buildroot}%{_libdir}/security/%{name}
rm -fr src/*~
cp -pr src/* %{buildroot}%{_libdir}/security/%{name}

# Facial recognition model preinstalled manualy (before packaging), need to delete some files
rm -fr %{buildroot}%{_libdir}/security/%{name}/dlib-data/{Readme.md,install.sh,.gitignore}

#Add bash completion
mkdir -p %{buildroot}%{_datadir}/bash-completion/completions
install -Dm 644 autocomplete/%{name} %{buildroot}%{_datadir}/bash-completion/completions

# Create an executable
mkdir -p %{buildroot}%{_bindir}
chmod +x %{buildroot}%{_libdir}/security/%{name}/cli.py
ln -s %{_libdir}/security/%{name}/cli.py %{buildroot}%{_bindir}/%{name}

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%dir %{_libdir}/security
%{_libdir}/security/%{name}
%{_datadir}/bash-completion/completions/%{name}
%config(noreplace) %{_libdir}/security/%{name}/config.ini

%changelog
* Sun May 12 2019 Dmitriy O. Afanasyev <dmafanasyev@gmail.com> - 2.5.1
- Initial packaging

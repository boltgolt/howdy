%global         debug_package %{nil}

Name:           howdy
Version:        3.0.0
Release:        1%{?dist}
Summary:        Windows Helloâ„¢ style authentication for Linux


License:        MIT
URL:            https://github.com/boltgolt/%{name}
Source0:        https://github.com/boltgolt/%{name}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires: polkit-devel
# We need python3-devel for pathfix.py
BuildRequires: python3-devel
Requires:      python3dist(dlib) >= 6.0
Requires:      python3-opencv


%description
Windows Helloâ„¢ style authentication for Linux. Use your built-in IR emitters and camera in combination with face recognition to prove who you are.


%prep
%autosetup
pathfix.py -i %{__python3} .


%build
## nothing to build


%install
mkdir -p %{buildroot}%{_libdir}/security/%{name}
# Remove backup file
rm -fr src/*~

# Install source file 
mkdir -p %{buildroot}%{_libdir}/security/%{name}
install -Dm 0644 src/config.ini %{buildroot}%{_libdir}/security/%{name}
install -Dm 0644 src/logo.png %{buildroot}%{_libdir}/security/%{name}
install -Dm 0644 src/*.py -t %{buildroot}%{_libdir}/security/%{name}
install -Dm 0644 src/cli/* -t %{buildroot}%{_libdir}/security/%{name}/cli/
install -Dm 0644 src/dlib-data/* -t %{buildroot}%{_libdir}/security/%{name}/dlib-data/
chmod a+x %{buildroot}%{_libdir}/security/%{name}/dlib-data
install -Dm 0644 src/recorders/* -t %{buildroot}%{_libdir}/security/%{name}/records/
install -Dm 0644 src/rubberstamps/* -t %{buildroot}%{_libdir}/security/%{name}/rubberstamps/

# Install facial recognition, may look at better alternative
# for offline user
sh %{buildroot}%{_libdir}/security/%{name}/dlib-data/install.sh
mv *.dat %{buildroot}%{_libdir}/security/%{name}/dlib-data
rm -fr %{buildroot}%{_libdir}/security/%{name}/dlib-data/{Readme.md,install.sh,.gitignore}

# Add polkit rules
mkdir -p %{buildroot}%{_datadir}/polkit-1/actions
install -Dm 0644 howdy/fedora/com.github.boltgolt.howdy.policy %{buildroot}%{_datadir}/polkit-1/actions/

#Add bash completion
mkdir -p %{buildroot}%{_datadir}/bash-completion/completions
install -Dm 644 autocomplete/%{name} %{buildroot}%{_datadir}/bash-completion/completions

# Create an executable
mkdir -p %{buildroot}%{_bindir}
chmod +x %{buildroot}%{_libdir}/security/%{name}/cli.py
ln -s %{_libdir}/security/%{name}/cli.py %{buildroot}%{_bindir}/%{name}

# Add environment variables
install -Dm 0644 src/shell/howdy.sh %{buildroot}%{_sysconfdir}/profile.d/
install -Dm 0644 src/shell/howdy.csh %{buildroot}%{_sysconfdir}/profile.d/

%post
if [ "$1" -eq 1 ]; then
    # set environement variable
    sed "s|HOWDY_LIB=''|HOWDY_LIB=%{_libdir}/security/%{name}|" %{_sysconfdir}/profile.d/howdy.sh
    sed "s|HOWDY_LIB ''|HOWDY_LIB %{_libdir}/security/%{name}|" %{_sysconfdir}/profile.d/howdy.sh
fi


%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{_datadir}/bash-completion/completions/%{name}
%{_datadir}/polkit-1/actions/
%{_libdir}/security/%{name}
%config(noreplace) %{_libdir}/security/%{name}/config.ini
%config(noreplace) %{_sysconfdir}/profile.d/howdy.*


%changelog
* Fri May 20 2022 Arthur Bols <arthur@bols.dev> - 2.6.1-6
- Rebuilt for Fedora 36

* Fri Jan 07 2022 Arthur Bols <arthur@bols.dev> - 2.6.1-5
- Incorrect disable of Intel MFX messages in csh

* Thu Jan 06 2022 Arthur Bols <arthur@bols.dev> - 2.6.1-4
- Add option to fix Intel MFX messages

* Thu Jun 10 2021 Arthur Bols <arthur@bols.dev> - 2.6.1-3
- Set OPENCV_LOG_LEVEL to ERROR to fix notices.

* Wed Sep 02 2020 Arthur Bols <arthur@bols.dev> - 2.6.1-2
- Rebuild for Fedora 32
- Fix spec formatting

* Wed Sep 02 2020 Arthur Bols <arthur@bols.dev> - 2.6.1-1
- Update to 2.6.1

* Sun May 03 2020 Arthur Bols <arthur@bols.dev> - 2.6.0-1
- Update to 2.6.0

* Sun May 03 2020 Arthur Bols <arthur@bols.dev> - 2.5.1-4
- Fixed dependencies

* Sun Apr 07 2019 Luya Tshimbalanga <luya@fedoraproject.org> - 2.5.1-3
- Add polkit policy

* Sun Apr 07 2019 Luya Tshimbalanga <luya@fedoraproject.org> - 2.5.1-2
- Install facial recognition data

* Tue Apr 02 2019 Luya Tshimbalanga <luya@fedoraproject.org> - 2.5.1-1
- Update to 2.5.1

* Sat Mar 16 2019 Luya Tshimbalanga <luya@fedoraproject.org> - 2.5.0-3
- Require python-v4l2

* Wed Jan 23 2019 Luya Tshimbalanga <luya@fedoraproject.org> - 2.5.0-2
- Fix pam configuration

* Sun Jan 06 2019 Luya Tshimbalanga <luya@fedoraproject.org> - 2.5.0-1
- Update to 2.5.0

* Thu Nov 29 2018 Luya Tshimbalanga <luya@fedoraproject.org> - 2.4.0-3
- Add conditional statement for RHEL/Centos 7.x based on williamwlk spec

* Thu Nov 29 2018 Luya Tshimbalanga <luya@fedoraproject.org> - 2.4.0-3
- Include bash completion

* Mon Nov 26 2018 Luya Tshimbalanga <luya@fedoraproject.org> - 2.4.0-2
- Switch to new requirement method from Fedora Python guideline

* Mon Nov 26 2018 Luya Tshimbalanga <luya@fedoraproject.org> - 2.4.0-1
- Update to 2.4.0

* Thu Nov  1 2018 Luya Tshimbalanga <luya@fedoraproject.org> - 2.3.1-1
- Initial package
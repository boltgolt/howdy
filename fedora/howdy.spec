%global 	with_snapshot 0
%global 	date 20181109.
%global		commit b4ecafe61c83a4aaab56a52a713296143c87b576
%global		shortcommit %(c=%{commit}; echo ${c:0:7})
%global		debug_package %{nil}	

Name:           howdy
Version:        2.5.1
%if %{with_snapshot}
Release:	0.1.git.%{date}%{shortcommit}%{?dist}
%else
Release:	3%{?dist}
%endif
Summary:        Windows Hello™ style authentication for Linux


License:        MIT
URL:            https://github.com/boltgolt/%{name}
%if %{with_snapshot}
Source0:	https://github.com/boltgolt/%{name}/archive/%{commit}/%{name}-%{shortcommit}.tar.gz
%else
Source0:	https://github.com/boltgolt/%{name}/archive/v%{version}/%{name}-%{version}.tar.gz
%endif
Source1:	com.github.boltgolt.howdy.policy

BuildRequires:	polkit-devel
%if 0%{?fedora}
# We need python3-devel for pathfix.py
BuildRequires:	python3-devel	
Requires:       python3dist(dlib) >= 6.0
Requires:	python3dist(v4l2)
Requires:	python3-face_recognition
Supplements:	python3-face_recognition_models
Requires:	python3-opencv
Requires:	pam_python
%endif


%description
Windows Hello™ style authentication for Linux. Use your built-in IR emitters and camera in combination with face recognition to prove who you are.

%prep
%autosetup
pathfix.py -i %{__python3} .

%build
## nothing to build

%install
mkdir -p %{buildroot}%{_libdir}/security/%{name}
# Remove backup file
rm -fr src/*~
cp -pr src/* %{buildroot}%{_libdir}/security/%{name}

# Install facial recognition, may look at better alternative
# for offline user
sh %{buildroot}%{_libdir}/security/%{name}/dlib-data/install.sh
mv *.dat %{buildroot}%{_libdir}/security/%{name}/dlib-data
rm -fr %{buildroot}%{_libdir}/security/%{name}/dlib-data/{Readme.md,install.sh,.gitignore}

# Add polkit rules
mkdir -p %{buildroot}%{_datadir}/polkit-1/actions
install -Dm 0644 %{SOURCE1} %{buildroot}%{_datadir}/polkit-1/actions/

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
%{_datadir}/bash-completion/completions/%{name}
%{_datadir}/polkit-1/actions/
%{_libdir}/security/%{name}
%config(noreplace) %{_libdir}/security/%{name}/config.ini

%changelog
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

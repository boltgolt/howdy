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
Release:	1%{?dist}
%endif
Summary:        Windows Hello™ style authentication for Linux


License:        MIT
URL:            https://github.com/boltgolt/%{name}
%if %{with_snapshot}
Source0:	https://github.com/boltgolt/%{name}/archive/%{commit}/%{name}-%{shortcommit}.tar.gz
%else
Source0:	https://github.com/boltgolt/%{name}/archive/v%{version}/%{name}-%{version}.tar.gz
%endif

%if 0%{?fedora}
# We need python3-devel for pathfix.py
BuildRequires:	python3-devel	
Requires:       python3dist(dlib) >= 6.0
Requires:	python3dist(v4l2)
Requires:	python3-face_recognition
Supplements:	python3-face_recognition_models
Requires:	python3-opencv
Requires:	python3-pam
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
cp -pr src/* %{buildroot}%{_libdir}/security/%{name}

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
#%%{_datadir}/pam-config/%%{name}
%{_libdir}/security/%{name}
%config(noreplace) %{_libdir}/security/%{name}/config.ini

%changelog

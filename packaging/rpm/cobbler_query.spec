Name:           cobbler_query
Version:        0.1
Release:        0
Summary:        Query a cobbler server over xmlrpc
License:        GPLv2
URL:            https://github.com/weaselkeeper/cobbler_query
Group:          System Environment/Base
Source0:        %{name}-%{version}.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-root-%(%{__id_u} -n)
BuildArch:      noarch

Requires:       python

%description
query a cobbler server for information on a system.

%prep
%setup -q -n %{name}

%install
rm -rf %{buildroot}

%{__mkdir_p} %{buildroot}%{_bindir}
%{__mkdir_p} %{buildroot}%{_sysconfdir}/%{name}
%{__mkdir_p} %{buildroot}%{_localstatedir}/log/%{name}
cp -r ./*.py %{buildroot}%{_bindir}/
#cp -r ./config/* %{buildroot}%{_sysconfdir}/%{name}

%files
%{_bindir}/*.py
#%{_sysconfdir}/%{name}/*

%pre

%post

%clean
rm -rf %{buildroot}

%changelog
* Sat Jul 27 2013 Jim Richardson <weaselkeeper@gmail.com> - 0.1
- Initial RPM build structure added.

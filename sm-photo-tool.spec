Name:           sm-photo-tool
Version:        1.16
Release:        1
Summary:        Smugmug client
Group:          Applications/Multimedia
License:        GPL
URL:            http://sm-photo-tool.sourceforge.net/
Source0:        %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-root-%(%{__id_u} -n)
BuildArch:      noarch
BuildRequires:  python
Requires:       python >= 2.3

%description
Smugmug client

%prep
%setup -q

%install
rm -rf %{buildroot}
install -d -m 755 %{buildroot}%{_usr}/share/%{name}/
install -d -m 755 %{buildroot}%{_usr}/share/doc/%{name}-%{version}/
install -d -m 755 %{buildroot}%{_usr}/bin/
install -d -m 755 %{buildroot}%{_sysconfdir}/%{name}/
install -m 644 LICENSE.TXT %{buildroot}%{_usr}/share/doc/%{name}-%{version}/
install -m 644 src/smugmugrc %{buildroot}%{_usr}/share/doc/%{name}-%{version}/
install -m 755 src/sm_photo_tool.py %{buildroot}%{_usr}/bin/%{name}
cp src/cli.py %{buildroot}%{_usr}/share/%{name}/
cp src/smcommands.py %{buildroot}%{_usr}/share/%{name}/
cp src/config.py %{buildroot}%{_usr}/share/%{name}/
cp src/sm_wrapper.py %{buildroot}%{_usr}/share/%{name}/

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%attr(755, root, root) %{_usr}/bin/%{name}
%{_usr}/share/doc/%{name}-%{version}/LICENSE.TXT
%{_usr}/share/doc/%{name}-%{version}/smugmugrc
%{_usr}/share/sm-photo-tool/*.py*

%changelog
* Tue Aug 04 2009 jesus m rodriguez <jesusr@redhat.com> 1.16-1
- bump the version (jesusr@redhat.com)
- add 1.15 release (jesusr@redhat.com)
- remove old playpen directory (jesusr@redhat.com)
- rename commands.py -> smcommands.py (jesusr@redhat.com)
- renamed commands.py, insert path using sys.path.insert (jesusr@redhat.com)
- fix up %files (jesusr@redhat.com)
- add /usr/share/sm_photo_tool path (jesusr@redhat.com)
- copy the files from their new location (jesusr@redhat.com)
- point to correct smugmugrc (jesusr@redhat.com)

* Mon Aug 03 2009 jesus m rodriguez <jesusr@redhat.com> 1.15-1
- new package

* Tue Mar 18 2007 Jesus Rodriguez <jmrodri at gmail dot com> 1.12-1
-  albumid written incorrectly to gallery file causing img uploads to fail
* Mon Mar 17 2007 Jesus Rodriguez <jmrodri at gmail dot com> 1.11-1
- fix bug: 1819595
- reformat code to have spaces after all comma's
* Sat Apr  1 2006 Jesus Rodriguez <jmrodri at gmail dot com> 1.10-1
- initial rpm release

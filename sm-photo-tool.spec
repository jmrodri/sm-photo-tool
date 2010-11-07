Name:           sm-photo-tool
Version:        1.22
Release:        1%{?dist}
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
cp src/log.py %{buildroot}%{_usr}/share/%{name}/
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
* Sun Nov 07 2010 jesus m rodriguez <jmrodri@gmail.com> 1.22-1
- add png support (jmrodri@gmail.com)

* Sat Nov 06 2010 jesus m rodriguez <jmrodri@gmail.com> 1.21-1
- mark link as dead (jesusr@redhat.com)
- documenation changes (jmrodri@gmail.com)
- Fix usage string.  [options] have to come after the MODULE.
  (lccha+github@immerbox.com)
- remove pointless ignore lines (jmrodri@gmail.com)

* Mon Dec 28 2009 jesus m rodriguez <jmrodri@gmail.com> 1.20-1
- raise SmugmugException during login. (jmrodri@gmail.com)
- Add new options. (lccha+smphototool@immerbox.com)
- Added new options (lccha+smphototool@immerbox.com)
- If filename ends with +, append instead of overwriting log file
  (lccha+smphototool@immerbox.com)
- fix file formats (jmrodri@gmail.com)
- allow mp4 type files (jmrodri@gmail.com)

* Fri Oct 30 2009 jesus m rodriguez <jesusr@redhat.com> 1.19-1
- add log.py to the list of files to copy (jesusr@redhat.com)

* Fri Oct 30 2009 jesus m. rodriguez <jmrodri@gmail.com>
- switched to using HTTP PUT instead of HTTP POST (jmrodri@gmail.com)
- figured out how to use httplib correctly. (jmrodri@gmail.com)
- added log file support (jmrodri@gmail.com)
- httplib version (jmrodri@gmail.com)
- flush the output so that we can see what's going on. (jmrodri@gmail.com)
- removing unused old Makefile (jmrodri@gmail.com)

* Tue Aug 04 2009 jesus m rodriguez <jesusr@redhat.com> 1.16-2
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

sm-photo-tool

Small script to manage photos and galleries on smugmug.com

Welcome to the new home of sm-photo-tool. This a small python script
used to manage photos and galleries on smugmug.com. Using sm-photo-tool
requires an account on smugmug.com.

sm-photo-tool is based on the original sm_tool.py (smugmug.py) by
John Ruttenberg. You can find the original here:
http://gate.chezrutt.com:8030/rutt/sm_tool/sm_tool.py

I wanted to find a home for sm_tool.py and give it issue and version
tracking.

sm_tool.py - actual python script
smugmugrc - configuration file used by the script
LICENSE.TXT - GNU GENERAL PUBLIC LICENSE 2.0
sm_tool.spec - Fedora Core RPM spec file.  Not yet finished.

BUILDING RPM
-------------
If you'd like to build an RPM follow these simple steps:

1) create the tar file for use in the src.rpm

   ./buildtar.sh

2) now symlink the files in the rpm/ directory to the appropriate
   rpm build environment.  Defaults to /usr/src/redhat/.

   cd /usr/src/redhat/SOURCES/
   ln -s $SM_PHOTO_TOOL/rpm/sm-photo-tool-1.10.tar.gz
   ln -s $SM_PHOTO_TOOL/rpm/sm-photo-tool-1.10-license.patch
   cd /usr/src/redhat/SPECS/
   ln -s $SM_PHOTO_TOOL/rpm/spec/sm-photo-tool.spec

3) now build the rpm

   cd /usr/src/redhat/SPECS/
   rpmbuild -ba sm-photo-tool.spec

4) you can find the rpm in /usr/src/redhat/RPMS/noarch/

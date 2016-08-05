sm-photo-tool

Small script to manage photos and galleries on smugmug.com

Welcome to the new home of sm-photo-tool. This a small python script
used to manage photos and galleries on smugmug.com. Using sm-photo-tool
requires an account on smugmug.com.

sm-photo-tool is based on the original sm_tool.py (smugmug.py) by
John Ruttenberg. You can find the original here:
http://gate.chezrutt.com:8030/rutt/sm_tool/sm_tool.py (dead link)

I wanted to find a home for sm_tool.py and give it issue and version
tracking.

src/sm_photo_tool.py - actual python script
src/smugmugrc - configuration file used by the script
LICENSE.TXT - GNU GENERAL PUBLIC LICENSE 2.0
rpm/spec/sm_photo_tool.spec - Fedora RPM spec file.

BUILDING RPM
-------------
If you'd like to build an RPM follow these simple steps:

1) make release

2) you can find the rpm in rpm-build

BUILDING TARBALL
-----------------
1) make maketar

2) you can find the tarball in dist/

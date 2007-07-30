#!/bin/bash
NAME=sm-photo-tool
VERSION=`grep "^version" src/sm_photo_tool.py | awk '{print $3}' | sed 's/\"//g'`
mkdir /tmp/$NAME-$VERSION/
cp LICENSE.TXT /tmp/$NAME-$VERSION/
cp src/sm-photo-tool.py /tmp/$NAME-$VERSION/
cp src/smugmugrc /tmp/$NAME-$VERSION/
pushd /tmp/ > /dev/null
tar czf $NAME-$VERSION.tar.gz $NAME-$VERSION/
rm -rf $NAME-$VERSION/
popd > /dev/null
cp /tmp/$NAME-$VERSION.tar.gz rpm/
rm -f /tmp/$NAME-$VERSION.tar.gz
echo "Tar file located: " `ls rpm/*.tar.gz`

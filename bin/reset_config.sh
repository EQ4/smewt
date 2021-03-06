#!/bin/sh

rm -fr $HOME/.config/Falafelton/Smewt-dev*
rm -fr /tmp/smewt.cache

# for Mac OS X
rm -fr $HOME/Library/Preferences/Smewt*
rm -fr $HOME/Library/Preferences/com.smewt.*


# also remove all *.pyc files
find . -iname "*.pyc" -exec rm {} \;

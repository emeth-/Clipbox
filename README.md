#Latest Binary

OSX:
https://dl.dropboxusercontent.com/u/4238738/clipbox.app.zip

To Enable GIF screencast support, you must run this:
$ brew install imagemagick --disable-openmp --build-from-source

#Info

Dependencies:
- Python 2.7.2 64 bit (http://www.python.org/ftp/python/2.7.2/python-2.7.2-macosx10.6.dmg)
- wxPython2.9-osx-cocoa-py2.7 (http://downloads.sourceforge.net/wxpython/wxPython2.9-osx-2.9.2.4-cocoa-py2.7.dmg)
- py2app (http://pypi.python.org/packages/source/p/py2app/py2app-0.6.3.tar.gz#md5=49a9101ff25fb59d1ba733e329bf502e)
- Imagemagick (brew install imagemagick --disable-openmp --build-from-source)

Run script:
- $ python clipbox.py

Compile binary:
- $ python py2app.py py2app
- (note to self, use python2.7 on current machine)

#Program Information

You can change your backend and shortcuts in the Settings menu option after opening the app.

--------OSX Default Shortcuts----------
- cmd + shift + c = Clipbox Copy (sends cmd + c to foremost window, sends as paste + puts a URL in your clipboard for you to share)
- cmd + shift + x = Clipbox Screenie (Grabs rectangular screenshot that you specify, sends as paste + puts a URL in your clipboard for you to share)

--------Backends Supported----------
- Dropbox
- FTP


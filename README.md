/******************************************/
/*************   Latest Binary   ********/
/******************************************/

OSX:
https://dl.dropboxusercontent.com/u/4238738/clipbox.app.zip

/******************************************/
/*************   The Files   **************/
/******************************************/

clipbox.py - The bread and butter.

toasterbox.py - The notification system.

py2app.py - Compile the scripts into a .app

after_osx_build.py -  Make some changes to the resulting .app from py2app.

/***********************************************/
/*************   How to Compile   **************/
/***********************************************/

Dependencies:
Python 2.7.2 64 bit (http://www.python.org/ftp/python/2.7.2/python-2.7.2-macosx10.6.dmg)
wxPython2.9-osx-cocoa-py2.7 (http://downloads.sourceforge.net/wxpython/wxPython2.9-osx-2.9.2.4-cocoa-py2.7.dmg)
py2app (http://pypi.python.org/packages/source/p/py2app/py2app-0.6.3.tar.gz#md5=49a9101ff25fb59d1ba733e329bf502e)
...

Compile binary:
$ python py2app.py py2app
#note to self, use python2.7 on current machine

Then be sure to move the config.txt to the root directory of the app and update it with your settings.


/****************************************************/
/*************   Program Information   **************/
/****************************************************/

You can change your backend and shortcuts in the Settings menu option after opening the app.

--------OSX Default Shortcuts----------
- cmd + shift + c = Clipbox Copy (sends cmd + c to foremost window, sends as paste + puts a URL in your clipboard for you to share)
- cmd + shift + x = Clipbox Screenie (Grabs rectangular screenshot that you specify, sends as paste + puts a URL in your clipboard for you to share)

--------Backends Supported----------
- Dropbox
- FTP


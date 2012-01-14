
/******************************************/
/*************   The Files   **************/
/******************************************/



clipbox.py - The bread and butter.

cb_API.py - Some 'api' functions that interact with pastes. Should eventually either be consolidated into clipbox.py, or strip more of clipbox.py out into it.

cb_helper.py - Some OS specific functions.

screenshotRect.py - A class to take a screenshot based off a rectangle selected by the user, Windows only

toasterbox.py - The notification system.

UltimateListCtrl.py - List Controls on steroids. Probably a bit out of date, but I'm a bit scared to update as I vaguely recall hacking some things in this file.

py2app.py - Compile the scripts into a .app file for OSX

py2exe.py - Compile the scripts into a .exe file for Windows

after_osx_build.py -  Copy over the images/temp folders into the .app file.

nsisWindowsInstaller.nsi - An installer script for an older version of this program using NSIS for Windows. Currently not up to date.


/***********************************************/
/*************   How to Compile   **************/
/***********************************************/

---OSX---
Libraries I Use:
Python 2.7.2 64 bit (http://www.python.org/ftp/python/2.7.2/python-2.7.2-macosx10.6.dmg)
wxPython2.9-osx-cocoa-py2.7 (http://downloads.sourceforge.net/wxpython/wxPython2.9-osx-2.9.2.4-cocoa-py2.7.dmg)
py2app (http://pypi.python.org/packages/source/p/py2app/py2app-0.6.3.tar.gz#md5=49a9101ff25fb59d1ba733e329bf502e)
Python Imaging Library 1.1.7 Source Kit (http://effbot.org/downloads/Imaging-1.1.7.tar.gz)

Compile:
$ python py2app.py py2app
$ python after_osx_build.py

---WINDOWS---
Libraries I Use:
Python 2.7.2 32 bit (http://www.python.org/ftp/python/2.7.2/python-2.7.2.msi)
wxPython2.8-win32-unicode-py27  (http://downloads.sourceforge.net/wxpython/wxPython2.8-win32-unicode-2.8.12.1-py27.exe)
Python Imaging Library 1.1.7 for Python 2.7 (http://effbot.org/downloads/PIL-1.1.7.win32-py2.7.exe)
py2exe-0.6.9.win32-py2.7.exe (http://sourceforge.net/projects/py2exe/files/py2exe/0.6.9/py2exe-0.6.9.win32-py2.7.exe/download)
pywin32-216.win32-py2.7.exe (http://sourceforge.net/projects/pywin32/files/pywin32/Build216/pywin32-216.win32-py2.7.exe/download)

Compile:
-python py2exe.py py2exe
-Copy contents of 'copy_into_dist' folder into 'dist' folder
-optional, run the NSIS script to create an installer. Probably needs some edits first though.



/****************************************************/
/*************   Program Information   **************/
/****************************************************/




Initial load-up / login options:
Clipbox Password: Stores a 'password' that you can enter on the web / our mobile app to access your pastes
Dropbox Public Folder Path: Full path to your Public Dropbox folder. Does not yet support subfolders. (e.g. /Users/seankooyman/Dropbox/Public/)
Dropbox ID: Your Dropbox ID. Can be found by right clicking an item in your public folder, and clicking 'copy public link', and extracting the number from the url! (e.g. http://dl.dropbox.com/u/4238738/stuff.txt, where 4238738 = your Dropbox ID)

There are two versions, one for the Mac OSX and one for Windows XP or above.

--------Windows Shortcuts----------
**Main 3**
- control + shift + c = Clipbox Copy (sends control + c to foremost window, sends as paste + puts a URL in your clipboard for you to share)
- control + shift + v = Clipbox Paste (loads whatever your last clipbox copy was into your clipboard, sends control + v to foremost window)
- control + shift + r = Recent Pastes (shows list of all pastes you have pending)

**Mutations of Clipbox Copy**
- control + shift + 3 = Clipbox Full Screenie (Grabs screenshot, sends as paste + puts a URL in your clipboard for you to share)
- control + shift + 4 = Clipbox Screenie (Grabs rectangular screenshot that you specify, sends as paste + puts a URL in your clipboard for you to share)
- control + shift + 1 = Clipbox -Copy (sends as paste whatever your current clipboard contents are)
- control + shift + x = Clipbox Cut (Same as Clipbox Copy, but with cut command instead)


--------OSX Shortcuts----------
**Main 3**
- cmd + shift + c = Clipbox Copy (sends cmd + c to foremost window, sends as paste + puts a URL in your clipboard for you to share)
- cmd + shift + v = Clipbox Paste (loads whatever your last clipbox copy was into your clipboard, sends cmd + v to foremost window)
- cmd + shift + r = Recent Pastes (shows list of all pastes you have pending)
- cmd + shift + x = Clipbox Screenie (Grabs rectangular screenshot that you specify, sends as paste + puts a URL in your clipboard for you to share)

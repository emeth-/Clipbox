'''
 *  Copyright (c) 2011
 *  http://teachthe.net/?page_id=1657
 *  Originally developed by Sean Kooyman | teachthe.net(at)gmail.com
 *
 *  License:  GPL version 3.
 *
 *  Permission is hereby granted, free of charge, to any person obtaining a copy
 *  of this software and associated documentation files (the "Software"), to deal
 *  in the Software without restriction, including without limitation the rights
 *  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 *  copies of the Software, and to permit persons to whom the Software is
 *  furnished to do so, subject to the following conditions:
 *
 *  The above copyright notice and this permission notice shall be included in
 *  all copies or substantial portions of the Software.

 *  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 *  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 *  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 *  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 *  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 *  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 *  THE SOFTWARE.
'''
"""
Usage:
    python2.7 freeze.py py2app
"""

import ez_setup
ez_setup.use_setuptools()

import sys
from setuptools import setup

mainscript = 'clipbox.py'

if sys.platform == 'darwin':
    extra_options = dict(
        setup_requires=['py2app'],
        app=[mainscript],
        # Cross-platform applications generally expect sys.argv to
        # be used for opening files.
        options=dict(py2app={"packages": "wx", "iconfile":"images/clipboard.icns", 'semi_standalone':'False', 'includes': 'wx', 'excludes': 'PIL,Image', 'argv_emulation': False})
    )
elif sys.platform == 'win32':
    extra_options = dict(
        setup_requires=['py2exe'],
        app=[mainscript],
    )
else:
     extra_options = dict(
         # Normally unix-like platforms will use "setup.py install"
         # and install the main script as such
         scripts=[mainscript],
     )

setup(
    name="Clipbox",
    **extra_options
)


#####CUSTOM ALTERATIONS AFTER BUILD COMPLETE
import os
if sys.platform == 'darwin':
    def check_if_exists(before):
        for line in before.split('\n'):
            if '<LSUIElement>' in line:
                return True
        return False

    os.system('mkdir dist/clipbox.app/Contents/Resources/temp/')
    os.system('mkdir dist/clipbox.app/Contents/Resources/images/')
    os.system('cp -rf images/ dist/clipbox.app/Contents/Resources/images/')
    os.system('cp -rf static/ dist/clipbox.app/Contents/Resources/static/')
    os.system('cp index.html dist/clipbox.app/Contents/Resources/index.html')
    os.system('cp convert dist/clipbox.app/Contents/Resources/convert')
    os.system('mkdir dist/clipbox.app/Contents/Frameworks/Python.framework/')
    os.system('cp -rf Python.framework/ dist/clipbox.app/Contents/Frameworks/Python.framework/')
    os.system('touch dist/clipbox.app/Contents/Resources/config.txt')

    x = open('dist/clipbox.app/Contents/Info.plist', 'r')
    before = x.read()
    x.close()

    #add flag to hide icon from dock
    if not check_if_exists(before):
        beforeByLine = before.split('\n')
        after = []
        inserted = 0
        for line in beforeByLine:
            if inserted == 0 and '<key>' in line:
                after.append('	<key>LSUIElement</key>')
                after.append('	<string>1</string>')
                inserted = 1
            after.append(line)

        x = open('dist/clipbox.app/Contents/Info.plist', 'w')
        x.write('\n'.join(after))
        x.close()


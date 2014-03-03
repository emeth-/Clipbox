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
    python py2app.py py2app
"""

from setuptools import setup

APP = ['clipbox.py']
DATA_FILES = [(".",["images/clipboard.icns"])]
OPTIONS = {"packages": "wx", "iconfile":"images/clipboard.icns", 'semi_standalone':'False', 'includes': 'wx', 'argv_emulation': False}



setup(
    app=APP,
    version='1.1.0',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
)



#####CUSTOM ALTERATIONS AFTER BUILD COMPLETE

import os

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


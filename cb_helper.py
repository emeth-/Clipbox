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
import platform
if platform.system() == 'Windows':
    settings = {"os_version": "win"}
else:
    settings = {"os_version": "osx"}
import json
import os
import ctypes
import time
import random
import wx

################WINDOWS

if settings['os_version'] == "win":
    import win32process #to close any pre-existing socialpaste.exe processes
    import win32api #to close any pre-existing socialpaste.exe processes
    import win32clipboard #to solve the 'clipboard in use bug' - only way found to catch system error on Windows
    import win32con #for the VK keycodes
    import win32com.client #Sendkeys, to simulate ctrl+c / v
    from ctypes.wintypes import *

    def wait_for_key_up(key):
        ctypes.windll.user32.GetAsyncKeyState.restype = WORD
        ctypes.windll.user32.GetAsyncKeyState.argtypes = [ ctypes.c_char ]
        if key == 'cut':
            while (ctypes.windll.user32.GetAsyncKeyState('X')):
                time.sleep(0.05)
            ctypes.windll.user32.GetAsyncKeyState.argtypes = [ ctypes.c_void_p ]
            while (ctypes.windll.user32.GetAsyncKeyState(get_keycode('control'))):
                time.sleep(0.05)
            return 1
        if key == 'paste':
            while (ctypes.windll.user32.GetAsyncKeyState('V')):
                time.sleep(0.05)
            ctypes.windll.user32.GetAsyncKeyState.argtypes = [ ctypes.c_void_p ]
            while (ctypes.windll.user32.GetAsyncKeyState(get_keycode('control'))):
                time.sleep(0.05)
            return 1
        if key == 'copy':
            while (ctypes.windll.user32.GetAsyncKeyState('C')):
                time.sleep(0.05)
            ctypes.windll.user32.GetAsyncKeyState.argtypes = [ ctypes.c_void_p ]
            while (ctypes.windll.user32.GetAsyncKeyState(get_keycode('control'))):
                time.sleep(0.05)
            return 1
        return 0

    def send_key(key):
        shell = win32com.client.Dispatch("WScript.Shell")
        if key == 'copy':
            shell.SendKeys("^c")
        if key == 'cut':
            shell.SendKeys("^x")
        if key  == 'paste':
            shell.SendKeys("^v")

    def get_keycode(key):
        if key == "control":
            return win32con.VK_CONTROL
        elif key == "control_mod":
            return win32con.MOD_CONTROL
        elif key == "shift_mod":
            return win32con.MOD_SHIFT
        elif key == "x":
            return 0x58
        elif key == "c":
            return 0x43
        elif key == "a":
            return 0x41
        elif key == "v":
            return 0x56
        elif key == "r":
            return 0x52
        elif key == "1":
            return 0x31
        elif key == "3":
            return 0x33
        elif key == "4":
            return 0x34
        return None

    def kill_other_sp_exe():
        processes = win32process.EnumProcesses()    # get PID list
        mypid = win32api.GetCurrentProcessId()
        for pid in processes:
            if pid != mypid:
                try:
                    handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, pid)
                    exe = win32process.GetModuleFileNameEx(handle, 0)
                    if "socialpaste.exe" in exe.lower():
                        win32process.TerminateProcess(handle,0)
                except:
                    pass

    def catch_clipboard_in_use_bug():
        '''
            This section catches the 'clipboard in use bug'
            and repeatedly 'hits' it until Windows fixes it
        '''
        cbOpened = False
        while not cbOpened:
            try:
                win32clipboard.OpenClipboard(0)
                cbOpened = True
                win32clipboard.CloseClipboard()
            except Exception, err:
                print 'Clipboard in use error: Waiting...'
                # If access is denied, that means that the clipboard is in use.
                # Keep trying until it's available.
                if err[0] == 5:  #Access Denied
                    pass
                    print 'waiting on clipboard...'
                    # wait on clipboard because something else has it. we're waiting a
                    # random amount of time before we try again so we don't collide again
                    time.sleep( random.random()/50 )
                elif err[0] == 1418:  #doesn't have board open
                    pass
                elif err[0] == 0:  #open failure
                    pass
                else:
                    print 'ERROR in Clipboard section of readcomments: %s' % err


#####################OSX
if settings['os_version'] == "osx":
    import os
    def wait_for_key_up(key):
        #wait for user to release keys after triggering hotkey. How to get keystate from OSX?
        time.sleep(1)
        return 1

    def send_key(key):
        import os
        if key == 'copy':
            cmd = """
            osascript -e 'tell application "System Events" to keystroke "c" using {command down}'
            """
            os.system(cmd)
        if key  == 'paste':
            cmd = """
            osascript -e 'tell application "System Events" to keystroke "v" using {command down}'
            """
            os.system(cmd)

    def get_keycode(key):
        if key == "control_mod": #command
            return wx.WXK_START
        elif key == "shift_mod":
            return wx.MOD_SHIFT
        #NOT WORKING ALT
        elif key == "alt": #alt/option
            return wx.MOD_ALT #wx.WXK_ALT
        elif key == "a":
            return ord('A')
        elif key == "x":
            return ord('X')
        elif key == "c":
            return ord('C')
        elif key == "v":
            return ord('V')
        elif key == "r":
            return ord('R')
        elif key == "1":
            return ord('1')
        elif key == "3":
            return ord('3')
        elif key == "4":
            return ord('4')
        return None

    def kill_other_sp_exe():
        #not needed for osx
        pass

    def catch_clipboard_in_use_bug():
        #not needed for osx
        pass

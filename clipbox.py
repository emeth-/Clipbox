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

import wx, re, sys, glob, random, urllib2, Image, urllib
import os,stat
import time
import httplib, mimetypes #fun internet stuffs
import toasterbox #popup in lower right for new pastes
from datetime import datetime
import webbrowser #to open http links in user's preferred browser
import shutil #to copy files to the sent directory
import string
import zipfile
import screenshotRect
from time import gmtime, strftime
import base64, md5

import cb_API
import cb_helper

clipboxWindow = None
weburl = "http://teachthe.net/?page_id=1657"

settings['db_public_path'] = ""
settings['db_public_url'] = ""
settings['name'] = ""


class mainFrame(wx.Frame, wx.lib.mixins.listctrl.ColumnSorterMixin):
    global clipboxWindow, settings
    def __init__(self, parent, id, title):
        style = wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER
        self.window = wx.Frame.__init__(self, parent, id, title, size=(450,555), style=style)

        self.regHotKey()
        self.Bind(wx.EVT_HOTKEY, self.handleHotKey, id=self.hotCopy)
        self.Bind(wx.EVT_HOTKEY, self.handleHotKey, id=self.hotScreenRect)

        icon1 = wx.Icon("images/clipboard.png", wx.BITMAP_TYPE_PNG)
        self.SetIcon(icon1)

        self.tskic = MyTaskBarIcon(self)
        font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        #BEGIN

        self.Bind(wx.EVT_CLOSE,self.OnClose)

        wx.GetApp().Bind(wx.EVT_QUERY_END_SESSION, self.onFullClose)
        wx.GetApp().Bind(wx.EVT_END_SESSION, self.onFullClose)
        self.Bind(wx.EVT_CLOSE, self.onFullClose)

        wx.CallAfter(self.createSubWindows)
        self.Layout()

    def createSubWindows(self):
        self.toasterWindow = ToasterBox(None, -1, 'ToasterBox')

    def onFullClose(self, event):
        for w in wx.GetTopLevelWindows():
            w.Destroy()
        self.Destroy()

    def OnClose(self,event):
        self.Show(False)
        event.Veto()

    def regHotKey(self):
        mod_control = cb_helper.get_keycode('control_mod')
        mod_shift = cb_helper.get_keycode('shift_mod')
        self.hotCopy = 100
        self.RegisterHotKey(
            self.hotCopy, 
            mod_control | mod_shift, 
            cb_helper.get_keycode('c')) 

        self.hotScreenRect = 104
        self.RegisterHotKey(
            self.hotScreenRect, #a unique ID for this hotkey
            mod_control | mod_shift, #the modifier keys
            cb_helper.get_keycode('x'))



    def handleHotKey(self, evt):
        eventId = evt.GetId()
        if eventId == 104: #hotScreenRect

            if settings['os_version'] == 'osx':
                cb_helper.send_key('screenshot')
                self.onHotCopy()

            elif settings['os_version'] == 'win':
                ssdlg = screenshotRect.Screen_Capture(None)
                ssdlg.ShowModal()
                ssdlg.Raise()
                x1 = min(ssdlg.c1.x, ssdlg.c2.x)
                x2 = max(ssdlg.c1.x, ssdlg.c2.x)
                y1 = min(ssdlg.c1.y, ssdlg.c2.y)
                y2 = max(ssdlg.c1.y, ssdlg.c2.y)
                captureBmapSize = (x2-x1, y2-y1)
                #captureBmapSize = (wx.SystemSettings.GetMetric( wx.SYS_SCREEN_X ),
                #wx.SystemSettings.GetMetric( wx.SYS_SCREEN_Y ) )
                captureStartPos = (x1, y1)    # Arbitrary U-L position anywhere within the screen
                scrDC = wx.ScreenDC()
                scrDcSize = scrDC.Size
                scrDcSizeX, scrDcSizeY = scrDcSize

                # Cross-platform adaptations :
                scrDcBmap     = scrDC.GetAsBitmap()
                scrDcBmapSize = scrDcBmap.GetSize()

                # Check if scrDC.GetAsBitmap() method has been implemented on this platform.
                if   scrDcBmapSize == (0, 0) :      # Not implemented :  Get the screen bitmap the long way.

                    scrDcBmap = wx.EmptyBitmap( *scrDcSize )
                    scrDcBmapSizeX, scrDcBmapSizeY = scrDcSize

                    memDC = wx.MemoryDC( scrDcBmap )

                    memDC.Blit( 0, 0,                           # Copy to this start coordinate.
                                scrDcBmapSizeX, scrDcBmapSizeY, # Copy an area this size.
                                scrDC,                          # Copy from this DC's bitmap.
                                0, 0,                    )      # Copy from this start coordinate.

                    memDC.SelectObject( wx.NullBitmap )     # Finish using this wx.MemoryDC.
                                                            # Release scrDcBmap for other uses.
                else :
                    scrDcBmap = scrDC.GetAsBitmap()     # So easy !  Copy the entire Desktop bitmap.

                bitmap = scrDcBmap.GetSubBitmap( wx.RectPS( captureStartPos, captureBmapSize ) )
                bitmap.SaveFile( 'temp/screenshot.png', wx.BITMAP_TYPE_PNG )

                bd = wx.BitmapDataObject()
                bimgsucc = bd.SetBitmap(bitmap)
                if wx.TheClipboard.Open():
                    successb = wx.TheClipboard.SetData(bd)
                    wx.TheClipboard.Close()

                self.onHotCopy()
                
        if eventId == 100: #hotCopy
            cb_helper.wait_for_key_up('copy')
            cb_helper.send_key('copy')
            time.sleep(1.5)
            self.onHotCopy()

    def onHotCopy(self):
        global settings
        cb_helper.catch_clipboard_in_use_bug()
        if wx.TheClipboard.Open():
            td = wx.TextDataObject()
            fd = wx.FileDataObject()
            bd = wx.BitmapDataObject()
            successt = wx.TheClipboard.GetData(td)
            successf = wx.TheClipboard.GetData(fd)
            successb = wx.TheClipboard.GetData(bd)
            wx.TheClipboard.Close()
            text = td.GetText()
            ftext = ''.join(fd.GetFilenames())
            bimg = bd.GetBitmap() #this is a wx.Bitmap
            pasteText = text

        #on OSX, in a file 'copy' event, both these variables are true
        if successt and successf:
            successt = False
            successb = False

        self.Show(False)
        if not os.path.exists(settings['db_public_path'] + '.clipbox/'):
            os.makedirs(settings['db_public_path'] + '.clipbox/')
            
        if successt:
            appd = ""
            if len(pasteText) > 20:
                appd = "..."
            meta = ""+pasteText[:20].strip()
            if len(pasteText) > 20:
                meta = meta + "..."
            meta = meta + " ("+str(len(pasteText))+" chars)"
            pasteID = strftime("%Y-%m-%d_%H-%M-%S", gmtime())+''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(6))

            result = cb_API.add_paste_to_db('text', meta, pasteID, settings['db_public_path']+'.clipbox/', settings['name'])
            try:
                datafo = open(settings['db_public_path']+'.clipbox/'+pasteID, 'w')
                datafo.write(pasteText)
                datafo.close()
                public_paste_url = 'http://dl.dropbox.com/u/'+settings['db_public_url']+'/' + '.clipbox/'+pasteID
                clipboxWindow.toasterWindow.RunToaster('Download URL copied to your Clipboard!', 'text')
                td = wx.TextDataObject()
                td.SetText(public_paste_url)
                if wx.TheClipboard.Open():
                    successt = wx.TheClipboard.SetData(td)
                    wx.TheClipboard.Close()
            except:
                clipboxWindow.toasterWindow.RunToaster('An Error Occurred.', 'text')
                
        if successf:
            allFileNames = fd.GetFilenames()
            ftext = allFileNames[0]
            pasteID =  os.path.basename(ftext)
            #check through .pastes file, if pasteID already exists, overwrite it
            try:
                if len(allFileNames)>1:
                    compression = zipfile.ZIP_DEFLATED
                    zfname = settings['db_public_path']+'.clipbox/' + pasteID
                    zf = zipfile.ZipFile(zfname, mode='w')
                    try:
                        for fnm in allFileNames:
                            zf.write(str(fnm), os.path.basename(str(fnm)), compress_type=compression)
                    finally:
                        zf.close()
                    fileloc = settings['db_public_path']+'.clipbox/' + pasteID
                    fname = os.path.basename(ftext) + ".zip"
                else:
                    shutil.copyfile(ftext, settings['db_public_path']+'.clipbox/'+pasteID)
                    fname = os.path.basename(ftext)

                size = convert_bytes(os.path.getsize(settings['db_public_path']+'.clipbox/' + pasteID))
                meta = fname + " ("+str(size)+")"
                result = cb_API.add_paste_to_db('file', meta, pasteID, settings['db_public_path']+'.clipbox/', settings['name'])

                public_paste_url = 'http://dl.dropbox.com/u/'+settings['db_public_url']+'/' + '.clipbox/'+pasteID
                td = wx.TextDataObject()
                td.SetText(public_paste_url)
                if wx.TheClipboard.Open():
                    successt = wx.TheClipboard.SetData(td)
                    wx.TheClipboard.Close()
                clipboxWindow.toasterWindow.RunToaster('Download URL copied to your Clipboard!', 'file')
            except:
                clipboxWindow.toasterWindow.RunToaster('An Error Occurred.', 'file')
                
        if successb:
            bmpimg = wx.ImageFromBitmap(bimg)
            width = bmpimg.GetWidth()
            height = bmpimg.GetHeight()
            tmpPasteName = strftime("%Y-%m-%d_%H-%M-%S", gmtime())+''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(6))
            bimg.SaveFile('temp/'+tmpPasteName+'.png', wx.BITMAP_TYPE_PNG)
            fullpath = os.getcwd() + "/temp/"+tmpPasteName+".png"
            size = convert_bytes(os.path.getsize('temp/'+tmpPasteName+'.png'))
            meta = str(width)+"x"+str(height)+" pixels ("+str(size)+")"
            pasteID = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(6)) + '_' + os.path.basename(fullpath)
            result = cb_API.add_paste_to_db('image', meta, pasteID, settings['db_public_path']+'.clipbox/', settings['name'])
            try:
                shutil.copyfile(fullpath, settings['db_public_path']+'.clipbox/'+pasteID)
                public_paste_url = 'http://dl.dropbox.com/u/'+settings['db_public_url']+'/' + '.clipbox/'+pasteID
                td = wx.TextDataObject()
                td.SetText(public_paste_url)
                if wx.TheClipboard.Open():
                    successt = wx.TheClipboard.SetData(td)
                    wx.TheClipboard.Close()
                clipboxWindow.toasterWindow.RunToaster('Download URL copied to your Clipboard!', 'image')
            except:
                clipboxWindow.toasterWindow.RunToaster('An Error Occurred.', 'image')


class MyTaskBarIcon(wx.TaskBarIcon):
    global weburl, clipboxWindow, settings
    def __init__(self, frame):
        wx.TaskBarIcon.__init__(self)

        self.frame = frame

        myimage = wx.Bitmap('images/spsprite.png', wx.BITMAP_TYPE_PNG)
        submyimage = myimage.GetSubBitmap(wx.Rect(0,0,16,16))
        myicon = wx.EmptyIcon()
        myicon.CopyFromBitmap(submyimage)
        self.SetIcon(myicon, 'ClipBox')
        self.Bind(wx.EVT_MENU, self.hotCopy, id=20)
        self.Bind(wx.EVT_MENU, self.gotoweb, id=8)
        self.Bind(wx.EVT_MENU, self.showPreferences, id=14)
        self.Bind(wx.EVT_MENU, self.OnTaskBarClose, id=3)
        self.Bind(wx.EVT_MENU, self.deleteAllPastes, id=2)
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_click)


    def OnTaskBarClose(self, event):
        self.RemoveIcon()
        self.frame.Destroy()
        clipboxWindow.toasterWindow.Destroy()
        clipboxWindow.Destroy()
        for w in wx.GetTopLevelWindows():
            w.Destroy()
            
    def deleteAllPastes(self, event):
        dlg = wx.MessageDialog(clipboxWindow, 
            "Are you sure you want to delete all your pastes?",
            "Confirm Delete", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            result = cb_API.delete_all_pastes(settings['db_public_path']+'.clipbox/', settings['name'])
            wx.MessageBox("All pastes deleted. Isn't that clean feeling lovely?", 'Finished.', wx.OK | wx.ICON_INFORMATION)
            

    def on_left_click(self, e):
        self.PopupMenu(self.CreatePopupMenu())

    def CreatePopupMenu(self):
        tbmenu = wx.Menu()
        mip = wx.MenuItem(tbmenu, 20, 'ClipBox Copy')
        font = mip.GetFont()
        font.SetWeight(wx.BOLD)
        mip.SetFont(font)
        tbmenu.AppendItem(mip)
        tbmenu.Append(2, 'Delete All Pastes')
        tbmenu.Append(14, 'Preferences...')
        tbmenu.Append(8, 'Go To Website')
        tbmenu.Append(3, 'Exit')
        return tbmenu

    def hotCopy(self, event):
        global clipboxWindow
        clipboxWindow.onHotCopy()

    def gotoweb(self, event):
        global weburl
        webbrowser.open(weburl)

    def showPreferences(self, event):
        logind = LoginWin(None, -1, "Preferences", logout=1)
        logind.ShowModal()
        logind.Destroy()

class ToasterBox(wx.Frame):
   def __init__(self, parent, id, title):
       wx.Frame.__init__(self, parent, id, title)
       self.panel = wx.Panel(self)
       self.Show(False)

   def RunToaster(self, poptext, type):
        toaster = toasterbox.ToasterBox(self, tbstyle=toasterbox.TB_COMPLEX)
        toaster.SetPopupPositionByInt(3)
        toaster.SetPopupPauseTime(5000)

        tbpanel = toaster.GetToasterBoxWindow()
        panel = wx.Panel(tbpanel, -1)

        sizer = wx.BoxSizer(wx.VERTICAL)
        horsizer1 = wx.BoxSizer(wx.HORIZONTAL)

        if type == "file":
            myimage = wx.Bitmap("images/file_icon_50.png", wx.BITMAP_TYPE_PNG)
        elif type == "text":
            myimage = wx.Bitmap("images/text_icon_50.png", wx.BITMAP_TYPE_PNG)
        elif type == "image":
            myimage = wx.Bitmap("images/image_icon_50.png", wx.BITMAP_TYPE_PNG)
        else:
            myimage = wx.Bitmap("images/text_icon_50.png", wx.BITMAP_TYPE_PNG)
        stbmp = wx.StaticBitmap(panel, -1, myimage)
        horsizer1.Add(stbmp, 0)

        sttext = wx.StaticText(panel, -1, poptext)
        sttext.SetFont(wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "Verdana"))
        horsizer1.Add(sttext, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        sizer.Add((0,5))
        sizer.Add(horsizer1, 0, wx.EXPAND)

        sizer.Layout()
        panel.SetSizer(sizer)

        toaster.AddPanel(panel)
        toaster.Play()

class LoginWin(wx.Dialog):
    global settings
    def __init__(self, parent, id, title,logout=0):
        global settings
        wx.Dialog.__init__(self, parent, id, title,  size=(660,356))
        icon1 = wx.Icon("images/clipboard.png", wx.BITMAP_TYPE_PNG)
        self.SetIcon(icon1)
        dbox_location = get_dropbox_location()
        if settings['db_public_path'] == "":
            if settings['os_version'] == 'osx':
                settings['db_public_path'] = dbox_location + '/Public/'
            elif settings['os_version'] == 'win':
                settings['db_public_path'] = dbox_location + '\\Public\\'
        if settings['db_public_url'] == "":
            settings['db_public_url'] = ''

        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

        #added to osx
        self.backImg = wx.Bitmap("images/loginbg.png", type = wx.BITMAP_TYPE_PNG)
        self.Bind(wx.EVT_PAINT, self.OnEraseBackground)


        self.stName = wx.StaticText(self, -1, 'Clipbox Password', pos=(465, 20))
        self.stName.SetForegroundColour((61,110,186))
        self.tbName = wx.TextCtrl(self, -1, pos=(465, 40))

        self.stdb_public_path = wx.StaticText(self, -1, 'Dropbox Public Folder Path', pos=(463, 120))
        self.stdb_public_path.SetForegroundColour((61,110,186))
        self.tbdb_public_path = wx.TextCtrl(self, -1, pos=(465, 140))

        self.stdb_public_url = wx.StaticText(self, -1, 'Dropbox ID', pos=(463, 170))
        self.stdb_public_url.SetForegroundColour((61,110,186))
        self.tbdb_public_url = wx.TextCtrl(self, -1, pos=(465, 190))

        self.butSub = wx.Button(self, 13, 'Submit', pos=(477, 220))

        if settings['os_version'] == 'win':
            self.stName.SetBackgroundColour('#FAFAF6')
            self.stdb_public_path.SetBackgroundColour('#FAFAF6')
            self.stdb_public_url.SetBackgroundColour('#FAFAF6')

        self.tbName.SetValue(settings['name'])
        self.tbdb_public_path.SetValue(settings['db_public_path'])
        self.tbdb_public_url.SetValue(settings['db_public_url'])

        self.Raise()

        self.Bind (wx.EVT_BUTTON, self.submitInfo, id=13)

    def OnEraseBackground(self, event):
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.backImg, 0, 0, True)

    def submitInfo(self, event):
        global settings

        if not os.path.isdir(self.tbdb_public_path.GetValue()):
            #invalid directory. Show error somehow.
            pass
        else:
            self.Show(False)
            settings['name'] = self.tbName.GetValue()
            settings['db_public_path'] = self.tbdb_public_path.GetValue()
            settings['db_public_url'] = self.tbdb_public_url.GetValue()

            if settings['os_version'] == 'osx':
                if settings['db_public_path'][-1:] != '/':
                    settings['db_public_path'] = settings['db_public_path'] + '/'
            elif settings['os_version'] == 'win':
                if settings['db_public_path'][-1:] != '\\':
                    settings['db_public_path'] = settings['db_public_path'] + '\\'

            saveMyInfo(self)
            self.EndModal(True)




def loadMyInfo(self):
    global settings
    try:
        spdatafile = open('.spdata', 'r')
        jsoncode = spdatafile.read()
        spdatafile.close()
        data = json.loads(jsoncode)
    except:
        jsoncode = json.dumps({'name': '', 'db_public_path': '', 'db_public_url': ''})
        data = json.loads(jsoncode)
    settings['name'] = data['name']
    settings['db_public_path'] = data['db_public_path']
    settings['db_public_url'] = data['db_public_url']

def saveMyInfo(self):
    global settings
    try:
        jsoncode = json.dumps({'name': settings['name'], 'db_public_path': settings['db_public_path'], 'db_public_url': settings['db_public_url']})
        spdatafile = open('.spdata', 'w')
        spdatafile.write(jsoncode)
        spdatafile.close()
    except:
        pass

def get_dropbox_location():
    global settings
    if settings['os_version'] == 'osx':
        HOST_DB_PATH = os.path.expanduser(r'~/.dropbox/host.db')
    elif settings['os_version'] == 'win':
        HOST_DB_PATH = os.path.expandvars(r'%APPDATA%\Dropbox\host.db')
    f = open(HOST_DB_PATH, "r")
    try:
        ignore = f.readline()
        location_line = f.readline().strip()
        return base64.decodestring(location_line).decode('utf8')
    finally:
        f.close()
    return ""

def convert_bytes(bytes):
    bytes = float(bytes)
    if bytes >= 1099511627776:
        terabytes = bytes / 1099511627776
        size = '%.1fT' % terabytes
    elif bytes >= 1073741824:
        gigabytes = bytes / 1073741824
        size = '%.1fG' % gigabytes
    elif bytes >= 1048576:
        megabytes = bytes / 1048576
        size = '%.1fM' % megabytes
    elif bytes >= 1024:
        kilobytes = bytes / 1024
        size = '%.1fK' % kilobytes
    else:
        size = '%.1fb' % bytes
    return size

class MyApp(wx.App):
    global settings, clipboxWindow
    def OnInit(self):
        global settings, clipboxWindow

        loadMyInfo(self)

        forcelogin = 0
        if settings['db_public_path'] != '':
            if not os.path.isdir(settings['db_public_path']):
                forcelogin = 1
            else:
                clipboxWindow = mainFrame(None, -1, 'ClipBox') #already logged in
        else:
            forcelogin = 1

        if forcelogin == 1:
            logind = LoginWin(None, -1, "Initialize")
            logind.ShowModal()
            clipboxWindow = mainFrame(None, -1, 'ClipBox')

        return True

    def onCloseIt(self, event):
        for w in wx.GetTopLevelWindows():
            w.Destroy()
        self.Destroy()

app = MyApp(0)
app.MainLoop()

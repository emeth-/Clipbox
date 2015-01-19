import json
import wx
import random
import os
import time

# For the Notifications
from Foundation import NSUserNotification, NSObject, NSDictionary
from Foundation import NSUserNotificationCenter

import webbrowser #to open http links in user's preferred browser
import shutil #to copy files to the sent directory

#for the settings webserver UI (Yeah. I'd go this far just to avoid having to make a native GUI.)
from bottle import route, run, static_file, request
import thread

from ftplib import FTP

settings = {
    "backend": "ftp",
    "ftp_host": "", #ftp backend
    "ftp_public_url": "", #ftp backend
    "ftp_username": "", #ftp backend
    "ftp_password": "", #ftp backend
    "ftp_remote_dir": "", #ftp backend
    "db_public_path": "", #dropbox backend
    "db_public_url": "", #dropbox backend
    "key_first_mod": "MOD_CMD",
    "key_second_mod": "MOD_SHIFT",
    "key_copy": "C",
    "key_screenshot": "X",
}

def load_settings():
    global settings
    try:
        spdatafile = open('config.txt', 'r')
        jsoncode = spdatafile.read()
        spdatafile.close()
        settings = json.loads(jsoncode)
    except:
        pass

class mainFrame(wx.Frame):
    global settings
    def __init__(self, parent, id, title):
        style = wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER
        self.window = wx.Frame.__init__(self, parent, id, title, size=(450,555), style=style)

        self.regHotKey()
        self.Bind(wx.EVT_HOTKEY, self.handleHotKey, id=self.hotCopy)
        self.Bind(wx.EVT_HOTKEY, self.handleHotKey, id=self.hotScreenRect)

        icon1 = wx.Icon("images/clipbox_icon.png", wx.BITMAP_TYPE_PNG)
        self.SetIcon(icon1)

        self.tskic = MyTaskBarIcon(self)

        self.Bind(wx.EVT_CLOSE,self.OnClose)

        wx.GetApp().Bind(wx.EVT_QUERY_END_SESSION, self.onFullClose)
        wx.GetApp().Bind(wx.EVT_END_SESSION, self.onFullClose)
        self.Bind(wx.EVT_CLOSE, self.onFullClose)

        wx.CallAfter(self.StartServer) 
        self.Layout()
        
    def checkSettings(self):
        global settings
        pop_settings_ui = False
        if settings['backend'] == "ftp":
            if settings['ftp_host'] == '' or settings['ftp_public_url'] == '' or settings['ftp_username'] == '' or settings['ftp_password'] == '':
                pop_settings_ui = True
        else:
            if settings['db_public_path'] == '' or settings['db_public_url'] == '':
                    pop_settings_ui = True
            else:
                if not os.path.isdir(settings['db_public_path']):
                    pop_settings_ui = True
        if pop_settings_ui:
            webbrowser.open("http://localhost:8181/")

    def onFullClose(self, event):
        for w in wx.GetTopLevelWindows():
            w.Destroy()
        self.Destroy()
        
    def StartServer(self): 
        thread.start_new_thread(self._StartServe, ())
        self.checkSettings()
        
    def _StartServe(self):
        print "starting server thread..." 

        @route('/settings.js', method='GET')
        def settingsjs():
            spdatafile = open('config.txt', 'r')
            settings_data = spdatafile.read()
            spdatafile.close()
            return "load_current_settings("+json.dumps(settings_data)+");"

        @route('/save', method='POST')
        def save():
            data = request.forms.get('data')
            spdatafile = open('config.txt', 'w')
            spdatafile.write(data)
            spdatafile.close()
            load_settings()
            return json.dumps({"status":"success"})
        
        @route('/')
        def base():
            return static_file("index.html", root='./')
        
        @route('/static/:filename#.*#')
        def send_static(filename):
            return static_file(filename, root='./static/')

        run(host='0.0.0.0', port=8181)

    def OnClose(self,event):
        self.Show(False)
        event.Veto()

    def regHotKey(self):
        global settings

        self.hotCopy = 100
        self.RegisterHotKey(
            self.hotCopy,
            eval("wx."+settings['key_first_mod']) | eval("wx."+settings['key_second_mod']),
            ord(settings['key_copy']))

        self.hotScreenRect = 104
        self.RegisterHotKey(
            self.hotScreenRect, #a unique ID for this hotkey
            eval("wx."+settings['key_first_mod']) | eval("wx."+settings['key_second_mod']),
            ord(settings['key_screenshot']))

    def handleHotKey(self, evt):
        eventId = evt.GetId()
        if eventId == self.hotScreenRect: 
            os.system('screencapture -c -i') #allow user to draw rectangle screenshot, copy image to clipboard
            self.onHotCopy()
        if eventId == self.hotCopy: 
            time.sleep(1)
            os.system("""osascript -e 'tell application "System Events" to keystroke "c" using {command down}'""") #send copy command.
            time.sleep(1.5)
            self.onHotCopy()

    def copyToClipboard(self, text):
        td = wx.TextDataObject()
        td.SetText(text)
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(td)
            wx.TheClipboard.Close()
            return True
        return False
            
    def onHotCopy(self):
        global settings
        if wx.TheClipboard.Open():
            td = wx.TextDataObject()
            fd = wx.FileDataObject()
            bd = wx.BitmapDataObject()
            successt = wx.TheClipboard.GetData(td)
            successf = wx.TheClipboard.GetData(fd)
            successb = wx.TheClipboard.GetData(bd)
            wx.TheClipboard.Close()
            text = td.GetText()
            bimg = bd.GetBitmap() #this is a wx.Bitmap
            pasteText = text

        self.Show(False)
        if settings['backend'] == "dropbox":
            #if clipbox dropbox folder doesn't exist, create it
            if not os.path.exists(settings['db_public_path'] + '.clipbox/'):
                os.makedirs(settings['db_public_path'] + '.clipbox/')

        if successf:
            allFileNames = fd.GetFilenames()
            pasteID =  os.path.basename(allFileNames[0])
            try:
                if settings['backend'] == "ftp":
                    ftp_conn = FTP(settings['ftp_host'], settings['ftp_username'], settings['ftp_password'])
                    ftp_conn.storbinary('STOR '+settings['ftp_remote_dir']+pasteID, open(allFileNames[0], 'rb'))
                    public_paste_url = settings['ftp_public_url']+pasteID
                else:
                    shutil.copyfile(allFileNames[0], settings['db_public_path']+'.clipbox/'+pasteID)
                    public_paste_url = 'http://dl.dropbox.com/u/'+settings['db_public_url']+'/' + '.clipbox/'+pasteID
    
                self.copyToClipboard(public_paste_url)
                notify('Download URL copied to your Clipboard!')
            except:
                notify('An Error Occurred.')
        elif successt:
            
            pasteID = time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime())+''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for x in range(6))
            try:
                if settings['backend'] == "ftp":
                    tmpf = open("tmptxt", 'w')
                    tmpf.write(pasteText)
                    tmpf.close()
                    public_paste_url = settings['ftp_public_url']+pasteID
                    self.copyToClipboard(public_paste_url)
                    ftp_conn = FTP(settings['ftp_host'], settings['ftp_username'], settings['ftp_password'])
                    ftp_conn.storbinary('STOR '+settings['ftp_remote_dir']+pasteID, open("tmptxt"))
                else:
                    datafo = open(settings['db_public_path']+'.clipbox/'+pasteID, 'w')
                    datafo.write(pasteText)
                    datafo.close()
                    public_paste_url = 'http://dl.dropbox.com/u/'+settings['db_public_url']+'/' + '.clipbox/'+pasteID
                    self.copyToClipboard(public_paste_url)
                notify('Download URL copied to your Clipboard!')
            except:
                notify('An Error Occurred.')
        elif successb:
            pasteID = time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime())+''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for x in range(6))+".png"
            bimg.SaveFile('temp/'+pasteID, wx.BITMAP_TYPE_PNG)
            fullpath = os.getcwd() + "/temp/"+pasteID
            try:
                if settings['backend'] == "ftp":
                    ftp_conn = FTP(settings['ftp_host'], settings['ftp_username'], settings['ftp_password'])
                    ftp_conn.storbinary('STOR '+settings['ftp_remote_dir']+pasteID, open(fullpath, 'rb'))
                    public_paste_url = settings['ftp_public_url']+pasteID
                else:
                    shutil.copyfile(fullpath, settings['db_public_path']+'.clipbox/'+pasteID)
                    public_paste_url = 'http://dl.dropbox.com/u/'+settings['db_public_url']+'/' + '.clipbox/'+pasteID
                td = wx.TextDataObject()
                td.SetText(public_paste_url)
                if wx.TheClipboard.Open():
                    successt = wx.TheClipboard.SetData(td)
                    wx.TheClipboard.Close()
                notify('Download URL copied to your Clipboard!')
            except ImportWarning:
                notify('An Error Occurred.')

class MyTaskBarIcon(wx.TaskBarIcon):
    def __init__(self, frame):
        wx.TaskBarIcon.__init__(self)

        self.frame = frame

        myimage = wx.Bitmap('images/clipbox_icon.png', wx.BITMAP_TYPE_PNG)
        submyimage = myimage.GetSubBitmap(wx.Rect(0,0,16,16))
        myicon = wx.EmptyIcon()
        myicon.CopyFromBitmap(submyimage)
        self.SetIcon(myicon, 'ClipBox')
        self.Bind(wx.EVT_MENU, self.gotoweb, id=8)
        self.Bind(wx.EVT_MENU, self.showSettings, id=14)
        self.Bind(wx.EVT_MENU, self.OnTaskBarClose, id=3)
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_click)

    def OnTaskBarClose(self, event):
        self.RemoveIcon()
        self.frame.Destroy()
        for w in wx.GetTopLevelWindows():
            w.Destroy()

    def on_left_click(self, e):
        self.PopupMenu(self.CreatePopupMenu())

    def CreatePopupMenu(self):
        tbmenu = wx.Menu()
        tbmenu.Append(14, 'Settings...')
        tbmenu.Append(8, 'Go To Website')
        tbmenu.Append(3, 'Exit')
        return tbmenu

    def gotoweb(self, event):
        webbrowser.open("https://github.com/seanybob/Clipbox")

    def showSettings(self, event):
        webbrowser.open("http://localhost:8181/")

def notify(text):

    notification = NSUserNotification.alloc().init()
    notification.setTitle_('Clipbox')
    notification.setInformativeText_(text)
    center = NSUserNotificationCenter.defaultUserNotificationCenter()
    center.deliverNotification_(notification)

class MyApp(wx.App):
    def OnInit(self):
        load_settings()
        mainFrame(None, -1, 'ClipBox') #already logged in
        return True

    def onCloseIt(self, event):
        for w in wx.GetTopLevelWindows():
            w.Destroy()
        self.Destroy()

app = MyApp(0)
app.MainLoop()

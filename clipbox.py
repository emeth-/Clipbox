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
import wx.lib.mixins.listctrl as listmix  #listctrl add-ons
import UltimateListCtrl as ULC #greatly expands what we can do with listctrls
import httplib, mimetypes #fun internet stuffs
import toasterbox #popup in lower right for new pastes
from datetime import datetime
import webbrowser #to open http links in user's preferred browser
import shutil #to copy files to the sent directory
import string
import zipfile
#import zlib #superfluous? If so, delete
import screenshotRect
from time import gmtime, strftime
import base64

import cb_API
import cb_helper

#Global Variables. A lot more than I should have.
clipboxWindow = ""
pastelistglob = []
ctrlshiftv = []
logind = wx.Dialog
tbmenustr = [] #contains the paste info in the menu
tbitemcnt = 0
tbitemtype = "text"
name = ""
db_path = ""
db_public_path = ""
db_public_url = ""
lastPaste = ""
weburl = "http://teachthe.net/?page_id=1657"


sshotx1 = 0
sshoty1 = 0

sshotx2 = 0
sshoty2 = 0

settings['db_path'] = ""
settings['db_public_path'] = ""
settings['db_public_url'] = ""
settings['name'] = ""

if settings['os_version'] == 'osx':
    class myPasteList(ULC.UltimateListCtrl):
        def __init__(self, parent):
            self.par = parent
            ULC.UltimateListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.LC_SORT_DESCENDING, extraStyle=ULC.ULC_HAS_VARIABLE_ROW_HEIGHT)

        def ColumnSorter(self, key1, key2):
            item1 = self.par.pastedict[key1]
            item2 = self.par.pastedict[key2]
            found = 0
            time1 = 0
            time2 = 0
            for pinf in pastelistglob:
                if pinf[2] == item1:
                    found = 1
                    time1 = pinf[3]

            found = 0
            for pinf in pastelistglob:
                if pinf[2] == item2:
                    found = 1
                    time2 = pinf[3]
            if time1 < time2:
                return 1
            else:
                return -1
        def RefreshRows(self): #to fill in for listmix.ListRowHighlighter
            pass


if settings['os_version'] == 'win':
    class myPasteList(ULC.UltimateListCtrl, listmix.ListRowHighlighter):
        def __init__(self, parent):
            self.par = parent
            ULC.UltimateListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.LC_SORT_DESCENDING, extraStyle=ULC.ULC_HAS_VARIABLE_ROW_HEIGHT)
            listmix.ListRowHighlighter.__init__(self, wx.Colour(247,247,247))
            '''
            ListRowHighlighter is having problems. It doesn't update properly when we delete an
            entry from the listctrl, nor when we add an entry. Calling it's 'RowRefresh' function
            seems to freeze the control and not allow us to select anything. However... by clicking
            one of the headers on the listctrl, this seems to fix the freeze. To imitate this action
            in code, we reset the size on one of the headers each time we call rowrefresh. It fixes the
            problem
            '''

        def ColumnSorter(self, key1, key2):
            item1 = self.par.pastedict[key1]
            item2 = self.par.pastedict[key2]
            found = 0
            time1 = 0
            time2 = 0
            for pinf in pastelistglob:
                if pinf[2] == item1:
                    found = 1
                    time1 = pinf[3]

            found = 0
            for pinf in pastelistglob:
                if pinf[2] == item2:
                    found = 1
                    time2 = pinf[3]
            if time1 < time2:
                return 1
            else:
                return -1

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


class LoginWin(wx.Dialog):
    global settings
    def __init__(self, parent, id, title,logout=0):
        global settings
        wx.Dialog.__init__(self, parent, id, title,  size=(660,356))
        icon1 = wx.Icon("images/clipboard.png", wx.BITMAP_TYPE_PNG)
        self.SetIcon(icon1)
        dbox_location = get_dropbox_location()
        if settings['db_path'] == "":
            if settings['os_version'] == 'osx':
                settings['db_path'] = dbox_location + '/'
            elif settings['os_version'] == 'win':
                settings['db_path'] = dbox_location + '/'
        if settings['db_public_path'] == "":
            if settings['os_version'] == 'osx':
                settings['db_public_path'] = dbox_location + '/Public/'
            elif settings['os_version'] == 'win':
                settings['db_public_path'] = dbox_location + '\\Public\\'
        if settings['db_public_url'] == "":
            settings['db_public_url'] = 'http://dl.dropbox.com/u/{YOUR_USERID_HERE}/'

        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

        #added to osx
        self.backImg = wx.Bitmap("images/loginbg.png", type = wx.BITMAP_TYPE_PNG)
        self.Bind(wx.EVT_PAINT, self.OnEraseBackground)


        self.stName = wx.StaticText(self, -1, 'Computer Name', pos=(465, 20))
        self.stName.SetForegroundColour((61,110,186))
        self.tbName = wx.TextCtrl(self, -1, pos=(465, 40))

        self.stdb_path = wx.StaticText(self, -1, 'Dropbox Paste Folder Path', pos=(463, 70))
        self.stdb_path.SetForegroundColour((61,110,186))
        self.tbdb_path = wx.TextCtrl(self, -1, pos=(465, 90))

        self.stdb_public_path = wx.StaticText(self, -1, 'Dropbox Public Folder Path', pos=(463, 120))
        self.stdb_public_path.SetForegroundColour((61,110,186))
        self.tbdb_public_path = wx.TextCtrl(self, -1, pos=(465, 140))

        self.stdb_public_url = wx.StaticText(self, -1, 'Dropbox Public Folder URL', pos=(463, 170))
        self.stdb_public_url.SetForegroundColour((61,110,186))
        self.tbdb_public_url = wx.TextCtrl(self, -1, pos=(465, 190))

        self.butSub = wx.Button(self, 13, 'Submit', pos=(477, 220))

        if settings['os_version'] == 'win':
            self.stName.SetBackgroundColour('#FAFAF6')
            self.stdb_path.SetBackgroundColour('#FAFAF6')
            self.stdb_public_path.SetBackgroundColour('#FAFAF6')
            self.stdb_public_url.SetBackgroundColour('#FAFAF6')

        self.tbName.SetValue(settings['name'])
        self.tbdb_path.SetValue(settings['db_path'])
        self.tbdb_public_path.SetValue(settings['db_public_path'])
        self.tbdb_public_url.SetValue(settings['db_public_url'])

        self.Raise()

        self.Bind (wx.EVT_BUTTON, self.submitInfo, id=13)

    def OnEraseBackground(self, event):
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.backImg, 0, 0, True)

    def submitInfo(self, event):
        global settings

        if not os.path.isdir(self.tbdb_path.GetValue()):
            #invalid directory. Show error somehow.
            pass
        else:
            self.Show(False)
            settings['name'] = self.tbName.GetValue()
            settings['db_path'] = self.tbdb_path.GetValue()
            settings['db_public_path'] = self.tbdb_public_path.GetValue()
            settings['db_public_url'] = self.tbdb_public_url.GetValue()

            if settings['os_version'] == 'osx':
                if settings['db_path'][-1:] != '/':
                    settings['db_path'] = settings['db_path'] + '/'
                if settings['db_public_path'][-1:] != '/':
                    settings['db_public_path'] = settings['db_public_path'] + '/'
            elif settings['os_version'] == 'win':
                if settings['db_path'][-1:] != '\\':
                    settings['db_path'] = settings['db_path'] + '\\'
                if settings['db_public_path'][-1:] != '\\':
                    settings['db_public_path'] = settings['db_public_path'] + '\\'
            if settings['db_public_url'][-1:] != '/':
                settings['db_public_url'] = settings['db_public_url'] + '/'

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
        jsoncode = json.dumps({'name': '', 'db_path': '', 'db_public_path': '', 'db_public_url': ''})
        data = json.loads(jsoncode)
    settings['name'] = data['name']
    settings['db_path'] = data['db_path']
    settings['db_public_path'] = data['db_public_path']
    settings['db_public_url'] = data['db_public_url']

def saveMyInfo(self):
    global settings
    try:
        jsoncode = json.dumps({'name': settings['name'], 'db_path': settings['db_path'], 'db_public_path': settings['db_public_path'], 'db_public_url': settings['db_public_url']})
        spdatafile = open('.spdata', 'w')
        spdatafile.write(jsoncode)
        spdatafile.close()
    except:
        pass

class MyTaskBarIcon(wx.TaskBarIcon):
    global weburl, clipboxWindow, tbmenustr
    def __init__(self, frame):
        wx.TaskBarIcon.__init__(self)

        self.frame = frame

        myimage = wx.Bitmap('images/spsprite.png', wx.BITMAP_TYPE_PNG)
        submyimage = myimage.GetSubBitmap(wx.Rect(0,0,16,16))
        myicon = wx.EmptyIcon()
        myicon.CopyFromBitmap(submyimage)
        self.SetIcon(myicon, 'ClipBox')
        self.Bind(wx.EVT_MENU, self.hotCopy, id=20)
        self.Bind(wx.EVT_MENU, self.hotPublicCopy, id=21)
        self.Bind(wx.EVT_MENU, self.showPastes, id=4)
        self.Bind(wx.EVT_MENU, self.gotoweb, id=8)
        self.Bind(wx.EVT_MENU, self.showPreferences, id=14)
        self.Bind(wx.EVT_MENU, self.OnTaskBarClose, id=3)
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_click)
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.on_doubleleft_click)


    def OnTaskBarClose(self, event):
        '''
        This is the REAL close event that closes the entire program
        '''
        self.RemoveIcon()
        self.frame.Destroy()
        clipboxWindow.pasteListWindow.Destroy()
        clipboxWindow.toasterWindow.Destroy()
        clipboxWindow.Destroy()
        for w in wx.GetTopLevelWindows():
            w.Destroy()

    def on_left_click(self, e):
        self.PopupMenu(self.CreatePopupMenu())

    def on_doubleleft_click(self, e):
        clipboxWindow.pasteListWindow.Show(True)
        clipboxWindow.pasteListWindow.Raise()

    def CreatePopupMenu(self):
        global tbmenustr
        tbmenu = wx.Menu()
        tempitem = tbmenu.Append(-1,"X")                                   #'hack' to get images to work
        tempitem.SetBitmap(wx.Bitmap("images/file_icon_50.png"))             # 'hack' to get images to work
        mip = wx.MenuItem(tbmenu, 20, 'ClipBox Copy')
        font = mip.GetFont()
        font.SetWeight(wx.BOLD)
        mip.SetFont(font)
        tbmenu.AppendItem(mip)
        mip = wx.MenuItem(tbmenu, 21, 'ClipBox Public Copy')
        font = mip.GetFont()
        font.SetWeight(wx.BOLD)
        mip.SetFont(font)
        tbmenu.AppendItem(mip)
        mi = wx.MenuItem(tbmenu, 4, 'Show Pastes')
        font = mi.GetFont()
        font.SetWeight(wx.BOLD)
        mi.SetFont(font)
        tbmenu.AppendItem(mi)
        tbmenu.Append(14, 'Preferences...')
        if len(tbmenustr) > 1:
            tbmenu.AppendSeparator()
            csvcm = tbmenu.Append(10, 'Ctrl+Shift+V Contents:')
            csvc = tbmenu.Append(11, tbmenustr[1])
            if tbmenustr[0] == 'file':
                csvc.SetBitmap(wx.Bitmap("images/file_icon_50.png"))
            if tbmenustr[0] == 'image':
                csvc.SetBitmap(wx.Bitmap("images/image_icon_50.png"))
            if tbmenustr[0] == 'text':
                csvc.SetBitmap(wx.Bitmap("images/text_icon_50.png"))
            csvcm.Enable(False)
            csvc.Enable(False)
            tbmenu.AppendSeparator()

        tbmenu.Append(8, 'Go To Website')
        tbmenu.Append(3, 'Exit')
        tbmenu.Remove(tempitem.GetId()) #'hack' to get images to work
        return tbmenu

    def hotCopy(self, event):
        global clipboxWindow
        clipboxWindow.onHotCopy()

    def hotPublicCopy(self, event):
        global clipboxWindow
        clipboxWindow.onHotPublicCopy()

    def gotoweb(self, event):
        global weburl
        webbrowser.open(weburl)

    def showPreferences(self, event):
        logind = LoginWin(None, -1, "Preferences", logout=1)
        logind.ShowModal()
        logind.Destroy()

    def showPastes(self, event):
        clipboxWindow.pasteListWindow.Show(True)
        clipboxWindow.pasteListWindow.Raise()

class pasteFrame(wx.Frame):
    global pastelistglob
    def __init__(self, parent, id, title):

        style = wx.STAY_ON_TOP | wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER
        frame = wx.Frame.__init__(self, parent, id, title, size=(515,380), style=style)
        icon1 = wx.Icon("images/clipboard.png", wx.BITMAP_TYPE_PNG)
        self.SetIcon(icon1)

        # Here we create a panel and a notebook on the panel
        p = wx.Panel(self)

        # create the page windows as children of the notebook
        self.page1 = pastePanel(p)

        # finally, put the notebook in a sizer for the panel to manage
        # the layout
        sizer = wx.BoxSizer()
        sizer.Add(self.page1, 1, wx.EXPAND)
        p.SetSizer(sizer)
        self.Bind (wx.EVT_BUTTON, self.OnClose, id=13)
        self.Bind(wx.EVT_CLOSE,self.OnClose)

        accel_tbl = wx.AcceleratorTable([(wx.ACCEL_NORMAL, wx.WXK_ESCAPE, 13 )])
        self.SetAcceleratorTable(accel_tbl)

    def OnClose(self,event):
        self.Show(False)
        try:
            event.Veto()
        except:
            event.Skip()


class pastePanel(wx.Panel):
    global clipboxWindow, pastelistglob, lastPaste, settings
    def __init__(self, parent):
        global clipboxWindow

        wx.Panel.__init__(self, parent)
        #self.lcp = wx.ListCtrl(self, -1, style=wx.LC_REPORT)
        #self.lcp = ULC.UltimateListCtrl(self, -1, style=wx.LC_REPORT, extraStyle=ULC.ULC_HAS_VARIABLE_ROW_HEIGHT)
        self.lcp = myPasteList(self)
        self.lcp.SetBackgroundColour('#D6D6D6')

        self.lcp.InsertColumn(0, 'Paste')
        self.lcp.InsertColumn(1, 'From')
        self.lcp.InsertColumn(2, 'Time')
        self.lcp.SetColumnWidth(0, 260)
        self.lcp.SetColumnWidth(1, 115)
        self.lcp.SetColumnWidth(2, 125)


        self.pastedict = {}
        self.pastedictc = 0


        self.lcpil = wx.ImageList(50, 50)
        typefile = wx.Bitmap("images/file_icon_50.png", wx.BITMAP_TYPE_PNG)
        self.lcpil.Add(typefile)
        typeimg = wx.Bitmap("images/image_icon_50.png", wx.BITMAP_TYPE_PNG)
        self.lcpil.Add(typeimg)
        typetxt = wx.Bitmap("images/text_icon_50.png", wx.BITMAP_TYPE_PNG)
        self.lcpil.Add(typetxt)
        self.lcp.SetImageList(self.lcpil, wx.IMAGE_LIST_SMALL)


        hbox  = wx.BoxSizer(wx.HORIZONTAL)
        hbox1  = wx.BoxSizer(wx.HORIZONTAL)
        vbox1 = wx.BoxSizer(wx.VERTICAL) #content of left side

        pnl2 = wx.Panel(self, -1) #paste info

        vbox1.Add(pnl2, 0, wx.EXPAND | wx.ALL, 0)
        vbox1.Add(self.lcp, 1, wx.EXPAND | wx.ALL, 0)

        pnl2.SetSizer(hbox1)

        hbox.Add(vbox1, 1, wx.EXPAND)
        self.SetSizer(hbox)

        self.retrieve = wx.Button(pnl2, 12, 'Retrieve')
        self.delete = wx.Button(pnl2, 14, 'Delete')
        self.refresh = wx.Button(pnl2, 20, 'Refresh')
        self.retrieve.Enable(False)
        self.delete.Enable(False)
        hbox1.Add(self.retrieve, 0)
        hbox1.Add(self.delete, 0)
        hbox1.Add((191, -1), 1, wx.EXPAND | wx.ALIGN_RIGHT)
        hbox1.Add(self.refresh, 0, wx.ALIGN_RIGHT)

        self.Bind (wx.EVT_BUTTON, RetrievePaste, id=12)
        self.Bind (wx.EVT_BUTTON, DeletePaste, id=14)
        self.Bind (wx.EVT_BUTTON, self.updatePastes, id=20)
        #self.updatePastes()
        self.pastetimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.updatePastes, self.pastetimer)
        self.pastetimer.Start(10000)
        self.lcp.Bind(wx.EVT_LIST_ITEM_SELECTED, self.activateButtons)


    def activateButtons(self, evt=None):
        self.retrieve.Enable(True)
        self.delete.Enable(True)

    #Updates paste list with new ones
    def updatePastes(self, evt=None):
        global pastelistglob, lastPaste, settings
        apiPastes = cb_API.getPasteList(settings['db_path']+'.clipbox/')
        total = 0
        popuptype = ""
        pasteIDS = []
        totalnewpastes = 0
        for singPaste in apiPastes:
            totitems = self.lcp.GetItemCount()
            i = 0
            plexists = 0
            found = 0
            pasteIDS.append(singPaste['id'])
            while (i < totitems):
                key = self.lcp.GetItemData(i)
                listPasteID = self.pastedict[key]
                if listPasteID ==  singPaste['id']:
                    if singPaste['id'] != "" :
                        found = 1
                i = i + 1
            if (found == 0 or totitems == 0) and singPaste['id']!= "":
                #add to list
                totalnewpastes = totalnewpastes + 1
                index = self.lcp.InsertStringItem(0,singPaste['id'])

                currentFromU = ''
                fulltype = singPaste['type']
                parttype = singPaste['type']
                popuptype = singPaste['type']
                if singPaste['type'] == "file" :
                    self.lcp.SetItemImage(index, 0, 0)
                if singPaste['type'] == "image" :
                    self.lcp.SetItemImage(index, 1, 1)
                if singPaste['type'] == "text" :
                    self.lcp.SetItemImage(index, 2, 2)

                createdTime = datetime.fromtimestamp(float(singPaste['time']))
                createdTimeclean1 = createdTime.strftime("%m")
                createdTimeclean2 = createdTime.strftime("%d")
                createdTimecleanyr = createdTime.strftime("%y")
                createdTimeclean3 = createdTime.strftime("%I")
                createdTimeclean4 = createdTime.strftime("%M %p")
                if createdTimeclean3[0] == '0':
                    createdTimeclean3 = createdTimeclean3[1]
                if createdTimeclean1[0] == '0':
                    createdTimeclean1 = createdTimeclean1[1]
                if createdTimeclean2[0] == '0':
                    createdTimeclean2 = createdTimeclean2[1]

                createdTimeclean = createdTimeclean1 + "/" + createdTimeclean2 + "/" + createdTimecleanyr + " " + createdTimeclean3 + ":" + createdTimeclean4
                #1/19/11
                onestring = singPaste['meta']

                prefixstr = ""

                twostring = ''
                threestring = createdTimeclean

                tmp = []
                tmp.append('remote')
                tmp.append('web')
                tmp.append(singPaste['id'])
                tmp.append(singPaste['type'])
                tmp.append(onestring)
                updateCSV(tmp)

                self.lcp.SetStringItem(index, 0, onestring)
                self.lcp.SetStringItem(index, 1, twostring)
                self.lcp.SetStringItem(index, 2, threestring)
                self.pastedict[self.pastedictc] = singPaste['id']
                self.lcp.SetItemData(index, self.pastedictc)
                self.pastedictc = self.pastedictc + 1
                pastelistglob.append((onestring, twostring, singPaste['id'].strip(), singPaste['time'], singPaste['type']))
        if totalnewpastes > 1:
            clipboxWindow.toasterWindow.RunToaster(str(totalnewpastes)+" new pastes.", popuptype)
        elif totalnewpastes == 1:
            if pasteIDS[-1].strip() != lastPaste:
                clipboxWindow.toasterWindow.RunToaster("New paste.", popuptype)
        #cycle through pastes currently in list - delete ones that are gone from the server
        #this is necessary in the event they retrieve the paste elsewhere
        totitems = self.lcp.GetItemCount()
        i = 0
        while (i < totitems):
            found = 0
            key = self.lcp.GetItemData(i)
            pid = self.pastedict[key]
            for pastID in pasteIDS:
                if pid.strip() == pastID.strip():
                    found = 1
            if found == 0:
                self.lcp.DeleteItem(i)
                globfound = -1
                j = 0
                for pasID in pastelistglob:
                    if pid.strip() == pasID[2].strip():
                        globfound= j
                    j = j + 1
                if globfound != -1:
                    pastelistglob.pop(globfound)
                totitems = totitems-1
            else:
                i = i + 1
        total = len(pastelistglob)

        saveTaskBarUpdates(total, popuptype)
        self.lcp.SortItems(self.lcp.ColumnSorter)
        self.cleanTemp()
        self.lcp.RefreshRows() #to update the zebra stripes, but for some reason freezes the listctrl area
        self.lcp.SetColumnWidth(0, 260) #unfreezes listctrl area

    def cleanTemp(self):
        i = 0
        for filename in os.listdir("temp"):
            if i > 3:
                break #only delete 3 at a time, max, to reduce lag
            basename = filename
            filename = os.getcwd()+"/temp/"+filename
            file_stats = os.stat(filename)
            modtime = file_stats[stat.ST_MTIME]
            currenttime = int(time.time())
            difftime = currenttime - modtime
            tenminute = 60 * 10 #60 seconds time ten minutes
            if difftime > tenminute: #if last modify time was more than 10 minutes ago
                os.remove(filename)
                i = i + 1

def DeletePaste(event):
    global clipboxWindow, pastelistglob, settings
    self = clipboxWindow.pasteListWindow
    clipboxWindow.pasteListWindow.page1.retrieve.Enable(False)
    clipboxWindow.pasteListWindow.page1.delete.Enable(False)
    index = clipboxWindow.pasteListWindow.page1.lcp.GetFocusedItem()
    if index != -1:
        key = clipboxWindow.pasteListWindow.page1.lcp.GetItemData(index)
        pasteID = clipboxWindow.pasteListWindow.page1.pastedict[key]
        cnt = 0
        for pinf in pastelistglob:
            if pinf[2] == pasteID:
                pasteType = pinf[4]
                fname = pinf[0].split(" ")[0]
                pastelistglob.pop(cnt) #remove it
            cnt = cnt + 1
        if not os.path.exists(settings['db_public_path'] + '.clipbox/'):
            os.makedirs(settings['db_public_path'] + '.clipbox/')
        if not os.path.exists(settings['db_path'] + '.clipbox/'):
            os.makedirs(settings['db_path'] + '.clipbox/')
        cb_API.deletePasteObject(pasteID, settings['db_path']+'.clipbox/')
        saveTaskBarUpdates(tbitemcnt-1)
        clipboxWindow.pasteListWindow.page1.lcp.DeleteItem(index)
        clipboxWindow.pasteListWindow.page1.lcp.RefreshRows()
        clipboxWindow.pasteListWindow.page1.lcp.SetColumnWidth(0, 260)

def updateCSV(tmp):
    global ctrlshiftv, tbmenustr
    ctrlshiftv = tmp
    tbmenustr = []
    tbmenustr.append(ctrlshiftv[3])
    tbmenustr.append(ctrlshiftv[4])


def RetrievePaste(self, event=None, shortcut="no"):
    global clipboxWindow, pastelistglob, ctrlshiftv, settings

    self = clipboxWindow.pasteListWindow
    if shortcut == "no": #from window
        clipboxWindow.pasteListWindow.page1.retrieve.Enable(False)
        clipboxWindow.pasteListWindow.page1.delete.Enable(False)
        index = clipboxWindow.pasteListWindow.page1.lcp.GetFocusedItem()
        key = clipboxWindow.pasteListWindow.page1.lcp.GetItemData(index)
        pasteID = clipboxWindow.pasteListWindow.page1.pastedict[key]
    else: #from hotkey
        pasteID = ctrlshiftv[2]
        index = 0

    cnt = 0
    pasteType = ""
    pastePrev = ""
    pasteFrom = ""
    fullInfo = ""
    for pinf in pastelistglob:
        if pinf[2] == pasteID:
            pasteType = pinf[4]
            pastePrev = pinf[0]
            pasteFrom = pinf[1]
            fnamet = pinf[0].split(" ")
            fnamet.pop(len(fnamet)-1)
            fname = ' '.join(fnamet)
            pastelistglob.pop(cnt) #remove it
        cnt = cnt + 1

    if shortcut == "no": #from window
        clipboxWindow.pasteListWindow.Show(False)

    if not os.path.exists(settings['db_public_path'] + '.clipbox/'):
        os.makedirs(settings['db_public_path'] + '.clipbox/')
    if not os.path.exists(settings['db_path'] + '.clipbox/'):
        os.makedirs(settings['db_path'] + '.clipbox/')
    if pasteType != "":
        if pasteType=='text' or pasteType =='Text' :
            txtdata = cb_API.retrievePasteObject(pasteID, settings['db_path']+'.clipbox/')
            td = wx.TextDataObject()
            td.SetText(txtdata)
            if wx.TheClipboard.Open():
                successt = wx.TheClipboard.SetData(td)
                wx.TheClipboard.Close()
            cb_API.delete_paste(pasteID, settings['db_path']+'.clipbox/')
        if pasteType=='file' or pasteType =='File' :
            fileName = fname
            fd = wx.FileDataObject()
            inputFData = cb_API.retrievePasteObject(pasteID, settings['db_path']+'.clipbox/')
            fullfile = settings['db_path'] + pasteID
            #need to make sure file pastes with proper name... this is inefficient. Find a better way.
            try:
                os.makedirs('temp')
            except:
                pass
            tmpFile = open(os.getcwd()+'/temp/'+fileName, 'w')
            tmpFile.write(inputFData)
            tmpFile.close()
            fd.AddFile(os.getcwd()+'/temp/'+fileName)
            if wx.TheClipboard.Open():
                successf = wx.TheClipboard.SetData(fd)
                wx.TheClipboard.Close()
            cb_API.delete_paste(pasteID, settings['db_path']+'.clipbox/')
        if pasteType=='image' or pasteType =='Image' :
            inputFData = cb_API.retrievePasteObject(pasteID, settings['db_path']+'.clipbox/')
            bd = wx.BitmapDataObject()
            bimg = wx.Bitmap(settings['db_path']+'.clipbox/'+pasteID, wx.BITMAP_TYPE_PNG)
            bimgsucc = bd.SetBitmap(bimg)
            if wx.TheClipboard.Open():
                successb = wx.TheClipboard.SetData(bd)
                wx.TheClipboard.Close()
            cb_API.delete_paste(pasteID, settings['db_path']+'.clipbox/')
        if shortcut == "no": #from window
            clipboxWindow.toasterWindow.RunToaster('Paste retrieved and loaded. Control+V will now paste it', pasteType)
            saveTaskBarUpdates(tbitemcnt-1, pasteType)
        #else: #from hotkey
        clipboxWindow.pasteListWindow.page1.lcp.DeleteItem(index)
        clipboxWindow.pasteListWindow.page1.lcp.RefreshRows()
        clipboxWindow.pasteListWindow.page1.lcp.SetColumnWidth(0, 260)

class mainFrame(wx.Frame, wx.lib.mixins.listctrl.ColumnSorterMixin):
    global clipboxWindow, pastelistglob, logind, settings, lastPaste
    def __init__(self, parent, id, title):
        style = wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER
        self.window = wx.Frame.__init__(self, parent, id, title, size=(450,555), style=style)

        self.regHotKey()
        self.Bind(wx.EVT_HOTKEY, self.handleHotKey, id=self.hotCopy)
        self.Bind(wx.EVT_HOTKEY, self.handleHotKey, id=self.hotPublicCopy)
        self.Bind(wx.EVT_HOTKEY, self.handleHotKey, id=self.hotPaste)
        self.Bind(wx.EVT_HOTKEY, self.handleHotKey, id=self.hotRecent)
        if settings['os_version'] == 'win':
            self.Bind(wx.EVT_HOTKEY, self.handleHotKey, id=self.hotCut)
            self.Bind(wx.EVT_HOTKEY, self.handleHotKey, id=self.hotScreen)
            self.Bind(wx.EVT_HOTKEY, self.handleHotKey, id=self.hotScreenRect)
            self.Bind(wx.EVT_HOTKEY, self.handleHotKey, id=self.hotCurrent)


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
        self.pasteListWindow = pasteFrame(self, -1, "Paste List")

    def onFullClose(self, event):
        for w in wx.GetTopLevelWindows():
            w.Destroy()
        self.Destroy()

    def OnClose(self,event):
        self.Show(False)
        event.Veto()

    def ViewPastes(self, event):
        clipboxWindow.pasteListWindow.Show(True)

    def regHotKey(self):
        """
        This function registers:
            hotkey Control+SHIFT+C with id=100
            hotkey Control+SHIFT+V with id=101
            hotkey Control+SHIFT+R with id=102
        """
        self.hotCopy = 100
        mod_control = cb_helper.get_keycode('control_mod')
        mod_shift = cb_helper.get_keycode('shift_mod')
        self.RegisterHotKey(
            self.hotCopy, #a unique ID for this hotkey
            mod_control | mod_shift, #the modifier keys
            cb_helper.get_keycode('c')) #the key to watch for (0x43 = C)

        self.hotPublicCopy = 107
        self.RegisterHotKey(
            self.hotPublicCopy, #a unique ID for this hotkey
            mod_control | mod_shift, #the modifier keys
            cb_helper.get_keycode('a'))

        self.hotPaste = 101
        self.RegisterHotKey(
            self.hotPaste, #a unique ID for this hotkey
            mod_control | mod_shift, #the modifier keys
            cb_helper.get_keycode('v')) #the key to watch for (0x56 = V)

        self.hotRecent = 102
        self.RegisterHotKey(
            self.hotRecent, #a unique ID for this hotkey
            mod_control | mod_shift, #the modifier keys
            cb_helper.get_keycode('r')) #the key to watch for (0x52 = R)

        if settings['os_version'] == 'win':
            self.hotScreen = 103
            self.RegisterHotKey(
                self.hotScreen, #a unique ID for this hotkey
                mod_control | mod_shift, #the modifier keys
                cb_helper.get_keycode('3')) #the key to watch for (0x33 = 3)

            self.hotScreenRect = 104
            self.RegisterHotKey(
                self.hotScreenRect, #a unique ID for this hotkey
                mod_control | mod_shift, #the modifier keys
                cb_helper.get_keycode('4')) #the key to watch for (0x34 = 4)

            self.hotCut = 105
            self.RegisterHotKey(
                self.hotCut, #a unique ID for this hotkey
                mod_control | mod_shift, #the modifier keys
                cb_helper.get_keycode('x')) #the key to watch for (0x58 = X)

            self.hotCurrent = 106
            self.RegisterHotKey(
                self.hotCurrent, #a unique ID for this hotkey
                mod_control | mod_shift, #the modifier keys
                cb_helper.get_keycode('1')) #the key to watch for (0x31 = 1)



    def handleHotKey(self, evt):
        global pastelistglob, ctrlshiftv, sshotx1, sshotx2, sshoty1, sshoty2
        eventId = evt.GetId()

        if eventId == 106: #hotCurrent
            #just use current contents of clipboard, don't change them
            self.onHotCopy()

        if eventId == 105: #hotCut
            cb_helper.wait_for_key_up('cut')
            cb_helper.send_key('cut')
            time.sleep(0.05)
            self.onHotCopy()

        if eventId == 104: #hotScreenRect

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
        if eventId == 103: #hotScreen
            captureBmapSize = (wx.SystemSettings.GetMetric( wx.SYS_SCREEN_X ),
            wx.SystemSettings.GetMetric( wx.SYS_SCREEN_Y ) )
            captureStartPos = (0, 0)    # Arbitrary U-L position anywhere within the screen
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

        if eventId == 102: #hotRecent
            #pull up pastes window
            clipboxWindow.pasteListWindow.Show(True)
            clipboxWindow.pasteListWindow.Raise()

        if eventId == 101: #hotPaste
            cb_helper.wait_for_key_up('paste')
            if len(ctrlshiftv) > 0:
                if ctrlshiftv[0] == 'remote':
                    RetrievePaste(self, shortcut="yes")
            cb_helper.send_key('paste')
            time.sleep(0.05)

        if eventId == 100: #hotCopy
            cb_helper.wait_for_key_up('copy')
            cb_helper.send_key('copy')
            time.sleep(1.5)
            self.onHotCopy()

        if eventId == 107: #hotPublicCopy
            cb_helper.wait_for_key_up('copy')
            cb_helper.send_key('copy')
            time.sleep(1.5)
            self.onHotPublicCopy()

    def onHotCopy(self):
        cb_helper.catch_clipboard_in_use_bug()
        self.OnPaste()

    def onHotPublicCopy(self):
        cb_helper.catch_clipboard_in_use_bug()
        self.OnPaste('None', 'Public')

    def OnPaste(self, event=None, type='Private'):
        global lastPaste, settings
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
        tmpPasteName = strftime("%Y-%m-%d_%H-%M-%S", gmtime())+''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(6))

        #on OSX, in a file copy, both these variables are true
        if successt and successf:
            successt = False
            successb = False

        self.Show(False)
        if not os.path.exists(settings['db_public_path'] + '.clipbox/'):
            os.makedirs(settings['db_public_path'] + '.clipbox/')
        if not os.path.exists(settings['db_path'] + '.clipbox/'):
            os.makedirs(settings['db_path'] + '.clipbox/')
        if successt:
            appd = ""
            if len(pasteText) > 20:
                appd = "..."
            meta = ""+pasteText[:20].strip()
            if len(pasteText) > 20:
                meta = meta + "..."
            meta = meta + " ("+str(len(pasteText))+" chars)"
            if type == 'Private':
                pasteID = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(6)) #6 should be good, eh?

                result = cb_API.add_paste_to_db('text', meta, pasteID, settings['db_path']+'.clipbox/')
                try:
                    datafo = open(settings['db_path']+'.clipbox/'+pasteID, 'w')
                    datafo.write(pasteText)
                    datafo.close()
                except:
                    pass
                clipboxWindow.toasterWindow.RunToaster('Paste Sent', 'text')
                lastPaste = pasteID
            else: #Public
                fname = tmpPasteName
                fexists = os.path.isfile(settings['db_public_path'] + '.clipbox/' + fname)
                if fexists == True:
                    #fname = fname + '_' + ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(6))
                    os.remove(settings['db_public_path'] + '.clipbox/' + fname) #remove old file
                try:
                    datafo = open(settings['db_public_path'] + '.clipbox/'+fname, 'w')
                    datafo.write(pasteText)
                    datafo.close()

                    public_paste_url = settings['db_public_url'] + '.clipbox/'+fname
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
            if type == 'Private':
                pasteID = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(6)) #6 should be good, eh?
                try:
                    if len(allFileNames)>1:
                        compression = zipfile.ZIP_DEFLATED
                        zfname = settings['db_path']+'.clipbox/' + pasteID
                        zf = zipfile.ZipFile(zfname, mode='w')
                        try:
                            for fnm in allFileNames:
                                zf.write(str(fnm), os.path.basename(str(fnm)), compress_type=compression)
                        finally:
                            zf.close()
                        fileloc = settings['db_path']+'.clipbox/' + pasteID
                        fname = os.path.basename(ftext) + ".zip"
                    else:
                        shutil.copyfile(ftext, settings['db_path']+'.clipbox/'+pasteID)
                        fname = os.path.basename(ftext)

                    size = convert_bytes(os.path.getsize(settings['db_path']+'.clipbox/' + pasteID))
                    meta = fname + " ("+str(size)+")"
                    result = cb_API.add_paste_to_db('file', meta, pasteID, settings['db_path']+'.clipbox/')

                except:
                    pass
                clipboxWindow.toasterWindow.RunToaster('Paste Sent', 'file')
                lastPaste = pasteID
            else: #Public
                fname = os.path.basename(ftext)
                fexists = os.path.isfile(settings['db_public_path'] + '.clipbox/' + fname)
                if fexists == True:
                    fname = fname + '_' + ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(6))
                try:
                    if len(allFileNames)>1:
                        compression = zipfile.ZIP_DEFLATED
                        zfname = settings['db_public_path'] + '.clipbox/'+fname
                        zf = zipfile.ZipFile(zfname, mode='w')
                        try:
                            for fnm in allFileNames:
                                zf.write(str(fnm), os.path.basename(str(fnm)), compress_type=compression)
                        finally:
                            zf.close()
                        fileloc = settings['db_public_path'] + '.clipbox/'+fname
                    else:
                        fileloc = ftext
                        shutil.copyfile(ftext, settings['db_public_path'] + '.clipbox/'+fname)

                    size = convert_bytes(os.path.getsize(fileloc))
                    meta = fname + " ("+str(size)+")"

                    public_paste_url = settings['db_public_url'] + '.clipbox/'+fname

                    clipboxWindow.toasterWindow.RunToaster('Download URL copied to your Clipboard!', 'file')
                    td = wx.TextDataObject()
                    td.SetText(public_paste_url)
                    if wx.TheClipboard.Open():
                        successt = wx.TheClipboard.SetData(td)
                        wx.TheClipboard.Close()
                except:
                    clipboxWindow.toasterWindow.RunToaster('An Error Occurred.', 'file')

        if successb:
            bmpimg = wx.ImageFromBitmap(bimg)
            width = bmpimg.GetWidth()
            height = bmpimg.GetHeight()
            bimg.SaveFile('temp/'+tmpPasteName+'.png', wx.BITMAP_TYPE_PNG)
            fullpath = os.getcwd() + "/temp/"+tmpPasteName+".png"
            size = convert_bytes(os.path.getsize('temp/'+tmpPasteName+'.png'))
            meta = str(width)+"x"+str(height)+" pixels ("+str(size)+")"
            if type == 'Private':
                pasteID = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(6)) #6 should be good, eh?

                result = cb_API.add_paste_to_db('image', meta, pasteID, settings['db_path']+'.clipbox/')
                try:
                    shutil.copyfile(fullpath, settings['db_path']+'.clipbox/'+pasteID)
                except:
                    pass
                clipboxWindow.toasterWindow.RunToaster('Paste Sent', 'image')
                lastPaste = pasteID
            else: #Public
                fname = os.path.basename(fullpath)
                fexists = os.path.isfile(settings['db_public_path'] + '.clipbox/' + fname)
                if fexists == True:
                    fname = fname + '_' + ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(6))
                try:
                    shutil.copyfile(fullpath, settings['db_public_path'] + '.clipbox/'+fname)

                    public_paste_url = settings['db_public_url'] + '.clipbox/'+fname
                    clipboxWindow.toasterWindow.RunToaster('Download URL copied to your Clipboard!', 'image')
                    td = wx.TextDataObject()
                    td.SetText(public_paste_url)
                    if wx.TheClipboard.Open():
                        successt = wx.TheClipboard.SetData(td)
                        wx.TheClipboard.Close()
                except:
                    clipboxWindow.toasterWindow.RunToaster('An Error Occurred.', 'image')

    def GetSortImages(self):
        return (self.dn, self.up)


def saveTaskBarUpdates(newtbcnt=-1, newtbtype=""):
    global tbitemcnt, tbitemtype, clipboxWindow
    if type(clipboxWindow).__name__ != 'str': #wait for clipbox Window to be fully created
        if newtbcnt != -1:
            tbitemcnt = newtbcnt
        if newtbtype != '':
            tbitemtype = newtbtype

        total = tbitemcnt
        popuptype = tbitemtype
        if(total < 0):
            total = 0
            tbitemcnt = 0
        if(total > 9):
            total = 10
        #white (text) blue (images) yellow (files)
        myimage = wx.Bitmap('images/spsprite.png', wx.BITMAP_TYPE_PNG)
        xcoor = 0
        ycoor = 0
        if(total != 0):
            ycoor = 16 * (total - 1)
            xcoor = 16 #default text
            if popuptype == 'image':
                xcoor = 32
            if popuptype == 'file':
                xcoor = 48
        submyimage = myimage.GetSubBitmap(wx.Rect(xcoor,ycoor,16,16))
        myicon = wx.EmptyIcon()
        myicon.CopyFromBitmap(submyimage)
        clipboxWindow.tskic.SetIcon(myicon, 'ClipBox')

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
    global clipboxWindow, logind, settings
    def OnInit(self):
        global logind, clipboxWindow, settings

        cb_helper.kill_other_sp_exe()

        loadMyInfo(self)

        forcelogin = 0
        if settings['db_path'] != '':
            try:
                if not os.path.isdir(settings['db_path']):
                    forcelogin = 1
                else:
                    clipboxWindow = mainFrame(None, -1, 'ClipBox')
            except urllib2.URLError, e:
                forcelogin = 1
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

    if settings['os_version'] == 'osx':
        def MacReopenApp(self):
            """Called when the doc icon is clicked"""
            self.GetTopWindow().pasteListWindow.Show(True)
            self.GetTopWindow().pasteListWindow.Raise()

app = MyApp(0)
app.MainLoop()

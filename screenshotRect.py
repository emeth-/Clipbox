import wx

class Screen_Capture ( wx.Dialog ) :

  def __init__(self, Filename, parent = None ) :
    self.Filename = Filename
    self.c1 = None
    self.c2 = None
    wx.Dialog.__init__( self, parent, -1, '', size=wx.DisplaySize(),
                       style = wx.SYSTEM_MENU | wx.FRAME_NO_TASKBAR | wx.NO_BORDER    )

    self.panel = wx.Panel (self, size=self.GetSize () )
    self.SetTransparent ( 50 )

    self.panel.Bind ( wx.EVT_LEFT_DOWN, self.OnMouseDown )
    self.panel.Bind ( wx.EVT_MOTION   , self.OnMouseMove )
    self.panel.Bind ( wx.EVT_LEFT_UP  , self.OnMouseUp   )
    self.panel.Bind ( wx.EVT_PAINT    , self.OnPaint     )

    self.SetCursor ( wx.StockCursor ( wx.CURSOR_CROSS ) )
    self.Show ()

  def OnMouseDown ( self, event ) :
    self.c1 = event.GetPosition()

  def OnMouseMove ( self, event ) :
    if event.Dragging() and event.LeftIsDown():
      self.c2 = event.GetPosition()
      self.Refresh()

  def OnMouseUp ( self, event ) :
    ## Don't know for sure that +(1,1) is correct ??
    self.c1 = self.ClientToScreen ( self.c1 ) + ( 1, 1 )
    self.c2 = self.ClientToScreen ( self.c2 ) + ( 1, 1 )
    x0 = self.c1.x
    x1 = self.c2.x
    y0 = self.c1.y
    y1 = self.c2.y
    if x0 == x1 or y0 == y1 :
      self.c1 = None
      self.c2 = None
      return

    if x0 > x1 :
      x  = x0
      x0 = x1
      x1 = x
    if y0 > y1 :
      y  = y0
      y0 = y1
      y1 = y

    self.Close()

  def OnPaint ( self, event ) :
    if ( self.c1 is None ) or ( self.c2 is None ) :
      return

    dc = wx.PaintDC ( self.panel )
    dc.SetPen ( wx.Pen ( 'red', 1 ) )
    dc.SetBrush ( wx.Brush ( wx.Color ( 0, 0, 0 ), wx.TRANSPARENT ))

    dc.DrawRectangle ( self.c1.x, self.c1.y,
                       self.c2.x - self.c1.x, self.c2.y - self.c1.y )
                       
                       
                       
                       
                
'''                              
class MyApp(wx.App):
    def OnInit(self):
		dlg = Screen_Capture(None)
		dlg.ShowModal()
		return True

app = MyApp(0)
app.MainLoop()
'''
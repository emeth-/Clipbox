# --------------------------------------------------------------------------------- #
# ULTIMATELISTCTRL wxPython IMPLEMENTATION
# Inspired by and heavily based on the wxWidgets C++ generic version of wxListCtrl.
#
# Andrea Gavana, @ 08 May 2009
# Latest Revision: 22 May 2009, 09.00 GMT
#
#
# TODO List
#
# 1)  Subitem selection;
# 2)  Watermark? (almost, does not work very well :-( );
# 3)  Groups? (Maybe, check ObjectListView);
# 4)  Scrolling items as headers and footers;
# 5)  Alpha channel for text/background of items;
# 6)  Custom renderers for headers/footers;
# 7)  Fading in and out on mouse motion (a la Windows Vista Aero);
# 8)  Sub-text for headers/footers (grey text below the header/footer text);
# 9)  Fixing the columns to the left or right side of the control layout;
# 10) Skins for header and scrollbars.
#
#
# For all kind of problems, requests of enhancements and bug reports, please
# write to me at:
#
# andrea.gavana@gmail.com
# gavana@kpo.kz
#
# Or, obviously, to the wxPython mailing list!!!
#
#
# End Of Comments
# --------------------------------------------------------------------------------- #


"""
Description
===========

UltimateListCtrl is a class that mimics the behaviour of wx.ListCtrl, withc almost
the same base functionalities plus some more enhancements. This class does
not rely on the native control, as it is a full owner-drawn list control.

In addition to the standard wx.ListCtrl behaviour this class supports:


Appearance
^^^^^^^^^^

* Multiple images for items/subitems;
* Font, colour, background, custom renderers and formatting for items and subitems;
* Ability to add persistent data to an item using SetPyData and GetPyData: the data
  can be any Python object and not necessarily an integer as in wx.ListCtrl;
* CheckBox-type items and subitems;
* RadioButton-type items and subitems;
* Overflowing items/subitems, a la wxGrid, i.e. an item/subitem may overwrite neighboring
  items/subitems if its text would not normally fit in the space allotted to it;
* Hyperlink-type items and subitems: they look like an hyperlink, with the proper mouse
  cursor on hovering;
* Multiline text items and subitems;
* Variable row heights depending on the item/subitem kind/text/window;
* User defined item/subitem renderers: these renderer classes *must* implement the methods
  `DrawSubItem`, `GetLineHeight` and `GetSubItemWidth` (see the demo);
* Enabling/disabling items (together with their plain or grayed out icons);
* Whatever non-toplevel widget can be attached next to an item/subitem;
* Column headers are fully customizable in terms of icons, colour, font, alignment etc...;
* Column headers can have their own checkbox/radiobutton;
* Column footers are fully customizable in terms of icons, colour, font, alignment etc...;
* Column footers can have their own checkbox/radiobutton;
* Ability to hide/show columns;
* Default selection style, gradient (horizontal/vertical) selection style and Windows
  Vista selection style.


Styles
^^^^^^

* A ULC_TILE style, in which each item appears as a full-sized icon with a label of
  one or more lines beside it (partially implemented);


Extra Styles
^^^^^^^^^^^^

* ULC_NO_HIGHLIGHT: No highlight when an item is selected;
* ULC_STICKY_HIGHLIGHT: Items are selected by simply hovering on them, with no need to
  click on them;
* ULC_STICKY_NOSELEVENT: Don't send a selection event when using ULC_STICKY_HIGHLIGHT
  extra style;
* ULC_SEND_LEFTCLICK: Send a left click event when an item is selected;
* ULC_AUTO_CHECK_CHILD: When a column header has a checkbox associated, auto-check all
  the subitems in that column;
* ULC_AUTO_TOGGLE_CHILD: When a column header has a checkbox associated, toggle all
  the subitems in that column;
* ULC_SHOW_TOOLTIPS: Show tooltips for ellipsized items/subitems (text too long to be
  shown in the available space) containing the full item/subitem text;
* ULC_HOT_TRACKING: Enable hot tracking of items on mouse motion;
* ULC_BORDER_SELECT: Changes border color whan an item is selected, instead of
  highlighting the item;
* ULC_TRACK_SELECT: Enables hot-track selection in a list control. Hot track selection
  means that an item is automatically selected when the cursor remains over the item for
  a certain period of time. The delay is retrieved on Windows using the win32api call
  win32gui.SystemParametersInfo(win32con.SPI_GETMOUSEHOVERTIME), and is defaulted to 400ms
  on other platforms. This extra style applies to all views of UltimateListCtrl;
* ULC_HEADER_IN_ALL_VIEWS: Show column headers in all view modes;
* ULC_NO_FULL_ROW_SELECT: When an item is selected, the only the item in the first column
  is highlighted;
* ULC_FOOTER: Show a footer too (only when header is present);


And a lot more. Check the demo for an almost complete review of the functionalities.


Events
======

All the events supported by wx.ListCtrl are also available in UltimateListCtrl.

Plus, UltimateListCtrl supports the events related to the checkbutton-type items, subitems
and column headers/footers:

  - EVT_LIST_ITEM_CHECKING: an item/subitem is being checked;
  - EVT_LIST_ITEM_CHECKED: an item/subitem has been checked;
  - EVT_LIST_COL_CHECKING: a column header is being checked;
  - EVT_LIST_COL_CHECKED: a column header has being checked;
  - EVT_LIST_FOOTER_CHECKING: a column footer is being checked;
  - EVT_LIST_FOOTER_CHECKED: a column footer has being checked.

And to hyperlink-type items:

  - EVT_LIST_ITEM_HYPERLINK: an hyperlink item has been clicked.

And footer-related events:

  - EVT_LIST_FOOTER_CLICK: the user left-clicked on a column footer;
  - EVT_LIST_FOOTER_RIGHT_CLICK: the user right-clicked on a column footer.

Plus the following specialized events:

  - EVT_LIST_ITEM_LEFT_CLICK: send a left-click event after an item is selected;
  - EVT_LIST_END_DRAG: notify an end-drag operation.


Supported Platforms
===================

UltimateListCtrl has been tested on the following platforms:
  * Windows (Windows XP);


Latest Revision: Andrea Gavana @ 22 May 2009, 09.00 GMT
Version 0.2
"""

import wx
import math
import bisect
import types
import zlib
import cStringIO

from wx.lib.expando import ExpandoTextCtrl

# Version Info
__version__ = "0.2"


# ----------------------------------------------------------------------------
# UltimateListCtrl constants
# ----------------------------------------------------------------------------

# style flags (compatible with wx.ListCtrl, except for ULC_TILE)
ULC_VRULES                  = wx.LC_VRULES
ULC_HRULES                  = wx.LC_HRULES

ULC_ICON                    = wx.LC_ICON
ULC_SMALL_ICON              = wx.LC_SMALL_ICON
ULC_LIST                    = wx.LC_LIST
ULC_REPORT                  = wx.LC_REPORT
ULC_TILE                    = 0x10000

ULC_ALIGN_TOP               = wx.LC_ALIGN_TOP
ULC_ALIGN_LEFT              = wx.LC_ALIGN_LEFT
ULC_AUTOARRANGE             = wx.LC_AUTOARRANGE
ULC_VIRTUAL                 = wx.LC_VIRTUAL
ULC_EDIT_LABELS             = wx.LC_EDIT_LABELS
ULC_NO_HEADER               = wx.LC_NO_HEADER
ULC_NO_SORT_HEADER          = wx.LC_NO_SORT_HEADER
ULC_SINGLE_SEL              = wx.LC_SINGLE_SEL
ULC_SORT_ASCENDING          = wx.LC_SORT_ASCENDING
ULC_SORT_DESCENDING         = wx.LC_SORT_DESCENDING

# Extra styles
ULC_NO_HIGHLIGHT            = 0x0001
ULC_STICKY_HIGHLIGHT        = 0x0002
ULC_STICKY_NOSELEVENT       = 0x0004
ULC_SEND_LEFTCLICK          = 0x0008
ULC_HAS_VARIABLE_ROW_HEIGHT = 0x0010

ULC_AUTO_CHECK_CHILD    = 0x0020  # only meaningful for checkboxes
ULC_AUTO_TOGGLE_CHILD   = 0x0040  # only meaningful for checkboxes
ULC_AUTO_CHECK_PARENT   = 0x0080  # only meaningful for checkboxes
ULC_SHOW_TOOLTIPS       = 0x0100  # shows tooltips on items with ellipsis (...)
ULC_HOT_TRACKING        = 0x0200  # enable hot tracking on mouse motion
ULC_BORDER_SELECT       = 0x0400  # changes border color whan an item is selected, instead of highlighting the item
ULC_TRACK_SELECT        = 0x0800  # Enables hot-track selection in a list control. Hot track selection means that an item
                                  # is automatically selected when the cursor remains over the item for a certain period
                                  # of time. The delay is retrieved on Windows using the win32api call
                                  # win32gui.SystemParametersInfo(win32con.SPI_GETMOUSEHOVERTIME), and is defaulted to 400ms
                                  # on other platforms. This style applies to all styles of UltimateListCtrl.
ULC_HEADER_IN_ALL_VIEWS = 0x1000  # Show column headers in all view modes
ULC_NO_FULL_ROW_SELECT  = 0x2000  # When an item is selected, the only the item in the first column is highlighted
ULC_FOOTER              = 0x4000  # Show a footer too (only when header is present)

ULC_MASK_TYPE  = ULC_ICON | ULC_SMALL_ICON | ULC_LIST | ULC_REPORT | ULC_TILE
ULC_MASK_ALIGN = ULC_ALIGN_TOP | ULC_ALIGN_LEFT
ULC_MASK_SORT  = ULC_SORT_ASCENDING | ULC_SORT_DESCENDING

# for compatibility only
ULC_USER_TEXT = ULC_VIRTUAL

# Omitted because
#  (a) too much detail
#  (b) not enough style flags
#  (c) not implemented anyhow in the generic version
#
# ULC_NO_SCROLL
# ULC_NO_LABEL_WRAP
# ULC_OWNERDRAW_FIXED
# ULC_SHOW_SEL_ALWAYS

# Mask flags to tell app/GUI what fields of UltimateListItem are valid
ULC_MASK_STATE         =      wx.LIST_MASK_STATE
ULC_MASK_TEXT          =      wx.LIST_MASK_TEXT
ULC_MASK_IMAGE         =      wx.LIST_MASK_IMAGE
ULC_MASK_DATA          =      wx.LIST_MASK_DATA
ULC_SET_ITEM           =      wx.LIST_SET_ITEM
ULC_MASK_WIDTH         =      wx.LIST_MASK_WIDTH
ULC_MASK_FORMAT        =      wx.LIST_MASK_FORMAT
ULC_MASK_FONTCOLOUR    =      0x0080
ULC_MASK_FONT          =      0x0100
ULC_MASK_BACKCOLOUR    =      0x0200
ULC_MASK_KIND          =      0x0400
ULC_MASK_ENABLE        =      0x0800
ULC_MASK_CHECK         =      0x1000
ULC_MASK_HYPERTEXT     =      0x2000
ULC_MASK_WINDOW        =      0x4000
ULC_MASK_PYDATA        =      0x8000
ULC_MASK_SHOWN         =      0x10000
ULC_MASK_RENDERER      =      0x20000
ULC_MASK_OVERFLOW      =      0x40000
ULC_MASK_FOOTER_TEXT   =      0x80000
ULC_MASK_FOOTER_IMAGE  =      0x100000
ULC_MASK_FOOTER_FORMAT =      0x200000
ULC_MASK_FOOTER_FONT   =      0x400000
ULC_MASK_FOOTER_CHECK  =      0x800000
ULC_MASK_FOOTER_KIND   =      0x1000000

# State flags for indicating the state of an item
ULC_STATE_DONTCARE    =   wx.LIST_STATE_DONTCARE
ULC_STATE_DROPHILITED =   wx.LIST_STATE_DROPHILITED      # MSW only
ULC_STATE_FOCUSED     =   wx.LIST_STATE_FOCUSED
ULC_STATE_SELECTED    =   wx.LIST_STATE_SELECTED
ULC_STATE_CUT         =   wx.LIST_STATE_CUT              # MSW only
ULC_STATE_DISABLED    =   wx.LIST_STATE_DISABLED         # OS2 only
ULC_STATE_FILTERED    =   wx.LIST_STATE_FILTERED         # OS2 only
ULC_STATE_INUSE       =   wx.LIST_STATE_INUSE            # OS2 only
ULC_STATE_PICKED      =   wx.LIST_STATE_PICKED           # OS2 only
ULC_STATE_SOURCE      =   wx.LIST_STATE_SOURCE           # OS2 only

# Hit test flags, used in HitTest
ULC_HITTEST_ABOVE           = wx.LIST_HITTEST_ABOVE            # Above the client area.
ULC_HITTEST_BELOW           = wx.LIST_HITTEST_BELOW            # Below the client area.
ULC_HITTEST_NOWHERE         = wx.LIST_HITTEST_NOWHERE          # In the client area but below the last item.
ULC_HITTEST_ONITEMICON      = wx.LIST_HITTEST_ONITEMICON       # On the bitmap associated with an item.
ULC_HITTEST_ONITEMLABEL     = wx.LIST_HITTEST_ONITEMLABEL      # On the label (string) associated with an item.
ULC_HITTEST_ONITEMRIGHT     = wx.LIST_HITTEST_ONITEMRIGHT      # In the area to the right of an item.
ULC_HITTEST_ONITEMSTATEICON = wx.LIST_HITTEST_ONITEMSTATEICON  # On the state icon for a tree view item that is in a user-defined state.
ULC_HITTEST_TOLEFT          = wx.LIST_HITTEST_TOLEFT           # To the left of the client area.
ULC_HITTEST_TORIGHT         = wx.LIST_HITTEST_TORIGHT          # To the right of the client area.
ULC_HITTEST_ONITEMCHECK     = 0x1000                           # On the checkbox (if any)

ULC_HITTEST_ONITEM = ULC_HITTEST_ONITEMICON | ULC_HITTEST_ONITEMLABEL | ULC_HITTEST_ONITEMSTATEICON | ULC_HITTEST_ONITEMCHECK

# Flags for GetNextItem (MSW only except ULC_NEXT_ALL)
ULC_NEXT_ABOVE = wx.LIST_NEXT_ABOVE         # Searches for an item above the specified item
ULC_NEXT_ALL   = wx.LIST_NEXT_ALL           # Searches for subsequent item by index
ULC_NEXT_BELOW = wx.LIST_NEXT_BELOW         # Searches for an item below the specified item
ULC_NEXT_LEFT  = wx.LIST_NEXT_LEFT          # Searches for an item to the left of the specified item
ULC_NEXT_RIGHT = wx.LIST_NEXT_RIGHT         # Searches for an item to the right of the specified item

# Alignment flags for Arrange (MSW only except ULC_ALIGN_LEFT)
ULC_ALIGN_DEFAULT      = wx.LIST_ALIGN_DEFAULT
ULC_ALIGN_LEFT         = wx.LIST_ALIGN_LEFT
ULC_ALIGN_TOP          = wx.LIST_ALIGN_TOP
ULC_ALIGN_SNAP_TO_GRID = wx.LIST_ALIGN_SNAP_TO_GRID

# Column format (MSW only except ULC_FORMAT_LEFT)
ULC_FORMAT_LEFT   = wx.LIST_FORMAT_LEFT
ULC_FORMAT_RIGHT  = wx.LIST_FORMAT_RIGHT
ULC_FORMAT_CENTRE = wx.LIST_FORMAT_CENTRE
ULC_FORMAT_CENTER = ULC_FORMAT_CENTRE

# Autosize values for SetColumnWidth
ULC_AUTOSIZE = wx.LIST_AUTOSIZE
ULC_AUTOSIZE_USEHEADER = wx.LIST_AUTOSIZE_USEHEADER      # partly supported by generic version

# Flag values for GetItemRect
ULC_RECT_BOUNDS = wx.LIST_RECT_BOUNDS
ULC_RECT_ICON   = wx.LIST_RECT_ICON
ULC_RECT_LABEL  = wx.LIST_RECT_LABEL

# Flag values for FindItem (MSW only)
ULC_FIND_UP    = wx.LIST_FIND_UP
ULC_FIND_DOWN  = wx.LIST_FIND_DOWN
ULC_FIND_LEFT  = wx.LIST_FIND_LEFT
ULC_FIND_RIGHT = wx.LIST_FIND_RIGHT

# Items/subitems rect
ULC_GETSUBITEMRECT_WHOLEITEM = wx.LIST_GETSUBITEMRECT_WHOLEITEM

# ----------------------------------------------------------------------------
# UltimateListCtrl event macros
# ----------------------------------------------------------------------------

wxEVT_COMMAND_LIST_BEGIN_DRAG = wx.wxEVT_COMMAND_LIST_BEGIN_DRAG
wxEVT_COMMAND_LIST_BEGIN_RDRAG = wx.wxEVT_COMMAND_LIST_BEGIN_RDRAG
wxEVT_COMMAND_LIST_BEGIN_LABEL_EDIT = wx.wxEVT_COMMAND_LIST_BEGIN_LABEL_EDIT
wxEVT_COMMAND_LIST_END_LABEL_EDIT = wx.wxEVT_COMMAND_LIST_END_LABEL_EDIT
wxEVT_COMMAND_LIST_DELETE_ITEM = wx.wxEVT_COMMAND_LIST_DELETE_ITEM
wxEVT_COMMAND_LIST_DELETE_ALL_ITEMS = wx.wxEVT_COMMAND_LIST_DELETE_ALL_ITEMS
wxEVT_COMMAND_LIST_ITEM_SELECTED = wx.wxEVT_COMMAND_LIST_ITEM_SELECTED
wxEVT_COMMAND_LIST_ITEM_DESELECTED = wx.wxEVT_COMMAND_LIST_ITEM_DESELECTED
wxEVT_COMMAND_LIST_KEY_DOWN = wx.wxEVT_COMMAND_LIST_KEY_DOWN
wxEVT_COMMAND_LIST_INSERT_ITEM = wx.wxEVT_COMMAND_LIST_INSERT_ITEM
wxEVT_COMMAND_LIST_COL_CLICK = wx.wxEVT_COMMAND_LIST_COL_CLICK
wxEVT_COMMAND_LIST_ITEM_RIGHT_CLICK = wx.wxEVT_COMMAND_LIST_ITEM_RIGHT_CLICK
wxEVT_COMMAND_LIST_ITEM_MIDDLE_CLICK = wx.wxEVT_COMMAND_LIST_ITEM_MIDDLE_CLICK
wxEVT_COMMAND_LIST_ITEM_ACTIVATED = wx.wxEVT_COMMAND_LIST_ITEM_ACTIVATED
wxEVT_COMMAND_LIST_CACHE_HINT = wx.wxEVT_COMMAND_LIST_CACHE_HINT
wxEVT_COMMAND_LIST_COL_RIGHT_CLICK = wx.wxEVT_COMMAND_LIST_COL_RIGHT_CLICK
wxEVT_COMMAND_LIST_COL_BEGIN_DRAG = wx.wxEVT_COMMAND_LIST_COL_BEGIN_DRAG
wxEVT_COMMAND_LIST_COL_DRAGGING = wx.wxEVT_COMMAND_LIST_COL_DRAGGING
wxEVT_COMMAND_LIST_COL_END_DRAG = wx.wxEVT_COMMAND_LIST_COL_END_DRAG
wxEVT_COMMAND_LIST_ITEM_FOCUSED = wx.wxEVT_COMMAND_LIST_ITEM_FOCUSED

wxEVT_COMMAND_LIST_FOOTER_CLICK = wx.NewEventType()
wxEVT_COMMAND_LIST_FOOTER_RIGHT_CLICK = wx.NewEventType()
wxEVT_COMMAND_LIST_FOOTER_CHECKING = wx.NewEventType()
wxEVT_COMMAND_LIST_FOOTER_CHECKED = wx.NewEventType()

wxEVT_COMMAND_LIST_ITEM_LEFT_CLICK = wx.NewEventType()
wxEVT_COMMAND_LIST_ITEM_CHECKING = wx.NewEventType()
wxEVT_COMMAND_LIST_ITEM_CHECKED = wx.NewEventType()
wxEVT_COMMAND_LIST_ITEM_HYPERLINK = wx.NewEventType()
wxEVT_COMMAND_LIST_END_DRAG = wx.NewEventType()
wxEVT_COMMAND_LIST_COL_CHECKING = wx.NewEventType()
wxEVT_COMMAND_LIST_COL_CHECKED = wx.NewEventType()

EVT_LIST_BEGIN_DRAG = wx.EVT_LIST_BEGIN_DRAG
EVT_LIST_BEGIN_RDRAG = wx.EVT_LIST_BEGIN_RDRAG
EVT_LIST_BEGIN_LABEL_EDIT = wx.EVT_LIST_BEGIN_LABEL_EDIT
EVT_LIST_END_LABEL_EDIT = wx.EVT_LIST_END_LABEL_EDIT
EVT_LIST_DELETE_ITEM = wx.EVT_LIST_DELETE_ITEM
EVT_LIST_DELETE_ALL_ITEMS = wx.EVT_LIST_DELETE_ALL_ITEMS
EVT_LIST_KEY_DOWN = wx.EVT_LIST_KEY_DOWN
EVT_LIST_INSERT_ITEM = wx.EVT_LIST_INSERT_ITEM
EVT_LIST_COL_CLICK = wx.EVT_LIST_COL_CLICK
EVT_LIST_COL_RIGHT_CLICK = wx.EVT_LIST_COL_RIGHT_CLICK
EVT_LIST_COL_BEGIN_DRAG = wx.EVT_LIST_COL_BEGIN_DRAG
EVT_LIST_COL_END_DRAG = wx.EVT_LIST_COL_END_DRAG
EVT_LIST_COL_DRAGGING = wx.EVT_LIST_COL_DRAGGING
EVT_LIST_ITEM_SELECTED = wx.EVT_LIST_ITEM_SELECTED
EVT_LIST_ITEM_DESELECTED = wx.EVT_LIST_ITEM_DESELECTED
EVT_LIST_ITEM_RIGHT_CLICK = wx.EVT_LIST_ITEM_RIGHT_CLICK
EVT_LIST_ITEM_MIDDLE_CLICK = wx.EVT_LIST_ITEM_MIDDLE_CLICK
EVT_LIST_ITEM_ACTIVATED = wx.EVT_LIST_ITEM_ACTIVATED
EVT_LIST_ITEM_FOCUSED = wx.EVT_LIST_ITEM_FOCUSED
EVT_LIST_CACHE_HINT = wx.EVT_LIST_CACHE_HINT

EVT_LIST_ITEM_LEFT_CLICK = wx.PyEventBinder(wxEVT_COMMAND_LIST_ITEM_LEFT_CLICK, 1)
EVT_LIST_ITEM_CHECKING = wx.PyEventBinder(wxEVT_COMMAND_LIST_ITEM_CHECKING, 1)
EVT_LIST_ITEM_CHECKED = wx.PyEventBinder(wxEVT_COMMAND_LIST_ITEM_CHECKED, 1)
EVT_LIST_ITEM_HYPERLINK = wx.PyEventBinder(wxEVT_COMMAND_LIST_ITEM_HYPERLINK, 1)
EVT_LIST_END_DRAG = wx.PyEventBinder(wxEVT_COMMAND_LIST_END_DRAG, 1)
EVT_LIST_COL_CHECKING = wx.PyEventBinder(wxEVT_COMMAND_LIST_COL_CHECKING, 1)
EVT_LIST_COL_CHECKED = wx.PyEventBinder(wxEVT_COMMAND_LIST_COL_CHECKED, 1)

EVT_LIST_FOOTER_CLICK = wx.PyEventBinder(wxEVT_COMMAND_LIST_FOOTER_CLICK, 1)
EVT_LIST_FOOTER_RIGHT_CLICK = wx.PyEventBinder(wxEVT_COMMAND_LIST_FOOTER_RIGHT_CLICK, 1)
EVT_LIST_FOOTER_CHECKING = wx.PyEventBinder(wxEVT_COMMAND_LIST_FOOTER_CHECKING, 1)
EVT_LIST_FOOTER_CHECKED = wx.PyEventBinder(wxEVT_COMMAND_LIST_FOOTER_CHECKED, 1)

# NOTE: If using the wxExtListBox visual attributes works everywhere then this can
# be removed, as well as the #else case below.

_USE_VISATTR = 0


# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

SCROLL_UNIT_X = 15
SCROLL_UNIT_Y = 15

# the spacing between the lines (in report mode)
LINE_SPACING = 0

# extra margins around the text label
EXTRA_WIDTH = 4
EXTRA_HEIGHT = 4

if wx.Platform == "__WXGTK__":
    EXTRA_HEIGHT = 6

# margin between the window and the items
EXTRA_BORDER_X = 2
EXTRA_BORDER_Y = 2

# offset for the header window
HEADER_OFFSET_X = 1
HEADER_OFFSET_Y = 1

# margin between rows of icons in [small] icon view
MARGIN_BETWEEN_ROWS = 6

# when autosizing the columns, add some slack
AUTOSIZE_COL_MARGIN = 10

# default and minimal widths for the header columns
WIDTH_COL_DEFAULT = 80
WIDTH_COL_MIN = 10

# the space between the image and the text in the report mode
IMAGE_MARGIN_IN_REPORT_MODE = 5

# the space between the image and the text in the report mode in header
HEADER_IMAGE_MARGIN_IN_REPORT_MODE = 2

# and the width of the icon, if any
MARGIN_BETWEEN_TEXT_AND_ICON = 2

# Background Image Style
_StyleTile = 0
_StyleStretch = 1

# Windows Vista Colours
_rgbSelectOuter = wx.Colour(170, 200, 245)
_rgbSelectInner = wx.Colour(230, 250, 250)
_rgbSelectTop = wx.Colour(210, 240, 250)
_rgbSelectBottom = wx.Colour(185, 215, 250)
_rgbNoFocusTop = wx.Colour(250, 250, 250)
_rgbNoFocusBottom = wx.Colour(235, 235, 235)
_rgbNoFocusOuter = wx.Colour(220, 220, 220)
_rgbNoFocusInner = wx.Colour(245, 245, 245)

# Mouse hover time for track selection
HOVER_TIME = 400
if wx.Platform == "__WXMSW__":
    try:
        import win32gui, win32con
        HOVER_TIME = win32gui.SystemParametersInfo(win32con.SPI_GETMOUSEHOVERTIME)
    except ImportError:
        pass


# Utility method
def to_list(input):

    if isinstance(input, types.ListType):
        return input
    elif isinstance(input, types.IntType):
        return [input]
    else:
        raise Exception("Invalid parameter passed to `to_list`: only integers and list are accepted.")


def CheckVariableRowHeight(listCtrl, text):

    if not listCtrl.HasExtraFlag(ULC_HAS_VARIABLE_ROW_HEIGHT):
        if "\n" in text:
            raise Exception("Multiline text items are not allowed without the ULC_HAS_VARIABLE_ROW_HEIGHT extra style.")


def CreateListItem(itemOrId, col):

    if type(itemOrId) == types.IntType:
        item = UltimateListItem()
        item._itemId = itemOrId
        item._col = col
    else:
        item = itemOrId

    return item


def GrayOut(anImage):
    """
    Convert the given image (in place) to a grayed-out version,
    appropriate for a 'disabled' appearance.
    """

    factor = 0.7        # 0 < f < 1.  Higher Is Grayer

    if anImage.HasMask():
        maskColour = (anImage.GetMaskRed(), anImage.GetMaskGreen(), anImage.GetMaskBlue())
    else:
        maskColour = None

    data = map(ord, list(anImage.GetData()))

    for i in range(0, len(data), 3):

        pixel = (data[i], data[i+1], data[i+2])
        pixel = MakeGray(pixel, factor, maskColour)

        for x in range(3):
            data[i+x] = pixel[x]

    anImage.SetData(''.join(map(chr, data)))

    return anImage


def MakeGray((r,g,b), factor, maskColour):
    """
    Make a pixel grayed-out. If the pixel matches the maskcolour, it won't be
    changed.
    """

    if (r,g,b) != maskColour:
        return map(lambda x: int((230 - x) * factor) + x, (r,g,b))
    else:
        return (r,g,b)


#----------------------------------------------------------------------
def GetdragcursorData():
    return zlib.decompress(
"x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd2\xa2@,\xcf\xc1\
\x06$9z\xda>\x00)\xce\x02\x8f\xc8b\x06\x06na\x10fd\x985G\x02(\xd8W\xe2\x1aQ\
\xe2\x9c\x9f\x9b\x9b\x9aW\xc2\x90\xec\x11\xe4\xab\x90\x9cQ\x9a\x97\x9d\x93\
\x9a\xa7`l\xa4\x90\x99\x9e\x97_\x94\x9a\xc2\xeb\x18\xec\xec\xe9i\xa5\xa0\xa7\
W\xa5\xaa\x07\x01P:7\x1eH\xe4\xe8\xe9\xd9\x808\x11\xbc\x1e\xae\x11V\n\x06@`\
\xeehd\n\xa2-\x0c,\x8cA\xb4\x9b\t\x94o\xe2b\x08\xa2\xcd\\L\xdd@\xb4\xab\x85\
\x993\x886v\xb6p\x02\xd1\x86N\xa6\x16\x12\xf7~\xdf\x05\xbal\xa9\xa7\x8bcH\
\xc5\x9c3W9\xb9\x1a\x14\x04X/\xec\xfc\xbft\xed\x02\xa5\xf4\xc2m\xfa*<N\x17??\
\x0frqy\x9c\xd3\xb2f5\xaf\x89\x8f9Gk\xbc\x08\xa7\xbf\x06\x97\x98\x06S\xd8E\
\xbd\x9cE\xb2\x15\x9da\x89\xe2k\x0f\x9c\xb6|\x1a\xea\x14X\x1d6G\x83E\xe7\x9c\
\x1dO\xa8\xde\xb6\x84l\x15\x9eS\xcf\xc2tf\x15\xde\xf7\xb5\xb2]\xf0\x96+\xf5@\
D\x90\x1d\xef19_\xf5\xde5y\xb6+\xa7\xdeZ\xfbA\x9bu\x9f`\xffD\xafYn\xf6\x9eW\
\xeb>\xb6\x7f\x98\\U\xcb\xf5\xd5\xcb\x9a'\xe7\xf4\xd7\x0b\xba\x9e\xdb\x17E\
\xfdf\x97Z\xcb\xcc\xc0\xf0\xff?3\xc3\x92\xabN\x8arB\xc7\x8f\x03\x1d\xcc\xe0\
\xe9\xea\xe7\xb2\xce)\xa1\t\x00B7|\x00" )

def GetdragcursorBitmap():
    return wx.BitmapFromImage(GetdragcursorImage())

def GetdragcursorImage():
    stream = cStringIO.StringIO(GetdragcursorData())
    return wx.ImageFromStream(stream)


class SelectionStore(object):

    def __init__(self):

        # the array of items whose selection state is different from default
        self._itemsSel = []
        # the default state: normally, False (i.e. off) but maybe set to true if
        # there are more selected items than non selected ones - this allows to
        # handle selection of all items efficiently
        self._defaultState = False
        # the total number of items we handle
        self._count  = 0

    # special case of SetItemCount(0)
    def Clear(self):

        self._itemsSel = []
        self._count = 0
        self._defaultState = False

    # return the total number of selected items
    def GetSelectedCount(self):

        return (self._defaultState and [self._count - len(self._itemsSel)] or [len(self._itemsSel)])[0]


    def IsSelected(self, item):

        isSel = item in self._itemsSel

        # if the default state is to be selected, being in m_itemsSel means that
        # the item is not selected, so we have to inverse the logic
        return (self._defaultState and [not isSel] or [isSel])[0]


    def SelectItem(self, item, select=True):

        # search for the item ourselves as like this we get the index where to
        # insert it later if needed, so we do only one search in the array instead
        # of two (adding item to a sorted array requires a search)
        index = bisect.bisect_right(self._itemsSel, item)
        isSel = index < len(self._itemsSel) and self._itemsSel[index] == item

        if select != self._defaultState:

            if item not in self._itemsSel:
                bisect.insort_right(self._itemsSel, item)
                return True

        else: # reset to default state

            if item in self._itemsSel:
                self._itemsSel.remove(item)
                return True

        return False


    def SelectRange(self, itemFrom, itemTo, select=True):

        # 100 is hardcoded but it shouldn't matter much: the important thing is
        # that we don't refresh everything when really few (e.g. 1 or 2) items
        # change state
        MANY_ITEMS = 100

        # many items (> half) changed state
        itemsChanged = []

        # are we going to have more [un]selected items than the other ones?
        if itemTo - itemFrom > self._count/2:

            if select != self._defaultState:

                # the default state now becomes the same as 'select'
                self._defaultState = select

                # so all the old selections (which had state select) shouldn't be
                # selected any more, but all the other ones should
                selOld = self._itemsSel[:]
                self._itemsSel = []

                # TODO: it should be possible to optimize the searches a bit
                #       knowing the possible range

                for item in xrange(itemFrom):
                    if item not in selOld:
                        self._itemsSel.append(item)

                for item in xrange(itemTo + 1, self._count):
                    if item not in selOld:
                        self._itemsSel.append(item)

            else: # select == self._defaultState

                # get the inclusive range of items between itemFrom and itemTo
                count = len(self._itemsSel)
                start = bisect.bisect_right(self._itemsSel, itemFrom)
                end = bisect.bisect_right(self._itemsSel, itemTo)

                if start == count or self._itemsSel[start] < itemFrom:
                    start += 1

                if end == count or self._itemsSel[end] > itemTo:
                    end -= 1

                if start <= end:

                    # delete all of them (from end to avoid changing indices)
                    for i in xrange(end, start-1, -1):
                        if itemsChanged:
                            if len(itemsChanged) > MANY_ITEMS:
                                # stop counting (see comment below)
                                itemsChanged = []
                            else:
                                itemsChanged.append(self._itemsSel[i])

                        self._itemsSel.pop(i)
                else:
                    self._itemsSel = []

        else: # "few" items change state

            if itemsChanged:
                itemsChanged = []

            # just add the items to the selection
            for item in xrange(itemFrom, itemTo+1):
                if self.SelectItem(item, select) and itemsChanged:
                    itemsChanged.append(item)
                    if len(itemsChanged) > MANY_ITEMS:
                        # stop counting them, we'll just eat gobs of memory
                        # for nothing at all - faster to refresh everything in
                        # this case
                        itemsChanged = []

        # we set it to None if there are many items changing state
        return itemsChanged


    def OnItemDelete(self, item):

        count = len(self._itemsSel)
        i = bisect.bisect_right(self._itemsSel, item)

        if i < count and self._itemsSel[i] == item:
            # this item itself was in m_itemsSel, remove it from there
            self._itemsSel.pop(i)

            count -= 1

        # and adjust the index of all which follow it
        while i < count:

            i += 1
            self._itemsSel[i] -= 1


    def SetItemCount(self, count):

        # forget about all items whose indices are now invalid if the size
        # decreased
        if count < self._count:
            for i in xrange(len(self._itemsSel), 0, -1):
                if self._itemsSel[i - 1] >= count:
                    self._itemsSel.pop(i - 1)

        # remember the new number of items
        self._count = count


# ----------------------------------------------------------------------------
# UltimateListItemAttr: a structure containing the visual attributes of an item
# ----------------------------------------------------------------------------

class UltimateListItemAttr(object):

    def __init__(self, colText=wx.NullColour, colBack=wx.NullColour, font=wx.NullFont,
                 enabled=True, footerColText=wx.NullColour, footerColBack=wx.NullColour,
                 footerFont=wx.NullFont):

        self._colText = colText
        self._colBack = colBack
        self._font = font
        self._enabled = enabled

        self._footerColText = footerColText
        self._footerColBack = footerColBack
        self._footerFont = footerFont


    # setters
    def SetTextColour(self, colText):

        self._colText = colText


    def SetBackgroundColour(self, colBack):

        self._colBack = colBack


    def SetFont(self, font):

        self._font = font


    def Enable(self, enable=True):

        self._enabled = enable


    def SetFooterTextColour(self, colText):

        self._footerColText = colText


    def SetFooterBackgroundColour(self, colBack):

        self._footerColBack = colBack


    def SetFooterFont(self, font):

        self._footerFont = font


    # accessors
    def HasTextColour(self):

        return self._colText.Ok()


    def HasBackgroundColour(self):

        return self._colBack.Ok()


    def HasFont(self):

        return self._font.Ok()


    def HasFooterTextColour(self):

        return self._footerColText.Ok()


    def HasFooterBackgroundColour(self):

        return self._footerColBack.Ok()


    def HasFooterFont(self):

        return self._footerFont.Ok()


    # getters
    def GetTextColour(self):

        return self._colText


    def GetBackgroundColour(self):

        return self._colBack


    def GetFont(self):

        return self._font


    def GetFooterTextColour(self):

        return self._footerColText


    def GetFooterBackgroundColour(self):

        return self._footerColBack


    def GetFooterFont(self):

        return self._footerFont


    def IsEnabled(self):

        return self._enabled

# ----------------------------------------------------------------------------
# UltimateListItem: the item or column info, used to exchange data with UltimateListCtrl
# ----------------------------------------------------------------------------

class UltimateListItem(wx.Object):

    def __init__(self, item=None):

        if not item:
            self.Init()
            self._attr = None
        else:
            self._mask = item._mask              # Indicates what fields are valid
            self._itemId = item._itemId          # The zero-based item position
            self._col = item._col                # Zero-based column, if in report mode
            self._state = item._state            # The state of the item
            self._stateMask = item._stateMask    # Which flags of self._state are valid (uses same flags)
            self._text = item._text              # The label/header text
            self._image = item._image[:]         # The zero-based indexes into an image list
            self._data = item._data              # App-defined data
            self._pyData = item._pyData          # Python-specific data
            self._format = item._format          # left, right, centre
            self._width = item._width            # width of column
            self._colour = item._colour          # item text colour
            self._font = item._font              # item font
            self._checked = item._checked        # The checking state for the item (if kind > 0)
            self._kind = item._kind              # Whether it is a normal, checkbox-like or a radiobutton-like item
            self._enabled = item._enabled        # Whether the item is enabled or not
            self._hypertext = item._hypertext    # indicates if the item is hypertext
            self._visited = item._visited        # visited state for an hypertext item
            self._wnd = item._wnd
            self._windowenabled = item._windowenabled
            self._windowsize = item._windowsize
            self._isColumnShown = item._isColumnShown
            self._customRenderer = item._customRenderer
            self._overFlow = item._overFlow
            self._footerChecked = item._footerChecked
            self._footerFormat = item._footerFormat
            self._footerImage = item._footerImage
            self._footerKind = item._footerKind
            self._footerText = item._footerText
            self._expandWin = item._expandWin
            self._attr = None

            # copy list item attributes
            if item.HasAttributes():
                self._attr = item.GetAttributes()[:]

    # resetting
    def Clear(self):

        self.Init()
        self._text = ""
        self.ClearAttributes()


    def ClearAttributes(self):

        if self._attr:
            del self._attr
            self._attr = None

    # setters
    def SetMask(self, mask):

        self._mask = mask


    def SetId(self, id):

        self._itemId = id


    def SetColumn(self, col):

        self._col = col


    def SetState(self, state):

        self._mask |= ULC_MASK_STATE
        self._state = state
        self._stateMask |= state


    def SetStateMask(self, stateMask):

        self._stateMask = stateMask


    def SetText(self, text):

        self._mask |= ULC_MASK_TEXT
        self._text = text


    def SetImage(self, image):

        self._mask |= ULC_MASK_IMAGE
        self._image = to_list(image)


    def SetData(self, data):

        self._mask |= ULC_MASK_DATA
        self._data = data


    def SetPyData(self, pyData):

        self._mask |= ULC_MASK_PYDATA
        self._pyData = pyData


    def SetWidth(self, width):

        self._mask |= ULC_MASK_WIDTH
        self._width = width


    def SetAlign(self, align):

        self._mask |= ULC_MASK_FORMAT
        self._format = align


    def SetTextColour(self, colText):

        self.Attributes().SetTextColour(colText)


    def SetBackgroundColour(self, colBack):

        self.Attributes().SetBackgroundColour(colBack)


    def SetFont(self, font):

        self.Attributes().SetFont(font)


    def SetFooterTextColour(self, colText):

        self.Attributes().SetFooterTextColour(colText)


    def SetFooterBackgroundColour(self, colBack):

        self.Attributes().SetFooterBackgroundColour(colBack)


    def SetFooterFont(self, font):

        self.Attributes().SetFooterFont(font)


    def Enable(self, enable=True):

        self.Attributes().Enable(enable)

    # accessors
    def GetMask(self):

        return self._mask


    def GetId(self):

        return self._itemId


    def GetColumn(self):

        return self._col


    def GetState(self):

        return self._state & self._stateMask


    def GetText(self):

        return self._text


    def GetImage(self):

        return self._image


    def GetData(self):

        return self._data


    def GetPyData(self):

        return self._pyData


    def GetWidth(self):

        return self._width


    def GetAlign(self):

        return self._format


    def GetAttributes(self):

        return self._attr


    def HasAttributes(self):

        return self._attr != None


    def GetTextColour(self):

        return (self.HasAttributes() and [self._attr.GetTextColour()] or [wx.NullColour])[0]


    def GetBackgroundColour(self):

        return (self.HasAttributes() and [self._attr.GetBackgroundColour()] or [wx.NullColour])[0]


    def GetFont(self):

        return (self.HasAttributes() and [self._attr.GetFont()] or [wx.NullFont])[0]


    def IsEnabled(self):

        return (self.HasAttributes() and [self._attr.IsEnabled()] or [True])[0]

    # creates self._attr if we don't have it yet
    def Attributes(self):

        if not self._attr:
            self._attr = UltimateListItemAttr()

        return self._attr


    def SetKind(self, kind):

        self._mask |= ULC_MASK_KIND
        self._kind = kind


    def GetKind(self):

        return self._kind


    def IsChecked(self):
        """Returns whether the item is checked or not."""

        return self._checked


    def Check(self, checked=True):
        """Check an item. Meaningful only for check and radio items."""

        self._mask |= ULC_MASK_CHECK
        self._checked = checked


    def IsShown(self):

        return self._isColumnShown


    def SetShown(self, shown=True):

        self._mask |= ULC_MASK_SHOWN
        self._isColumnShown = shown


    def SetHyperText(self, hyper=True):
        """Sets whether the item is hypertext or not."""

        self._mask |= ULC_MASK_HYPERTEXT
        self._hypertext = hyper


    def SetVisited(self, visited=True):
        """Sets whether an hypertext item was visited or not."""

        self._mask |= ULC_MASK_HYPERTEXT
        self._visited = visited


    def GetVisited(self):
        """Returns whether an hypertext item was visited or not."""

        return self._visited


    def IsHyperText(self):
        """Returns whether the item is hypetext or not."""

        return self._hypertext


    def SetWindow(self, wnd, expand=False):
        """Sets the window associated to the item."""

        self._mask |= ULC_MASK_WINDOW
        self._wnd = wnd

        listCtrl = wnd.GetParent()
        wnd.Reparent(listCtrl._mainWin)

        if wnd.GetSizer():      # the window is a complex one hold by a sizer
            size = wnd.GetBestSize()
        else:                   # simple window, without sizers
            size = wnd.GetSize()

        # We have to bind the wx.EVT_SET_FOCUS for the associated window
        # No other solution to handle the focus changing from an item in
        # CustomTreeCtrl and the window associated to an item
        # Do better strategies exist?
        self._wnd.Bind(wx.EVT_SET_FOCUS, self.OnSetFocus)
        self._windowsize = size

        # The window is enabled only if the item is enabled
        self._wnd.Enable(self._enabled)
        self._windowenabled = self._enabled
        self._expandWin = expand

        listCtrl._mainWin._hasWindows = True
        listCtrl._mainWin._itemWithWindow.append(self)


    def GetWindow(self):
        """Returns the window associated to the item."""

        return self._wnd


    def DeleteWindow(self):
        """Deletes the window associated to the item (if any)."""

        if self._wnd:
            listCtrl = self._wnd.GetParent()
            if self in listCtrl._itemWithWindow:
                listCtrl._itemWithWindow.remove(self)
            self._wnd.Destroy()
            self._wnd = None


    def GetWindowEnabled(self):
        """Returns whether the associated window is enabled or not."""

        if not self._wnd:
            raise Exception("\nERROR: This Item Has No Window Associated")

        return self._windowenabled


    def SetWindowEnabled(self, enable=True):
        """Sets whether the associated window is enabled or not."""

        if not self._wnd:
            raise Exception("\nERROR: This Item Has No Window Associated")

        self._windowenabled = enable
        self._wnd.Enable(enable)


    def GetWindowSize(self):
        """Returns the associated window size."""

        return self._windowsize


    def SetCustomRenderer(self, renderer):

        self._mask |= ULC_MASK_RENDERER
        self._customRenderer = renderer


    def GetCustomRenderer(self):

        return self._customRenderer


    def SetOverFlow(self, over=True):

        self._mask |= ULC_MASK_OVERFLOW
        self._overFlow = over


    def GetOverFlow(self):

        return self._overFlow


    def Init(self):

        self._mask = 0
        self._itemId = 0
        self._col = 0
        self._state = 0
        self._stateMask = 0
        self._image = []
        self._data = 0
        self._pyData = None
        self._text = ""

        self._format = ULC_FORMAT_CENTRE
        self._width = 0

        self._colour = wx.Colour(0, 0, 0)
        self._font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)

        self._kind = 0
        self._checked = False

        self._hypertext = False    # indicates if the item is hypertext
        self._visited = False      # visited state for an hypertext item

        self._wnd = None
        self._windowenabled = False
        self._windowsize = wx.Size()
        self._isColumnShown = True

        self._customRenderer = None
        self._overFlow = False
        self._footerChecked = False
        self._footerFormat = ULC_FORMAT_CENTRE
        self._footerImage = []
        self._footerKind = 0
        self._footerText = ""
        self._expandWin = False


    def SetFooterKind(self, kind):

        self._mask |= ULC_MASK_FOOTER_KIND
        self._footerKind = kind


    def GetFooterKind(self):

        return self._footerKind


    def IsFooterChecked(self):
        """Returns whether the item is checked or not."""

        return self._footerChecked


    def CheckFooter(self, checked=True):
        """Check an item. Meaningful only for check and radio items."""

        self._mask |= ULC_MASK_FOOTER_CHECK
        self._footerChecked = checked


    def GetFooterFormat(self):

        return self._footerFormat


    def SetFooterFormat(self, format):

        self._mask |= ULC_MASK_FOOTER_FORMAT
        self._footerFormat = format


    def GetFooterText(self):

        return self._footerText


    def SetFooterText(self, text):

        self._mask |= ULC_MASK_FOOTER_TEXT
        self._footerText = text


    def GetFooterImage(self):

        return self._footerImage


    def SetFooterImage(self, image):

        self._mask |= ULC_MASK_FOOTER_IMAGE
        self._footerImage = to_list(image)


    def GetFooterTextColour(self):

        return (self.HasAttributes() and [self._attr.GetFooterTextColour()] or [wx.NullColour])[0]


    def GetFooterBackgroundColour(self):

        return (self.HasAttributes() and [self._attr.GetFooterBackgroundColour()] or [wx.NullColour])[0]


    def GetFooterFont(self):

        return (self.HasAttributes() and [self._attr.GetFooterFont()] or [wx.NullFont])[0]


    def SetFooterAlign(self, align):

        self._mask |= ULC_MASK_FOOTER_FORMAT
        self._footerFormat = align


    def GetFooterAlign(self):

        return self._footerFormat


    def OnSetFocus(self, event):
        """Handles the wx.EVT_SET_FOCUS event for the associated window."""

        listCtrl = self._wnd.GetParent()
        select = listCtrl.GetItemState(self._itemId, ULC_STATE_SELECTED)

        # If the window is associated to an item that currently is selected
        # (has focus) we don't kill the focus. Otherwise we do it.
        if not select:
            listCtrl._hasFocus = False
        else:
            listCtrl._hasFocus = True

        listCtrl.SetFocus()

        event.Skip()

# ----------------------------------------------------------------------------
# ListEvent - the event class for the UltimateListCtrl notifications
# ----------------------------------------------------------------------------

class CommandListEvent(wx.PyCommandEvent):

    def __init__(self, commandTypeOrEvent=None, winid=0):

        if type(commandTypeOrEvent) == types.IntType:

            wx.PyCommandEvent.__init__(self, commandTypeOrEvent, winid)

            self.m_code = 0
            self.m_oldItemIndex = 0
            self.m_itemIndex = 0
            self.m_col = 0
            self.m_pointDrag = wx.Point()
            self.m_item = UltimateListItem()
            self.m_editCancelled = False

        else:

            wx.PyCommandEvent.__init__(self, commandTypeOrEvent.GetEventType(), commandTypeOrEvent.GetId())
            self.m_code = commandTypeOrEvent.m_code
            self.m_oldItemIndex = commandTypeOrEvent.m_oldItemIndex
            self.m_itemIndex = commandTypeOrEvent.m_itemIndex
            self.m_col = commandTypeOrEvent.m_col
            self.m_pointDrag = commandTypeOrEvent.m_pointDrag
            self.m_item = commandTypeOrEvent.m_item
            self.m_editCancelled = commandTypeOrEvent.m_editCancelled


    def GetKeyCode(self):

        return self.m_code


    def GetIndex(self):

        return self.m_itemIndex


    def GetColumn(self):

        return self.m_col


    def GetPoint(self):

        return self.m_pointDrag


    def GetLabel(self):

        return self.m_item._text


    def GetText(self):

        return self.m_item._text


    def GetImage(self):

        return self.m_item._image


    def GetData(self):

        return self.m_item._data


    def GetMask(self):

        return self.m_item._mask


    def GetItem(self):

        return self.m_item


    # for wxEVT_COMMAND_LIST_CACHE_HINT only
    def GetCacheFrom(self):

        return self.m_oldItemIndex


    def GetCacheTo(self):

        return self.m_itemIndex


    # was label editing canceled? (for wxEVT_COMMAND_LIST_END_LABEL_EDIT only)
    def IsEditCancelled(self):

        return self.m_editCancelled


    def SetEditCanceled(self, editCancelled):

        self.m_editCancelled = editCancelled


    def Clone(self):

        return UltimateListEvent(self)



# ----------------------------------------------------------------------------
# TreeEvent is a special class for all events associated with list controls
#
# NB: note that not all accessors make sense for all events, see the event
#     descriptions below
# ----------------------------------------------------------------------------

class UltimateListEvent(CommandListEvent):

    def __init__(self, commandTypeOrEvent=None, winid=0):
        """
        Default class constructor.
        For internal use: do not call it in your code!
        """

        CommandListEvent.__init__(self, commandTypeOrEvent, winid)

        if type(commandTypeOrEvent) == types.IntType:
            self.notify = wx.NotifyEvent(commandTypeOrEvent, winid)
        else:
            self.notify = wx.NotifyEvent(commandTypeOrEvent.GetEventType(), commandTypeOrEvent.GetId())


    def GetNotifyEvent(self):
        """Returns the actual wx.NotifyEvent."""

        return self.notify


    def IsAllowed(self):
        """Returns whether the event is allowed or not."""

        return self.notify.IsAllowed()


    def Veto(self):
        """Vetos the event."""

        self.notify.Veto()


    def Allow(self):
        """The event is allowed."""

        self.notify.Allow()


# ============================================================================
# private classes
# ============================================================================

#-----------------------------------------------------------------------------
#  ColWidthInfo (internal)
#-----------------------------------------------------------------------------

class ColWidthInfo(object):

    def __init__(self, w=0, needsUpdate=True):

        self._nMaxWidth = w
        self._bNeedsUpdate = needsUpdate


#-----------------------------------------------------------------------------
#  UltimateListItemData (internal)
#-----------------------------------------------------------------------------

class UltimateListItemData(object):

    def __init__(self, owner):


        # the list ctrl we are in
        self._owner = owner
        self.Init()

        # the item coordinates are not used in report mode, instead this pointer
        # is None and the owner window is used to retrieve the item position and
        # size

        if owner.InReportView():
            self._rect = None
        else:
            self._rect = wx.Rect()


    def SetImage(self, image):

        self._image = to_list(image)


    def SetData(self, data):

        self._data = data


    def HasText(self):

        return self._text != ""


    def GetText(self):

        return self._text


    def GetBackgroundColour(self):

        return self._backColour


    def GetColour(self):

        return self._colour


    def GetFont(self):

        return (self._hasFont and [self._font] or [wx.NullFont])[0]


    def SetText(self, text):

        self._text = text


    def SetColour(self, colour):

        if colour == wx.NullColour:
            self._hasColour = False
            del self._colour
            return

        self._hasColour = True
        self._colour = colour


    def SetFont(self, font):

        if font == wx.NullFont:
            self._hasFont = False
            del self._font
            return

        self._hasFont = True
        self._font = font


    def SetBackgroundColour(self, colour):

        if colour == wx.NullColour:
            self._hasBackColour = False
            del self._backColour
            return

        self._hasBackColour = True
        self._backColour = colour


    # we can't use empty string for measuring the string width/height, so
    # always return something
    def GetTextForMeasuring(self):

        s = self.GetText()
        if not s.strip():
            s = 'H'

        return s


    def GetImage(self):

        return self._image


    def HasImage(self):

        return len(self._image) > 0


    def SetKind(self, kind):

        self._kind = kind


    def GetKind(self):

        return self._kind


    def IsChecked(self):
        """Returns whether the item is checked or not."""

        return self._checked


    def Check(self, checked=True):
        """Check an item. Meaningful only for check and radio items."""

        self._checked = checked


    def SetHyperText(self, hyper=True):
        """Sets whether the item is hypertext or not."""

        self._hypertext = hyper


    def SetVisited(self, visited=True):
        """Sets whether an hypertext item was visited or not."""

        self._visited = visited


    def GetVisited(self):
        """Returns whether an hypertext item was visited or not."""

        return self._visited


    def IsHyperText(self):
        """Returns whether the item is hypetext or not."""

        return self._hypertext


    def SetWindow(self, wnd, expand=False):
        """Sets the window associated to the item."""

        self._mask |= ULC_MASK_WINDOW
        self._wnd = wnd

        if wnd.GetSizer():      # the window is a complex one hold by a sizer
            size = wnd.GetBestSize()
        else:                   # simple window, without sizers
            size = wnd.GetSize()

        # We have to bind the wx.EVT_SET_FOCUS for the associated window
        # No other solution to handle the focus changing from an item in
        # CustomTreeCtrl and the window associated to an item
        # Do better strategies exist?
        self._windowsize = size

        # The window is enabled only if the item is enabled
        self._wnd.Enable(self._enabled)
        self._windowenabled = self._enabled
        self._expandWin = expand


    def GetWindow(self):
        """Returns the window associated to the item."""

        return self._wnd


    def DeleteWindow(self):
        """Deletes the window associated to the item (if any)."""

        if self._wnd:
            self._wnd.Destroy()
            self._wnd = None


    def GetWindowEnabled(self):
        """Returns whether the associated window is enabled or not."""

        if not self._wnd:
            raise Exception("\nERROR: This Item Has No Window Associated")

        return self._windowenabled


    def SetWindowEnabled(self, enable=True):
        """Sets whether the associated window is enabled or not."""

        if not self._wnd:
            raise Exception("\nERROR: This Item Has No Window Associated")

        self._windowenabled = enable
        self._wnd.Enable(enable)


    def GetWindowSize(self):
        """Returns the associated window size."""

        return self._windowsize


    def SetAttr(self, attr):

        self._attr = attr


    def GetAttr(self):

        return self._attr


    def HasColour(self):

        return self._hasColour


    def HasFont(self):

        return self._hasFont


    def HasBackgroundColour(self):

        return self._hasBackColour


    def SetCustomRenderer(self, renderer):

        self._mask |= ULC_MASK_RENDERER
        self._customRenderer = renderer


    def GetCustomRenderer(self):

        return self._customRenderer


    def SetOverFlow(self, over=True):

        self._mask |= ULC_MASK_OVERFLOW
        self._overFlow = over


    def GetOverFlow(self):

        return self._overFlow


    def Init(self):

        # the item image or -1
        self._image = []
        # user data associated with the item
        self._data = 0
        self._pyData = None
        self._colour = wx.Colour(0, 0, 0)
        self._hasColour = False
        self._hasFont = False
        self._hasBackColour = False
        self._text = ""

        # kind = 0: normal item
        # kind = 1: checkbox-type item
        self._kind = 0
        self._checked = False

        self._enabled = True

        # custom attributes or None
        self._attr = None

        self._hypertext = False
        self._visited = False

        self._wnd = None
        self._windowenabled = True
        self._windowsize = wx.Size()
        self._isColumnShown = True
        self._customRenderer = None
        self._overFlow = False
        self._expandWin = False


    def SetItem(self, info):

        if info._mask & ULC_MASK_TEXT:
            CheckVariableRowHeight(self._owner, info._text)
            self.SetText(info._text)

        if info._mask & ULC_MASK_KIND:
            self._kind = info._kind

        if info._mask & ULC_MASK_CHECK:
            self._checked = info._checked

        if info._mask & ULC_MASK_ENABLE:
            self._enabled = info._enabled

        if info._mask & ULC_MASK_IMAGE:
            self._image = info._image[:]

        if info._mask & ULC_MASK_DATA:
            self._data = info._data

        if info._mask & ULC_MASK_PYDATA:
            self._pyData = info._pyData

        if info._mask & ULC_MASK_HYPERTEXT:
            self._hypertext = info._hypertext
            self._visited = info._visited

        if info._mask & ULC_MASK_FONTCOLOUR:
            self.SetColour(info.GetTextColour())

        if info._mask & ULC_MASK_FONT:
            self.SetFont(info.GetFont())

        if info._mask & ULC_MASK_BACKCOLOUR:
            self.SetBackgroundColour(info.GetBackgroundColour())

        if info._mask & ULC_MASK_WINDOW:
            self._wnd = info._wnd
            self._windowenabled = info._windowenabled
            self._windowsize = info._windowsize
            self._expandWin = info._expandWin

        if info._mask & ULC_MASK_SHOWN:
            self._isColumnShown = info._isColumnShown

        if info._mask & ULC_MASK_RENDERER:
            self._customRenderer = info._customRenderer

        if info._mask & ULC_MASK_OVERFLOW:
            self._overFlow = info._overFlow

        if info.HasAttributes():

            if self._attr:
                self._attr = info.GetAttributes()
            else:
                self._attr = UltimateListItemAttr(info.GetTextColour(), info.GetBackgroundColour(),
                                                  info.GetFont(), info.IsEnabled(), info.GetFooterTextColour(),
                                                  info.GetFooterBackgroundColour(), info.GetFooterFont())

        if self._rect:

            self._rect.x = -1
            self._rect.y = -1
            self._rect.height = 0
            self._rect.width = info._width


    def SetPosition(self, x, y):

        self._rect.x = x
        self._rect.y = y


    def SetSize(self, width, height):

        if width != -1:
            self._rect.width = width
        if height != -1:
            self._rect.height = height


    def IsHit(self, x, y):

        return wx.Rect(self.GetX(), self.GetY(), self.GetWidth(), self.GetHeight()).Contains((x, y))


    def GetX(self):

        return self._rect.x


    def GetY(self):

        return self._rect.y


    def GetWidth(self):

        return self._rect.width


    def GetHeight(self):

        return self._rect.height


    def GetItem(self, info):

        mask = info._mask
        if not mask:
            # by default, get everything for backwards compatibility
            mask = -1

        if mask & ULC_MASK_TEXT:
            info._text = self._text
        if mask & ULC_MASK_IMAGE:
            info._image = self._image[:]
        if mask & ULC_MASK_DATA:
            info._data = self._data
        if mask & ULC_MASK_PYDATA:
            info._pyData = self._pyData
        if info._mask & ULC_MASK_FONT:
            info.SetFont(self.GetFont())
        if mask & ULC_MASK_KIND:
            info._kind = self._kind
        if mask & ULC_MASK_CHECK:
            info._checked = self._checked
        if mask & ULC_MASK_ENABLE:
            info._enabled = self._enabled
        if mask & ULC_MASK_HYPERTEXT:
            info._hypertext = self._hypertext
            info._visited = self._visited
        if mask & ULC_MASK_WINDOW:
            info._wnd = self._wnd
            info._windowenabled = self._windowenabled
            info._windowsize = self._windowsize
            info._expandWin = self._expandWin
        if mask & ULC_MASK_SHOWN:
            info._isColumnShown = self._isColumnShown
        if mask & ULC_MASK_RENDERER:
            info._customRenderer = self._customRenderer
        if mask & ULC_MASK_OVERFLOW:
            info._overFlow = self._overFlow

        if self._attr:

            if self._attr.HasTextColour():
                info.SetTextColour(self._attr.GetTextColour())
            if self._attr.HasBackgroundColour():
                info.SetBackgroundColour(self._attr.GetBackgroundColour())
            if self._attr.HasFont():
                info.SetFont(self._attr.GetFont())
            info.Enable(self._attr.IsEnabled())

        return info


    def IsEnabled(self):

        return self._enabled


    def Enable(self, enable=True):

        self._enabled = enable


#-----------------------------------------------------------------------------
#  UltimateListHeaderData (internal)
#-----------------------------------------------------------------------------

class UltimateListHeaderData(object):

    def __init__(self, item=None):

        self.Init()

        if item:
            self.SetItem(item)


    def HasText(self):

        return self._text != ""


    def GetText(self):

        return self._text


    def SetText(self, text):

        self._text = text


    def GetFont(self):

        return self._font


    def Init(self):

        self._mask = 0
        self._image = []
        self._format = 0
        self._width = 0
        self._xpos = 0
        self._ypos = 0
        self._height = 0
        self._text = ""
        self._kind = 0
        self._checked = False
        self._font = wx.NullFont
        self._state = 0
        self._isColumnShown = True

        self._footerImage = []
        self._footerFormat = 0
        self._footerText = ""
        self._footerKind = 0
        self._footerChecked = False
        self._footerFont = wx.NullFont


    def SetItem(self, item):

        self._mask = item._mask

        if self._mask & ULC_MASK_TEXT:
            self._text = item._text

        if self._mask & ULC_MASK_FOOTER_TEXT:
            self._footerText = item._footerText

        if self._mask & ULC_MASK_IMAGE:
            self._image = item._image[:]

        if self._mask & ULC_MASK_FOOTER_IMAGE:
            self._footerImage = item._footerImage[:]

        if self._mask & ULC_MASK_FORMAT:
            self._format = item._format

        if self._mask & ULC_MASK_FOOTER_FORMAT:
            self._footerFormat = item._footerFormat

        if self._mask & ULC_MASK_WIDTH:
            self.SetWidth(item._width)

        if self._mask & ULC_MASK_FONT:
            self._font = item._font

        if self._mask & ULC_MASK_FOOTER_FONT:
            self._footerFont = item._footerFont

        if self._mask & ULC_MASK_FOOTER_KIND:
            self._footerKind = item._footerKind
            self._footerChecked = item._footerChecked

        if self._mask & ULC_MASK_KIND:
            self._kind = item._kind
            self._checked = item._checked

        if self._mask & ULC_MASK_CHECK:
            self._kind = item._kind
            self._checked = item._checked

        if self._mask & ULC_MASK_FOOTER_CHECK:
            self._footerKind = item._footerKind
            self._footerChecked = item._footerChecked

        if self._mask & ULC_MASK_STATE:
            self.SetState(item._state)

        if self._mask & ULC_MASK_SHOWN:
            self._isColumnShown = item._isColumnShown


    def SetState(self, flag):

        self._state = flag


    def SetPosition(self, x, y):

        self._xpos = x
        self._ypos = y


    def SetHeight(self, h):

        self._height = h


    def SetWidth(self, w):

        self._width = w

        if self._width < 0:
            self._width = WIDTH_COL_DEFAULT
        elif self._width < WIDTH_COL_MIN:
            self._width = WIDTH_COL_MIN


    def SetFormat(self, format):

        self._format = format


    def SetFooterFormat(self, format):

        self._footerFormat = format


    def HasImage(self):

        return len(self._image) > 0


    def HasFooterImage(self):

        return len(self._footerImage) > 0


    def IsHit(self, x, y):

        return ((x >= self._xpos) and (x <= self._xpos+self._width) and (y >= self._ypos) and (y <= self._ypos+self._height))


    def GetItem(self, item):

        item._mask = self._mask
        item._text = self._text
        item._image = self._image[:]
        item._format = self._format
        item._width = self._width
        if self._font:
            item._font = self._font
            item.Attributes().SetFont(self._font)

        item._kind = self._kind
        item._checked = self._checked
        item._state = self._state
        item._isColumnShown = self._isColumnShown

        item._footerImage = self._footerImage
        item._footerFormat = self._footerFormat
        item._footerText = self._footerText
        item._footerKind = self._footerKind
        item._footerChecked = self._footerChecked
        item._footerFont = self._footerFont

        return item


    def GetState(self):

        return self._state


    def GetImage(self):

        return self._image


    def GetFooterImage(self):

        return self._footerImage


    def GetWidth(self):

        return self._width


    def GetFormat(self):

        return self._format


    def GetFooterFormat(self):

        return self._footerFormat


    def SetFont(self, font):

        self._font = font


    def SetFooterFont(self, font):

        self._footerFont = font


    def SetKind(self, kind):

        self._kind = kind


    def SetFooterKind(self, kind):

        self._footerKind = kind


    def GetKind(self):

        return self._kind


    def GetFooterKind(self):

        return self._footerKind


    def IsChecked(self):
        """Returns whether the item is checked or not."""

        return self._checked


    def Check(self, checked=True):
        """Check an item. Meaningful only for check and radio items."""

        self._checked = checked


    def IsFooterChecked(self):

        return self._footerChecked


    def CheckFooter(self, check=True):

        self._footerChecked = check


#-----------------------------------------------------------------------------
#  GeometryInfo (internal)
#  this is not used in report view
#-----------------------------------------------------------------------------

class GeometryInfo(object):

    def __init__(self):

        # total item rect
        self._rectAll = wx.Rect()

        # label only
        self._rectLabel = wx.Rect()

        # icon only
        self._rectIcon = wx.Rect()

        # the part to be highlighted
        self._rectHighlight = wx.Rect()

        # the checkbox/radiobutton rect (if any)
        self._rectCheck = wx.Rect()

    # extend all our rects to be centered inside the one of given width
    def ExtendWidth(self, w):

        if self._rectAll.width > w:
            raise Exception("width can only be increased")

        self._rectAll.width = w
        self._rectLabel.x = self._rectAll.x + (w - self._rectLabel.width)/2
        self._rectIcon.x = self._rectAll.x + (w - self._rectIcon.width)/2
        self._rectHighlight.x = self._rectAll.x + (w - self._rectHighlight.width)/2


#-----------------------------------------------------------------------------
#  UltimateListLineData (internal)
#-----------------------------------------------------------------------------

class UltimateListLineData(object):

    def __init__(self, owner):

        # the list of subitems: only may have more than one item in report mode
        self._items = []


        # is this item selected? [NB: not used in virtual mode]
        self._highlighted = False

        # back pointer to the list ctrl
        self._owner = owner
        self._height = self._width = self._x = self._y = -1

        if self.InReportView():

            self._gi = None

        else:

            self._gi = GeometryInfo()

        if self.GetMode() in [ULC_REPORT, ULC_TILE] or self.HasExtraMode(ULC_HEADER_IN_ALL_VIEWS):
            self.InitItems(self._owner.GetColumnCount())
        else:
            self.InitItems(1)


    def GetHeight(self):

        return self._height


    def SetHeight(self, height):

        self._height = height


    def GetWidth(self):

        return self._width


    def SetWidth(self, width):

        self._width = width


    def GetX(self):

        return self._x


    def SetX(self, x):

        self._x = x


    def GetY(self):

        return self._y


    def SetY(self, y):

        self._y = y


    def ResetDimensions(self):

        self._height = self._width = self._x = self._y = -1


    def HasImage(self):

        return self.GetImage() != []


    def HasText(self):

        return self.GetText(0) != ""


    def IsHighlighted(self):

        if self.IsVirtual():
            raise Exception("unexpected call to IsHighlighted")

        return self._highlighted


    def GetMode(self):

        return self._owner.GetListCtrl().GetWindowStyleFlag() & ULC_MASK_TYPE


    def HasExtraMode(self, mode):

        return self._owner.GetListCtrl().HasExtraFlag(mode)


    def InReportView(self):

        return self._owner.HasFlag(ULC_REPORT)


    def IsVirtual(self):

        return self._owner.IsVirtual()


    def CalculateSize(self, dc, spacing):

        item = self._items[0]
        mode = self.GetMode()

        if mode in [ULC_ICON, ULC_SMALL_ICON]:

            self._gi._rectAll.width = spacing

            s = item.GetText()

            if not s:

                lh = -1
                self._gi._rectLabel.width = 0
                self._gi._rectLabel.height = 0

            else:

                lw, lh = dc.GetTextExtent(s)
                lw += EXTRA_WIDTH
                lh += EXTRA_HEIGHT

                self._gi._rectAll.height = spacing + lh

                if lw > spacing:
                    self._gi._rectAll.width = lw

                self._gi._rectLabel.width = lw
                self._gi._rectLabel.height = lh

            if item.HasImage():

                w, h = self._owner.GetImageSize(item.GetImage())
                self._gi._rectIcon.width = w + 8
                self._gi._rectIcon.height = h + 8

                if self._gi._rectIcon.width > self._gi._rectAll.width:
                    self._gi._rectAll.width = self._gi._rectIcon.width
                if self._gi._rectIcon.height + lh > self._gi._rectAll.height - 4:
                    self._gi._rectAll.height = self._gi._rectIcon.height + lh + 4

            if item.HasText():

                self._gi._rectHighlight.width = self._gi._rectLabel.width
                self._gi._rectHighlight.height = self._gi._rectLabel.height

            else:

                self._gi._rectHighlight.width = self._gi._rectIcon.width
                self._gi._rectHighlight.height = self._gi._rectIcon.height

        elif mode == ULC_LIST:

            s = item.GetTextForMeasuring()

            lw, lh = dc.GetTextExtent(s)
            lw += EXTRA_WIDTH
            lh += EXTRA_HEIGHT

            self._gi._rectLabel.width = lw
            self._gi._rectLabel.height = lh

            self._gi._rectAll.width = lw
            self._gi._rectAll.height = lh

            if item.HasImage():

                w, h = self._owner.GetImageSize(item.GetImage())
                h += 4
                self._gi._rectIcon.width = w
                self._gi._rectIcon.height = h

                self._gi._rectAll.width += 4 + w

                if h > self._gi._rectAll.height:
                    self._gi._rectAll.height = h

            if item.GetKind() in [1, 2]:

                w, h = self._owner.GetCheckboxImageSize()
                h += 4
                self._gi._rectCheck.width = w
                self._gi._rectCheck.height = h

                self._gi._rectAll.width += 4 + w

                if h > self._gi._rectAll.height:
                    self._gi._rectAll.height = h

            self._gi._rectHighlight.width = self._gi._rectAll.width
            self._gi._rectHighlight.height = self._gi._rectAll.height

        elif mode == ULC_REPORT:
            raise Exception("unexpected call to SetSize")

        else:
            raise Exception("unknown mode")


    def SetPosition(self, x, y, spacing):

        item = self._items[0]
        mode = self.GetMode()

        if mode in [ULC_ICON, ULC_SMALL_ICON]:

            self._gi._rectAll.x = x
            self._gi._rectAll.y = y

            if item.HasImage():

                self._gi._rectIcon.x = self._gi._rectAll.x + 4 + (self._gi._rectAll.width - self._gi._rectIcon.width)/2
                self._gi._rectIcon.y = self._gi._rectAll.y + 4

            if item.HasText():

                if self._gi._rectAll.width > spacing:
                    self._gi._rectLabel.x = self._gi._rectAll.x + 2
                else:
                    self._gi._rectLabel.x = self._gi._rectAll.x + 2 + (spacing/2) - (self._gi._rectLabel.width/2)

                self._gi._rectLabel.y = self._gi._rectAll.y + self._gi._rectAll.height + 2 - self._gi._rectLabel.height
                self._gi._rectHighlight.x = self._gi._rectLabel.x - 2
                self._gi._rectHighlight.y = self._gi._rectLabel.y - 2

            else:

                self._gi._rectHighlight.x = self._gi._rectIcon.x - 4
                self._gi._rectHighlight.y = self._gi._rectIcon.y - 4

        elif mode == ULC_LIST:

            self._gi._rectAll.x = x
            self._gi._rectAll.y = y

            wcheck = hcheck = 0

            if item.GetKind() in [1, 2]:
                wcheck, hcheck = self._owner.GetCheckboxImageSize()
                wcheck += 2
                self._gi._rectCheck.x = self._gi._rectAll.x + 2
                self._gi._rectCheck.y = self._gi._rectAll.y + 2

            self._gi._rectHighlight.x = self._gi._rectAll.x
            self._gi._rectHighlight.y = self._gi._rectAll.y
            self._gi._rectLabel.y = self._gi._rectAll.y + 2

            if item.HasImage():

                self._gi._rectIcon.x = self._gi._rectAll.x + wcheck + 2
                self._gi._rectIcon.y = self._gi._rectAll.y + 2
                self._gi._rectLabel.x = self._gi._rectAll.x + 6 + self._gi._rectIcon.width + wcheck

            else:

                self._gi._rectLabel.x = self._gi._rectAll.x + 2 + wcheck

        elif mode == ULC_REPORT:
            raise Exception("unexpected call to SetPosition")

        else:
            raise Exception("unknown mode")


    def InitItems(self, num):

        for i in xrange(num):
            self._items.append(UltimateListItemData(self._owner))


    def SetItem(self, index, info):

        item = self._items[index]
        item.SetItem(info)


    def GetItem(self, index, info):

        item = self._items[index]
        return item.GetItem(info)


    def GetText(self, index):

        item = self._items[index]
        return item.GetText()


    def SetText(self, index, s):

        item = self._items[index]
        item.SetText(s)


    def SetImage(self, index, image):

        item = self._items[index]
        item.SetImage(image)


    def GetImage(self, index=0):

        item = self._items[index]
        return item.GetImage()


    def Check(self, index, checked=True):

        item = self._items[index]
        item.Check(checked)


    def SetKind(self, index, kind=0):

        item = self._items[index]
        item.SetKind(kind)


    def GetKind(self, index=0):

        item = self._items[index]
        return item.GetKind()


    def IsChecked(self, index):

        item = self._items[index]
        return item.IsChecked()


    def SetColour(self, index, c):

        item = self._items[index]
        item.SetColour(c)


    def GetAttr(self):

        item = self._items[0]
        return item.GetAttr()


    def SetAttr(self, attr):

        item = self._items[0]
        item.SetAttr(attr)


    def SetAttributes(self, dc, attr, highlighted):

        listctrl = self._owner.GetParent()

        # fg colour
        # don't use foreground colour for drawing highlighted items - this might
        # make them completely invisible (and there is no way to do bit
        # arithmetics on wxColour, unfortunately)

        if not self._owner.HasExtraFlag(ULC_BORDER_SELECT) and not self._owner.HasExtraFlag(ULC_NO_FULL_ROW_SELECT):
            if highlighted:
                if wx.Platform == "__WXMAC__":
                    if self._owner.HasFocus():
                        colText = wx.WHITE
                    else:
                        colText = wx.BLACK
                else:
                    colText = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT)
            else:
                colText = listctrl.GetForegroundColour()
        elif attr and attr.HasTextColour():
            colText = attr.GetTextColour()
        else:
            colText = listctrl.GetForegroundColour()

        dc.SetTextForeground(colText)

        # font
        if attr and attr.HasFont():
            font = attr.GetFont()
        else:
            font = listctrl.GetFont()

        dc.SetFont(font)

        # bg colour
        hasBgCol = attr and attr.HasBackgroundColour()

        if highlighted or hasBgCol:
            if highlighted:
                dc.SetBrush(self._owner.GetHighlightBrush())
            else:
                dc.SetBrush(wx.Brush(attr.GetBackgroundColour(), wx.SOLID))

            dc.SetPen(wx.TRANSPARENT_PEN)

            return True

        return False


    def Draw(self, line, dc):

        item = self._items[0]
        highlighted = self.IsHighlighted()

        attr = self.GetAttr()

        useGradient, gradientStyle = self._owner._usegradients, self._owner._gradientstyle
        useVista = self._owner._vistaselection
        hasFocus = self._owner._hasFocus
        borderOnly = self._owner.HasExtraFlag(ULC_BORDER_SELECT)
        drawn = False

        if self.SetAttributes(dc, attr, highlighted):
            drawn = True

            if not borderOnly:

                if useGradient:
                    if gradientStyle == 0:
                        # horizontal gradient
                        self.DrawHorizontalGradient(dc, self._gi._rectAll, hasFocus)
                    else:
                        # vertical gradient
                        self.DrawVerticalGradient(dc, self._gi._rectAll, hasFocus)
                elif useVista:
                    # Vista selection style
                    self.DrawVistaRectangle(dc, self._gi._rectAll, hasFocus)
                else:
                    if wx.Platform not in ["__WXMAC__", "__WXGTK__"]:
                        dc.DrawRectangleRect(self._gi._rectHighlight)
                    else:
                        if highlighted:
                            flags = wx.CONTROL_SELECTED
                            if self._owner.HasFocus() and wx.Platform == "__WXMAC__":
                                flags |= wx.CONTROL_FOCUSED

                            wx.RendererNative.Get().DrawItemSelectionRect(self._owner, dc, self._gi._rectHighlight, flags)
                        else:
                            dc.DrawRectangleRect(self._gi._rectHighlight)

        else:

            if borderOnly:
                dc.SetBrush(wx.WHITE_BRUSH)
                dc.SetPen(wx.TRANSPARENT_PEN)
                dc.DrawRectangleRect(self._gi._rectAll)

        if item.GetKind() in [1, 2]:
            rectCheck = self._gi._rectCheck
            self._owner.DrawCheckbox(dc, rectCheck.x, rectCheck.y, item.GetKind(), item.IsChecked(), item.IsEnabled())

        if item.HasImage():
            # centre the image inside our rectangle, this looks nicer when items
            # ae aligned in a row
            rectIcon = self._gi._rectIcon
            self._owner.DrawImage(item.GetImage()[0], dc, rectIcon.x, rectIcon.y, True)

        if item.HasText():
            rectLabel = self._gi._rectLabel

            dc.SetClippingRect(rectLabel)
            dc.DrawText(item.GetText(), rectLabel.x, rectLabel.y)
            dc.DestroyClippingRegion()

        if self._owner.HasExtraFlag(ULC_HOT_TRACKING):
            if line == self._owner._newHotCurrent and not drawn:
                r = wx.Rect(*self._gi._rectAll)
                dc.SetBrush(wx.TRANSPARENT_BRUSH)
                dc.SetPen(wx.Pen(wx.NamedColor("orange")))
                dc.DrawRoundedRectangleRect(r, 3)

        if borderOnly and drawn:
            dc.SetPen(wx.Pen(wx.Colour(0, 191, 255), 2))
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            r = wx.Rect(*self._gi._rectAll)
            r.x += 1
            r.y += 1
            r.width -= 1
            r.height -= 1
            dc.DrawRoundedRectangleRect(r, 4)


    def HideItemWindow(self, item):

        wnd = item.GetWindow()
        if wnd and wnd.IsShown():
            wnd.Hide()


    def DrawInReportMode(self, dc, line, rect, rectHL, highlighted, current, enabled, oldPN, oldBR):

        attr = self.GetAttr()

        useGradient, gradientStyle = self._owner._usegradients, self._owner._gradientstyle
        useVista = self._owner._vistaselection
        hasFocus = self._owner._hasFocus
        borderOnly = self._owner.HasExtraFlag(ULC_BORDER_SELECT)
        nofullRow = self._owner.HasExtraFlag(ULC_NO_FULL_ROW_SELECT)

        drawn = False
        dc.SetBrush(wx.TRANSPARENT_BRUSH)

        if nofullRow:

            x = rect.x + HEADER_OFFSET_X
            y = rect.y
            height = rect.height

            for col, item in enumerate(self._items):

                width = self._owner.GetColumnWidth(col)
                if self._owner.IsColumnShown(col):
                    paintRect = wx.Rect(x, y, self._owner.GetColumnWidth(col)-2*HEADER_OFFSET_X, rect.height)
                    break

                xOld = x
                x += width

        else:

            paintRect = wx.Rect(*rectHL)

        if self.SetAttributes(dc, attr, highlighted) and enabled:

            drawn = True

            if not borderOnly:

                if useGradient:
                    if gradientStyle == 0:
                        # horizontal gradient
                        self.DrawHorizontalGradient(dc, paintRect, hasFocus)
                    else:
                        # vertical gradient
                        self.DrawVerticalGradient(dc, paintRect, hasFocus)
                elif useVista:
                    # Vista selection style
                    self.DrawVistaRectangle(dc, paintRect, hasFocus)
                else:
                    # Normal selection style
                    if wx.Platform not in ["__WXGTK__", "__WXMAC__"]:
                        dc.DrawRectangleRect(paintRect)
                    else:
                        if highlighted:
                            flags = wx.CONTROL_SELECTED
                            if hasFocus:
                                flags |= wx.CONTROL_FOCUSED
                            if current:
                                flags |= wx.CONTROL_CURRENT

                            wx.RendererNative.Get().DrawItemSelectionRect(self._owner, dc, paintRect, flags)
                        else:
                            dc.DrawRectangleRect(paintRect)

        else:

            if borderOnly:

                dc.SetBrush(wx.WHITE_BRUSH)
                dc.SetPen(wx.TRANSPARENT_PEN)
                dc.DrawRectangleRect(paintRect)

        x = rect.x + HEADER_OFFSET_X
        y = rect.y
        height = rect.height

        for col, item in enumerate(self._items):

            if not self._owner.IsColumnShown(col):
                self.HideItemWindow(item)
                continue

            width = self._owner.GetColumnWidth(col)
            xOld = x
            x += width

            if item.GetCustomRenderer():
                customRect = wx.Rect(xOld-HEADER_OFFSET_X, rect.y, width, rect.height)
                item.GetCustomRenderer().DrawSubItem(dc, customRect, line, highlighted, enabled)
                continue

            overflow = item.GetOverFlow() and item.HasText()

            if item.GetKind() in [1, 2]:

                # We got a checkbox-type item
                ix, iy = self._owner.GetCheckboxImageSize()
                checked = item.IsChecked()
                self._owner.DrawCheckbox(dc, xOld, y + (height-iy+1)/2, item.GetKind(), checked, enabled)
                xOld += ix
                width -= ix

            if item.HasImage():

                images = item.GetImage()

                for img in images:

                    ix, iy = self._owner.GetImageSize([img])
                    self._owner.DrawImage(img, dc, xOld, y + (height-iy)/2, enabled)

                    xOld += ix
                    width -= ix

##                if images:
##                    width -= IMAGE_MARGIN_IN_REPORT_MODE - MARGIN_BETWEEN_TEXT_AND_ICON

            wnd = item.GetWindow()
            xSize = 0
            if wnd:
                xSize, ySize = item.GetWindowSize()
                wndx = xOld - HEADER_OFFSET_X + width - xSize - 3
                xa, ya = self._owner.CalcScrolledPosition((0, rect.y))
                wndx += xa
                if rect.height > ySize:
                    ya += (rect.height - ySize)/2

            itemRect = wx.Rect(xOld-2*HEADER_OFFSET_X, rect.y, width-xSize-HEADER_OFFSET_X, rect.height)
            if overflow:
                itemRect = wx.Rect(xOld-2*HEADER_OFFSET_X, rect.y, rectHL.width-xSize-HEADER_OFFSET_X, rect.height)

            dc.SetClippingRect(itemRect)

            if item.HasBackgroundColour():
                dc.SetBrush(wx.Brush(item.GetBackgroundColour()))
                dc.SetPen(wx.Pen(item.GetBackgroundColour()))
                dc.DrawRectangleRect(itemRect)
                dc.SetBrush(oldBR)
                dc.SetPen(oldPN)

            if item.HasText():

                coloured = item.HasColour()
                oldDC = dc.GetTextForeground()
                oldFT = dc.GetFont()

                font = item.HasFont()

                if not enabled:
                    dc.SetTextForeground(self._owner.GetDisabledTextColour())
                else:
                    if coloured:
                        dc.SetTextForeground(item.GetColour())

                if item.IsHyperText():
                    dc.SetFont(self._owner.GetHyperTextFont())
                    if item.GetVisited():
                        dc.SetTextForeground(self._owner.GetHyperTextVisitedColour())
                    else:
                        dc.SetTextForeground(self._owner.GetHyperTextNewColour())
                else:
                    if font:
                        dc.SetFont(item.GetFont())

                itemRect = wx.Rect(itemRect.x+MARGIN_BETWEEN_TEXT_AND_ICON, itemRect.y, itemRect.width-8, itemRect.height)
                self.DrawTextFormatted(dc, item.GetText(), line, col, itemRect, overflow)

                if coloured:
                    dc.SetTextForeground(oldDC)

                if font:
                    dc.SetFont(oldFT)

            dc.DestroyClippingRegion()

            if wnd:
                if not wnd.IsShown():
                    wnd.Show()

                if item._expandWin:
                    if wnd.GetRect() != itemRect:
                        wRect = wx.Rect(*itemRect)
                        wRect.x += 2
                        wRect.width = width - 8
                        wRect.y += 2
                        wRect.height -= 4
                        wnd.SetRect(wRect)
                else:
                    if wnd.GetPosition() != (wndx, ya):
                        wnd.SetPosition((wndx, ya))

        if self._owner.HasExtraFlag(ULC_HOT_TRACKING):
            if line == self._owner._newHotCurrent and not drawn:
                r = wx.Rect(*paintRect)
                r.y += 1
                r.height -= 1
                dc.SetBrush(wx.TRANSPARENT_BRUSH)
                dc.SetPen(wx.Pen(wx.NamedColor("orange")))
                dc.DrawRoundedRectangleRect(r, 3)
                dc.SetPen(oldPN)

        if borderOnly and drawn:
            dc.SetPen(wx.Pen(wx.Colour(0, 191, 255), 2))
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            rect = wx.Rect(*paintRect)
            rect.y += 1
            rect.height -= 1
            dc.DrawRoundedRectangleRect(rect, 3)
            dc.SetPen(oldPN)


    def DrawTextFormatted(self, dc, text, row, col, itemRect, overflow):

        # determine if the string can fit inside the current width
        w, h, dummy = dc.GetMultiLineTextExtent(text)
        width = itemRect.width

        shortItems = self._owner._shortItems
        tuples = (row, col)

        # it can, draw it using the items alignment
        item = self._owner.GetColumn(col)
        align = item.GetAlign()

        if align == ULC_FORMAT_RIGHT:
            textAlign = wx.ALIGN_RIGHT
        elif align == ULC_FORMAT_CENTER:
            textAlign = wx.ALIGN_CENTER
        else:
            textAlign = wx.ALIGN_LEFT

        if w <= width:

            if tuples in shortItems:
                shortItems.remove(tuples)

            dc.DrawLabel(text, itemRect, textAlign|wx.ALIGN_CENTER_VERTICAL)

        else: # otherwise, truncate and add an ellipsis if possible

            if tuples not in shortItems:
                shortItems.append(tuples)

            # determine the base width
            ellipsis = "..."
            base_w, h = dc.GetTextExtent(ellipsis)

            # continue until we have enough space or only one character left

            newText = text.split("\n")
            theText = ""

            for text in newText:

                lenText = len(text)
                drawntext = text
                w, dummy = dc.GetTextExtent(text)

                while lenText > 1:

                    if w + base_w <= width:
                        break

                    w_c, h_c = dc.GetTextExtent(drawntext[-1])
                    drawntext = drawntext[0:-1]
                    lenText -= 1
                    w -= w_c

                # if still not enough space, remove ellipsis characters
                while len(ellipsis) > 0 and w + base_w > width:
                    ellipsis = ellipsis[0:-1]
                    base_w, h = dc.GetTextExtent(ellipsis)

                theText += drawntext + ellipsis + "\n"

            theText = theText.rstrip()
            # now draw the text
            dc.DrawLabel(theText, itemRect, textAlign|wx.ALIGN_CENTER_VERTICAL)


    def DrawVerticalGradient(self, dc, rect, hasfocus):
        """Gradient fill from colour 1 to colour 2 from top to bottom."""

        oldpen = dc.GetPen()
        oldbrush = dc.GetBrush()
        dc.SetPen(wx.TRANSPARENT_PEN)

        # calculate gradient coefficients
        if hasfocus:
            col2 = self._owner._secondcolour
            col1 = self._owner._firstcolour
        else:
            col2 = self._owner._highlightUnfocusedBrush.GetColour()
            col1 = self._owner._highlightUnfocusedBrush2.GetColour()

        r1, g1, b1 = int(col1.Red()), int(col1.Green()), int(col1.Blue())
        r2, g2, b2 = int(col2.Red()), int(col2.Green()), int(col2.Blue())

        flrect = float(rect.height)

        rstep = float((r2 - r1)) / flrect
        gstep = float((g2 - g1)) / flrect
        bstep = float((b2 - b1)) / flrect

        rf, gf, bf = 0, 0, 0

        for y in xrange(rect.y, rect.y + rect.height):
            currCol = (r1 + rf, g1 + gf, b1 + bf)
            dc.SetBrush(wx.Brush(currCol, wx.SOLID))
            dc.DrawRectangle(rect.x, y, rect.width, 1)
            rf = rf + rstep
            gf = gf + gstep
            bf = bf + bstep

        dc.SetPen(oldpen)
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawRectangleRect(rect)
        dc.SetBrush(oldbrush)


    def DrawHorizontalGradient(self, dc, rect, hasfocus):
        """Gradient fill from colour 1 to colour 2 from left to right."""

        oldpen = dc.GetPen()
        oldbrush = dc.GetBrush()
        dc.SetPen(wx.TRANSPARENT_PEN)

        # calculate gradient coefficients

        if hasfocus:
            col2 = self._owner._secondcolour
            col1 = self._owner._firstcolour
        else:
            col2 = self._owner._highlightUnfocusedBrush.GetColour()
            col1 = self._owner._highlightUnfocusedBrush2.GetColour()

        r1, g1, b1 = int(col1.Red()), int(col1.Green()), int(col1.Blue())
        r2, g2, b2 = int(col2.Red()), int(col2.Green()), int(col2.Blue())

        flrect = float(rect.width)

        rstep = float((r2 - r1)) / flrect
        gstep = float((g2 - g1)) / flrect
        bstep = float((b2 - b1)) / flrect

        rf, gf, bf = 0, 0, 0

        for x in xrange(rect.x, rect.x + rect.width):
            currCol = (int(r1 + rf), int(g1 + gf), int(b1 + bf))
            dc.SetBrush(wx.Brush(currCol, wx.SOLID))
            dc.DrawRectangle(x, rect.y, 1, rect.height)
            rf = rf + rstep
            gf = gf + gstep
            bf = bf + bstep

        dc.SetPen(oldpen)
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawRectangleRect(rect)
        dc.SetBrush(oldbrush)


    def DrawVistaRectangle(self, dc, rect, hasfocus):
        """Draw the selected item(s) with the Windows Vista style."""

        if hasfocus:

            outer = _rgbSelectOuter
            inner = _rgbSelectInner
            top = _rgbSelectTop
            bottom = _rgbSelectBottom

        else:

            outer = _rgbNoFocusOuter
            inner = _rgbNoFocusInner
            top = _rgbNoFocusTop
            bottom = _rgbNoFocusBottom

        oldpen = dc.GetPen()
        oldbrush = dc.GetBrush()

        bdrRect = wx.Rect(*rect.Get())
        filRect = wx.Rect(*rect.Get())
        filRect.Deflate(1,1)

        r1, g1, b1 = int(top.Red()), int(top.Green()), int(top.Blue())
        r2, g2, b2 = int(bottom.Red()), int(bottom.Green()), int(bottom.Blue())

        flrect = float(filRect.height)
        if flrect < 1:
            flrect = self._owner._lineHeight

        rstep = float((r2 - r1)) / flrect
        gstep = float((g2 - g1)) / flrect
        bstep = float((b2 - b1)) / flrect

        rf, gf, bf = 0, 0, 0
        dc.SetPen(wx.TRANSPARENT_PEN)

        for y in xrange(filRect.y, filRect.y + filRect.height):
            currCol = (r1 + rf, g1 + gf, b1 + bf)
            dc.SetBrush(wx.Brush(currCol, wx.SOLID))
            dc.DrawRectangle(filRect.x, y, filRect.width, 1)
            rf = rf + rstep
            gf = gf + gstep
            bf = bf + bstep

        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.SetPen(wx.Pen(outer))
        dc.DrawRoundedRectangleRect(bdrRect, 3)
        bdrRect.Deflate(1, 1)
        dc.SetPen(wx.Pen(inner))
        dc.DrawRoundedRectangleRect(bdrRect, 2)

        dc.SetPen(oldpen)
        dc.SetBrush(oldbrush)


    def Highlight(self, on):

        if on == self._highlighted:
            return False

        self._highlighted = on

        return True


    def ReverseHighlight(self):

        self.Highlight(not self.IsHighlighted())



#-----------------------------------------------------------------------------
#  UltimateListHeaderWindow (internal)
#-----------------------------------------------------------------------------

class UltimateListHeaderWindow(wx.PyControl):

    def __init__(self, win, id, owner, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0, validator=wx.DefaultValidator,
                 name="UltimateListCtrlcolumntitles", isFooter=False):

        wx.PyControl.__init__(self, win, id, pos, size, style|wx.NO_BORDER, validator, name)

        self._isFooter = isFooter
        self._owner = owner
        self._currentCursor = wx.NullCursor
        self._resizeCursor = wx.StockCursor(wx.CURSOR_SIZEWE)
        self._isDragging = False

        # column being resized or -1
        self._column = -1

        # divider line position in logical (unscrolled) coords
        self._currentX = 0

        # minimal position beyond which the divider line can't be dragged in
        # logical coords
        self._minX = 0

        # needs refresh
        self._dirty = False
        self._hasFont = False
        self._sendSetColumnWidth = False
        self._colToSend = -1
        self._widthToSend = 0
        self._leftDown = False
        self._enter = False
        self._currentColumn = -1

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda e: None)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouse)
        self.Bind(wx.EVT_SET_FOCUS, self.OnSetFocus)
        self.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

        if _USE_VISATTR:

            attr = wx.Panel.GetClassDefaultAttributes()
            self.SetOwnForegroundColour(attr.colFg)
            self.SetOwnBackgroundColour(attr.colBg)
            if not self._hasFont:
                self.SetOwnFont(attr.font)

        else:

            self.SetOwnForegroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT))
            self.SetOwnBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE))

            if not self._hasFont:
                self.SetOwnFont(wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT))


    def DoGetBestSize(self):

        w, h, d, dummy = self.GetFullTextExtent("Hg")
        maxH = self.GetTextHeight()
        nativeH = wx.RendererNative.Get().GetHeaderButtonHeight(self.GetParent())

        if not self._isFooter:
            maxH = max(max(h, maxH), nativeH)
            maxH += d
            self.GetParent()._headerHeight = maxH
        else:
            maxH = max(h, nativeH)
            maxH += d
            self.GetParent()._footerHeight = maxH

        return wx.Size(200, maxH)


    def IsColumnShown(self, column):

        if column < 0 or column >= self._owner.GetColumnCount():
            raise Exception("Invalid column")

        return self._owner.IsColumnShown(column)


    # shift the DC origin to match the position of the main window horz
    # scrollbar: this allows us to always use logical coords
    def AdjustDC(self, dc):

        xpix, dummy = self._owner.GetScrollPixelsPerUnit()
        x, dummy = self._owner.GetViewStart()

        # account for the horz scrollbar offset
        dc.SetDeviceOrigin(-x*xpix, 0)


    def GetTextHeight(self):

        maxH = 0
        numColumns = self._owner.GetColumnCount()
        dc = wx.ClientDC(self)
        for i in xrange(numColumns):

            if not self.IsColumnShown(i):
                continue

            item = self._owner.GetColumn(i)
            if item.GetFont().IsOk():
                dc.SetFont(item.GetFont())
            else:
                dc.SetFont(self.GetFont())

            wLabel, hLabel, dummy = dc.GetMultiLineTextExtent(item.GetText())
            maxH = max(maxH, hLabel)

        return maxH


    def OnPaint(self, event):

        dc = wx.BufferedPaintDC(self)
        # width and height of the entire header window
        w, h = self.GetClientSize()
        w, dummy = self._owner.CalcUnscrolledPosition(w, 0)
        dc.SetBrush(wx.Brush(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE)))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangle(0, -1, w, h+2)

        #self.PrepareDC(dc)
        self.AdjustDC(dc)

        dc.SetBackgroundMode(wx.TRANSPARENT)
        dc.SetTextForeground(self.GetForegroundColour())

        x = HEADER_OFFSET_X

        numColumns = self._owner.GetColumnCount()
        item = UltimateListItem()
        renderer = wx.RendererNative.Get()
        enabled = self.GetParent().IsEnabled()
        virtual = self._owner.IsVirtual()
        isFooter = self._isFooter

        for i in xrange(numColumns):

            if x >= w:
                break

            if not self.IsColumnShown(i):
                continue # do next column if not shown

            item = self._owner.GetColumn(i)
            wCol = item._width

            cw = wCol
            ch = h

            flags = 0
            if not enabled:
                flags |= wx.CONTROL_DISABLED

            # NB: The code below is not really Mac-specific, but since we are close
            # to 2.8 release and I don't have time to test on other platforms, I
            # defined this only for wxMac. If this behavior is desired on
            # other platforms, please go ahead and revise or remove the #ifdef.

            if "__WXMAC__" in wx.PlatformInfo:
                if not virtual and item._mask & ULC_MASK_STATE and item._state & ULC_STATE_SELECTED:
                    flags |= wx.CONTROL_SELECTED

            if i == 0:
               flags |= wx.CONTROL_SPECIAL # mark as first column

            if i == self._currentColumn:
                if self._leftDown:
                    flags |= wx.CONTROL_PRESSED
                else:
                    if self._enter:
                        flags |= wx.CONTROL_CURRENT

            # the width of the rect to draw: make it smaller to fit entirely
            # inside the column rect

            renderer.DrawHeaderButton(self, dc,
                                      wx.Rect(x-1, HEADER_OFFSET_Y-1, cw-1, ch),
                                      flags)

            # see if we have enough space for the column label
            if isFooter:
                if item.GetFooterFont().IsOk():
                    dc.SetFont(item.GetFooterFont())
                else:
                    dc.SetFont(self.GetFont())
            else:
                if item.GetFont().IsOk():
                    dc.SetFont(item.GetFont())
                else:
                    dc.SetFont(self.GetFont())

            wcheck = hcheck = 0
            kind = (isFooter and [item.GetFooterKind()] or [item.GetKind()])[0]
            checked = (isFooter and [item.IsFooterChecked()] or [item.IsChecked()])[0]

            if kind in [1, 2]:
                # We got a checkbox-type item
                ix, iy = self._owner.GetCheckboxImageSize()
                # We draw it on the left, always
                self._owner.DrawCheckbox(dc, x + HEADER_OFFSET_X, HEADER_OFFSET_Y + (h - 4 - iy)/2, kind, checked, enabled)
                wcheck += ix + HEADER_IMAGE_MARGIN_IN_REPORT_MODE
                cw -= ix + HEADER_IMAGE_MARGIN_IN_REPORT_MODE

            # for this we need the width of the text
            text = (isFooter and [item.GetFooterText()] or [item.GetText()])[0]
            wLabel, hLabel, dummy = dc.GetMultiLineTextExtent(text)
            wLabel += 2*EXTRA_WIDTH

            # and the width of the icon, if any
            image = (isFooter and [item._footerImage] or [item._image])[0]

            if image:
                imageList = self._owner._small_image_list
                if imageList:
                    for img in image:
                        ix, iy = imageList.GetSize(img)
                        wLabel += ix + HEADER_IMAGE_MARGIN_IN_REPORT_MODE

            else:

                imageList = None

            # ignore alignment if there is not enough space anyhow
            align = (isFooter and [item.GetFooterAlign()] or [item.GetAlign()])[0]
            align = (wLabel < cw and [align] or [ULC_FORMAT_LEFT])[0]

            if align == ULC_FORMAT_LEFT:
                xAligned = x + wcheck

            elif align == ULC_FORMAT_RIGHT:
                xAligned = x + cw - wLabel - HEADER_OFFSET_X

            elif align == ULC_FORMAT_CENTER:
                xAligned = x + wcheck + (cw - wLabel)/2

            # if we have an image, draw it on the right of the label
            if imageList:
                for indx, img in enumerate(image):
                    imageList.Draw(img, dc,
                                   xAligned + wLabel - (ix + HEADER_IMAGE_MARGIN_IN_REPORT_MODE)*(indx+1),
                                   HEADER_OFFSET_Y + (h - 4 - iy)/2,
                                   wx.IMAGELIST_DRAW_TRANSPARENT)

                    cw -= ix + HEADER_IMAGE_MARGIN_IN_REPORT_MODE

            # draw the text clipping it so that it doesn't overwrite the column
            # boundary
            dc.SetClippingRegion(x, HEADER_OFFSET_Y, cw, h - 4)
            self.DrawTextFormatted(dc, text, wx.Rect(xAligned+EXTRA_WIDTH, HEADER_OFFSET_Y, cw-EXTRA_WIDTH, h-4))

            x += wCol
            dc.DestroyClippingRegion()

        # Fill in what's missing to the right of the columns, otherwise we will
        # leave an unpainted area when columns are removed (and it looks better)
        if x < w:
            renderer.DrawHeaderButton(self, dc, wx.Rect(x, HEADER_OFFSET_Y, w - x, h), wx.CONTROL_DIRTY) # mark as last column


    def DrawTextFormatted(self, dc, text, rect):

        # determine if the string can fit inside the current width
        w, h, dummy = dc.GetMultiLineTextExtent(text)
        width = rect.width

        if w <= width:

            dc.DrawLabel(text, rect, wx.ALIGN_CENTER_VERTICAL)

        else:

            # determine the base width
            ellipsis = "..."
            base_w, h = dc.GetTextExtent(ellipsis)

            # continue until we have enough space or only one character left

            newText = text.split("\n")
            theText = ""

            for text in newText:

                lenText = len(text)
                drawntext = text
                w, dummy = dc.GetTextExtent(text)

                while lenText > 1:

                    if w + base_w <= width:
                        break

                    w_c, h_c = dc.GetTextExtent(drawntext[-1])
                    drawntext = drawntext[0:-1]
                    lenText -= 1
                    w -= w_c

                # if still not enough space, remove ellipsis characters
                while len(ellipsis) > 0 and w + base_w > width:
                    ellipsis = ellipsis[0:-1]
                    base_w, h = dc.GetTextExtent(ellipsis)

                theText += drawntext + ellipsis + "\n"

            theText = theText.rstrip()
            dc.DrawLabel(theText, rect, wx.ALIGN_CENTER_VERTICAL)


    def OnInternalIdle(self):

        wx.PyControl.OnInternalIdle(self)

        if self._isFooter:
            return

        if self._sendSetColumnWidth:
            self._owner.SetColumnWidth(self._colToSend, self._widthToSend)
            self._sendSetColumnWidth = False


    def DrawCurrent(self):

        self._sendSetColumnWidth = True
        self._colToSend = self._column
        self._widthToSend = self._currentX - self._minX


    def OnMouse(self, event):

        # we want to work with logical coords
        x, dummy = self._owner.CalcUnscrolledPosition(event.GetX(), 0)
        y = event.GetY()

        columnX, columnY = x, y

        if self._isDragging:

            self.SendListEvent(wxEVT_COMMAND_LIST_COL_DRAGGING, event.GetPosition())

            # we don't draw the line beyond our window, but we allow dragging it
            # there

            w, dummy = self.GetClientSize()
            w, dummy = self._owner.CalcUnscrolledPosition(w, 0)
            w -= 6

            # erase the line if it was drawn
            if self._currentX < w:
                self.DrawCurrent()

            if event.ButtonUp():

                self.ReleaseMouse()
                self._isDragging = False
                self._dirty = True
                self._owner.SetColumnWidth(self._column, self._currentX - self._minX)
                self.SendListEvent(wxEVT_COMMAND_LIST_COL_END_DRAG, event.GetPosition())

            else:

                if x > self._minX + 7:
                    self._currentX = x
                else:
                    self._currentX = self._minX + 7

                # draw in the new location
                if self._currentX < w:
                    self.DrawCurrent()

        else: # not dragging

            self._minX = 0
            hit_border = False

            # end of the current column
            xpos = 0

            # find the column where this event occurred
            countCol = self._owner.GetColumnCount()
            broken = False

            for col in xrange(countCol):

                if not self.IsColumnShown(col):
                    continue

                xpos += self._owner.GetColumnWidth(col)
                self._column = col

                if abs(x-xpos) < 3 and y < 22:
                    # near the column border
                    hit_border = True
                    broken = True
                    break

                if x < xpos:
                    # inside the column
                    broken = True
                    break

                self._minX = xpos

            if not broken:
                self._column = -1

            if event.LeftUp():
                self._leftDown = False
                self.Refresh()

            if event.LeftDown() or event.RightUp():

                if hit_border and event.LeftDown():

                    if not self._isFooter:

                        if self.SendListEvent(wxEVT_COMMAND_LIST_COL_BEGIN_DRAG,
                                              event.GetPosition()):

                            self._isDragging = True
                            self._currentX = x
                            self.CaptureMouse()
                            self.DrawCurrent()

                    #else: column resizing was vetoed by the user code

                else: # click on a column

                     # record the selected state of the columns
                    if event.LeftDown():

                        for i in xrange(self._owner.GetColumnCount()):

                            if not self.IsColumnShown(col):
                                continue

                            colItem = self._owner.GetColumn(i)
                            state = colItem.GetState()

                            if i == self._column:
                                colItem.SetState(state | ULC_STATE_SELECTED)
                                theX = x
                            else:
                                colItem.SetState(state & ~ULC_STATE_SELECTED)

                            self._leftDown = True
                            self._owner.SetColumn(i, colItem)
                            x += self._owner.GetColumnWidth(i)

                        if self.HandleColumnCheck(self._column, event.GetPosition()):
                            return

                    if not self._isFooter:
                        self.SendListEvent((event.LeftDown() and [wxEVT_COMMAND_LIST_COL_CLICK] or \
                                            [wxEVT_COMMAND_LIST_COL_RIGHT_CLICK])[0], event.GetPosition())
                    else:
                        self.SendListEvent((event.LeftDown() and [wxEVT_COMMAND_LIST_FOOTER_CLICK] or \
                                            [wxEVT_COMMAND_LIST_FOOTER_RIGHT_CLICK])[0], event.GetPosition())

                    self._leftDown = True
                    self._currentColumn = self._column

            elif event.Moving():

                setCursor = False

                if not self._isFooter:
                    if hit_border:

                        setCursor = self._currentCursor == wx.STANDARD_CURSOR
                        self._currentCursor = self._resizeCursor

                    else:

                        setCursor = self._currentCursor != wx.STANDARD_CURSOR
                        self._currentCursor = wx.STANDARD_CURSOR

                if setCursor:
                    self.SetCursor(self._currentCursor)
                else:
                    column = self.HitTestColumn(columnX, columnY)
                    self._enter = True
                    self._currentColumn = column
                    self._leftDown = wx.GetMouseState().LeftDown()

                    self.Refresh()

            elif event.ButtonDClick():

                self.HandleColumnCheck(self._column, event.GetPosition())


    def HandleColumnCheck(self, column, pos):

        if column < 0 or column >= self._owner.GetColumnCount():
            return False

        colItem = self._owner.GetColumn(column)
        # Let's see if it is a checkbox-type item

        kind = (self._isFooter and [colItem.GetFooterKind()] or [colItem.GetKind()])[0]
        if kind not in [1, 2]:
            return False

        x = HEADER_OFFSET_X

        for i in xrange(self._owner.GetColumnCount()):

            if not self.IsColumnShown(i):
                continue

            if i == self._column:
                theX = x
                break
            x += self._owner.GetColumnWidth(i)

        parent = self.GetParent()

        w, h = self.GetClientSize()
        ix, iy = self._owner.GetCheckboxImageSize()
        rect = wx.Rect(theX + HEADER_OFFSET_X, HEADER_OFFSET_Y + (h - 4 - iy)/2, ix, iy)

        if rect.Contains(pos):
            # User clicked on the checkbox
            evt = (self._isFooter and [wxEVT_COMMAND_LIST_FOOTER_CHECKING] or [wxEVT_COMMAND_LIST_COL_CHECKING])[0]
            if self.SendListEvent(evt, pos):
                # No veto for the item checking
                if self._isFooter:
                    isChecked = colItem.IsFooterChecked()
                    colItem.CheckFooter(not isChecked)
                else:
                    isChecked = colItem.IsChecked()
                    colItem.Check(not isChecked)

                self._owner.SetColumn(column, colItem)
                evt = (self._isFooter and [wxEVT_COMMAND_LIST_FOOTER_CHECKED] or [wxEVT_COMMAND_LIST_COL_CHECKED])[0]
                self.SendListEvent(evt, pos)
                self.RefreshRect(rect)

                if self._isFooter:
                    return True

                if parent.HasExtraFlag(ULC_AUTO_CHECK_CHILD):
                    self._owner.AutoCheckChild(isChecked, self._column)
                elif parent.HasExtraFlag(ULC_AUTO_TOGGLE_CHILD):
                    self._owner.AutoToggleChild(self._column)

                return True

        return False


    def OnEnterWindow(self, event):

        x, y = self._owner.CalcUnscrolledPosition(*self.ScreenToClient(wx.GetMousePosition()))
        column = self.HitTestColumn(x, y)

        self._leftDown = wx.GetMouseState().LeftDown()
        self._enter = column >= 0 and column < self._owner.GetColumnCount()
        self._currentColumn = column
        self.Refresh()


    def OnLeaveWindow(self, event):

        self._enter = False
        self._leftDown = False

        self._currentColumn = -1
        self.Refresh()


    def HitTestColumn(self, x, y):

        xOld = 0

        for i in xrange(self._owner.GetColumnCount()):
            if not self.IsColumnShown(i):
                continue

            xOld += self._owner.GetColumnWidth(i)
            if x <= xOld:
                return i

        return -1


    def OnSetFocus(self, event):

        self._owner.SetFocusIgnoringChildren()
        self._owner.Update()


    def SendListEvent(self, eventType, pos):

        parent = self.GetParent()
        le = UltimateListEvent(eventType, parent.GetId())
        le.SetEventObject(parent)
        le.m_pointDrag = pos

        # the position should be relative to the parent window, not
        # this one for compatibility with MSW and common sense: the
        # user code doesn't know anything at all about this header
        # window, so why should it get positions relative to it?
        le.m_pointDrag.y -= self.GetSize().y

        le.m_col = self._column
        return (not parent.GetEventHandler().ProcessEvent(le) or le.IsAllowed())


    def GetOwner(self):

        return self._owner



#-----------------------------------------------------------------------------
#  UltimateListRenameTimer (internal)
#-----------------------------------------------------------------------------

class UltimateListRenameTimer(wx.Timer):
    """Timer used for enabling in-place edit."""

    def __init__(self, owner):
        """
        Default class constructor.
        For internal use: do not call it in your code!
        """

        wx.Timer.__init__(self)
        self._owner = owner


    def Notify(self):
        """The timer has expired."""

        self._owner.OnRenameTimer()


#-----------------------------------------------------------------------------
#  UltimateListTextCtrl (internal)
#-----------------------------------------------------------------------------

class UltimateListTextCtrl(ExpandoTextCtrl):

    def __init__(self, owner, itemEdit):

        self._startValue = owner.GetItemText(itemEdit)
        self._currentValue = self._startValue

        self._itemEdited = itemEdit

        self._owner = owner
        self._finished = False
        self._aboutToFinish = False

        rectLabel = owner.GetLineLabelRect(itemEdit)
        rectLabel.x, rectLabel.y = self._owner.CalcScrolledPosition(rectLabel.x, rectLabel.y)
        xSize, ySize = rectLabel.width + 10, rectLabel.height

        expandoStyle = wx.WANTS_CHARS
        if wx.Platform in ["__WXGTK__", "__WXMAC__"]:
            expandoStyle |= wx.SIMPLE_BORDER
        else:
            expandoStyle |= wx.SUNKEN_BORDER

        ExpandoTextCtrl.__init__(self, owner, -1, self._startValue, wx.Point(rectLabel.x, rectLabel.y),
                                 wx.Size(xSize, ySize), expandoStyle)

        self.Bind(wx.EVT_CHAR, self.OnChar)
        self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)


    def AcceptChanges(self):
        """Accepts/refuses the changes made by the user."""

        value = self.GetValue()

        if value == self._startValue:
            # nothing changed, always accept
            # when an item remains unchanged, the owner
            # needs to be notified that the user decided
            # not to change the tree item label, and that
            # the edit has been cancelled
            self._owner.OnRenameCancelled(self._itemEdited)
            return True

        if not self._owner.OnRenameAccept(self._itemEdited, value):
            # vetoed by the user
            return False

        # accepted, do rename the item
        self._owner.SetItemText(self._itemEdited, value)

        if value.count("\n") != self._startValue.count("\n"):
            self._owner.ResetLineDimensions()
            self._owner.Refresh()

        return True


    def Finish(self):
        """Finish editing."""

        try:
            if not self._finished:
                self._finished = True
                self._owner.SetFocusIgnoringChildren()
                self._owner.ResetTextControl()
        except wx.PyDeadObjectError:
            return


    def OnChar(self, event):
        """Handles the wx.EVT_CHAR event for UltimateListTextCtrl."""

        keycode = event.GetKeyCode()
        shiftDown = event.ShiftDown()

        if keycode in [wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER]:
            if shiftDown:
                event.Skip()
            else:
                self._aboutToFinish = True
                self.SetValue(self._currentValue)
                # Notify the owner about the changes
                self.AcceptChanges()
                # Even if vetoed, close the control (consistent with MSW)
                wx.CallAfter(self.Finish)

        elif keycode == wx.WXK_ESCAPE:
            self.StopEditing()

        else:
            event.Skip()


    def OnKeyUp(self, event):
        """Handles the wx.EVT_KEY_UP event for UltimateListTextCtrl."""

        if not self._finished:

            # auto-grow the textctrl:
            parentSize = self._owner.GetSize()
            myPos = self.GetPosition()
            mySize = self.GetSize()

            dc = wx.ClientDC(self)
            sx, sy, dummy = dc.GetMultiLineTextExtent(self.GetValue() + "M")

            if myPos.x + sx > parentSize.x:
                sx = parentSize.x - myPos.x
            if mySize.x > sx:
                sx = mySize.x

            self.SetSize((sx, -1))
            self._currentValue = self.GetValue()

        event.Skip()


    def OnKillFocus(self, event):
        """Handles the wx.EVT_KILL_FOCUS event for UltimateListTextCtrl."""

        if not self._finished and not self._aboutToFinish:

            # We must finish regardless of success, otherwise we'll get
            # focus problems:

            if not self.AcceptChanges():
                self._owner.OnRenameCancelled(self._itemEdited)

        # We must let the native text control handle focus, too, otherwise
        # it could have problems with the cursor (e.g., in wxGTK).
        event.Skip()
        wx.CallAfter(self.Finish)


    def StopEditing(self):
        """Suddenly stops the editing."""

        self._owner.OnRenameCancelled(self._itemEdited)
        self.Finish()


#-----------------------------------------------------------------------------
#  UltimateListMainWindow (internal)
#-----------------------------------------------------------------------------

class UltimateListMainWindow(wx.PyScrolledWindow):

    def __init__(self, parent, id, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0, name="listctrlmainwindow"):

        wx.PyScrolledWindow.__init__(self, parent, id, pos, size, style|wx.HSCROLL|wx.VSCROLL, name)

        # the list of column objects
        self._columns = []

        # the array of all line objects for a non virtual list control (for the
        # virtual list control we only ever use self._lines[0])
        self._lines = []

        # currently focused item or -1
        self._current = -1

        # the number of lines per page
        self._linesPerPage = 0

        # this flag is set when something which should result in the window
        # redrawing happens (i.e. an item was added or deleted, or its appearance
        # changed) and OnPaint() doesn't redraw the window while it is set which
        # allows to minimize the number of repaintings when a lot of items are
        # being added. The real repainting occurs only after the next OnIdle()
        # call
        self._dirty = False
        self._parent = parent
        self.Init()

        self._highlightBrush = wx.Brush(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT), wx.SOLID)

        btnshadow = wx.SystemSettings_GetColour(wx.SYS_COLOUR_BTNSHADOW)
        self._highlightUnfocusedBrush = wx.Brush(btnshadow, wx.SOLID)
        r, g, b = btnshadow.Red(), btnshadow.Green(), btnshadow.Blue()
        backcolour = (max((r >> 1) - 20, 0),
                      max((g >> 1) - 20, 0),
                      max((b >> 1) - 20, 0))
        backcolour = wx.Colour(backcolour[0], backcolour[1], backcolour[2])
        self._highlightUnfocusedBrush2 = wx.Brush(backcolour)

        self.SetScrollbars(0, 0, 0, 0, 0, 0)

        attr = wx.ListCtrl.GetClassDefaultAttributes()
        self.SetOwnForegroundColour(attr.colFg)
        self.SetOwnBackgroundColour(attr.colBg)
        self.SetOwnFont(attr.font)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouse)
        self.Bind(wx.EVT_CHILD_FOCUS, self.OnChildFocus)
        self.Bind(wx.EVT_CHAR, self.OnChar)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.Bind(wx.EVT_SET_FOCUS, self.OnSetFocus)
        self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
        self.Bind(wx.EVT_SCROLLWIN, self.OnScroll)
        self.Bind(wx.EVT_TIMER, self.OnHoverTimer, self._hoverTimer)


    def Init(self):

        self._dirty = True
        self._countVirt = 0
        self._lineFrom = None
        self._lineTo = - 1
        self._linesPerPage = 0

        self._headerWidth = 0
        self._lineHeight = 0

        self._small_image_list = None
        self._normal_image_list = None

        self._small_spacing = 30
        self._normal_spacing = 40

        self._hasFocus = False
        self._dragCount = 0
        self._isCreated = False

        self._lastOnSame = False
        self._renameTimer = UltimateListRenameTimer(self)
        self._textctrl = None

        self._current = -1
        self._lineLastClicked = -1
        self._lineSelectSingleOnUp = -1
        self._lineBeforeLastClicked = -1

        self._dragStart = wx.Point(-1, -1)
        self._aColWidths = []

        self._selStore = SelectionStore()
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

        # Background image settings
        self._backgroundImage = None
        self._imageStretchStyle = _StyleTile

        # Disabled items colour
        self._disabledColour = wx.Colour(180, 180, 180)

        # Gradient selection colours
        self._firstcolour = colour= wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHT)
        self._secondcolour = wx.WHITE
        self._usegradients = False
        self._gradientstyle = 1   # Vertical Gradient

        # Vista Selection Styles
        self._vistaselection = False

        self.SetImageListCheck(16, 16)

        # Disabled items colour
        self._disabledColour = wx.Colour(180, 180, 180)

        # Hyperlinks things
        normalFont = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self._hypertextfont = wx.Font(normalFont.GetPointSize(), normalFont.GetFamily(),
                                      normalFont.GetStyle(), wx.NORMAL, True,
                                      normalFont.GetFaceName(), normalFont.GetEncoding())
        self._hypertextnewcolour = wx.BLUE
        self._hypertextvisitedcolour = wx.Colour(200, 47, 200)
        self._isonhyperlink = False

        self._itemWithWindow = []
        self._hasWindows = False
        self._shortItems = []

        self._isDragging = False
        self._cursor = wx.STANDARD_CURSOR

        image = GetdragcursorImage()

        # since this image didn't come from a .cur file, tell it where the hotspot is
        image.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_X, 1)
        image.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, 1)

        # make the image into a cursor
        self._dragCursor = wx.CursorFromImage(image)
        self._dragItem = None
        self._dropTarget = None

        self._oldHotCurrent = None
        self._newHotCurrent = None

        self._waterMark = None

        self._hoverTimer = wx.Timer(self, wx.ID_ANY)
        self._hoverItem = -1


    def GetMainWindowOfCompositeControl(self):

        return self.GetParent()


    def DoGetBestSize(self):

        return wx.Size(100, 80)


    def HasFlag(self, flag):

        return self._parent.HasFlag(flag)


    def HasExtraFlag(self, flag):

        return self._parent.HasExtraFlag(flag)


    def IsColumnShown(self, column):

        return self.GetColumn(column).IsShown()


    # return True if this is a virtual list control
    def IsVirtual(self):

        return self.HasFlag(ULC_VIRTUAL)


    # return True if the control is in report mode
    def InReportView(self):

        return self.HasFlag(ULC_REPORT)


    def InTileView(self):

        return self.HasFlag(ULC_TILE)

    # return True if we are in single selection mode, False if multi sel
    def IsSingleSel(self):

        return self.HasFlag(ULC_SINGLE_SEL)


    def HasFocus(self):

        return self._hasFocus


    # do we have a header window?
    def HasHeader(self):

        if (self.InReportView() or self.InTileView()) and not self.HasFlag(ULC_NO_HEADER):
            return True
        if self.HasExtraFlag(ULC_HEADER_IN_ALL_VIEWS):
            return True

        return False


    # do we have a footer window?
    def HasFooter(self):

        if self.HasHeader() and self.HasExtraFlag(ULC_FOOTER):
            return True

        return False


    # toggle the line state and refresh it
    def ReverseHighlight(self, line):

        self.HighlightLine(line, not self.IsHighlighted(line))
        self.RefreshLine(line)


    # get the size of the total line rect
    def GetLineSize(self, line):

        return self.GetLineRect(line).GetSize()


    # bring the current item into view
    def MoveToFocus(self):

        self.MoveToItem(self._current)


    def GetColumnCount(self):

        return len(self._columns)


    def GetItemText(self, item):

        info = UltimateListItem()
        info._mask = ULC_MASK_TEXT
        info._itemId = item
        info = self.GetItem(info)

        return info._text


    def SetItemText(self, item, value):

        info = UltimateListItem()
        info._mask = ULC_MASK_TEXT
        info._itemId = item
        info._text = value

        self.SetItem(info)


    def IsEmpty(self):

        return self.GetItemCount() == 0


    def ResetCurrent(self):

        self.ChangeCurrent(-1)


    def HasCurrent(self):

        return self._current != -1


    # override base class virtual to reset self._lineHeight when the font changes
    def SetFont(self, font):

        if not wx.PyScrolledWindow.SetFont(self, font):
            return False

        self._lineHeight = 0
        self.ResetLineDimensions()

        return True


    def ResetLineDimensions(self, force=False):

        if (self.HasFlag(ULC_REPORT) and self.HasExtraFlag(ULC_HAS_VARIABLE_ROW_HEIGHT) and not self.IsVirtual()) or force:
            for l in xrange(self.GetItemCount()):
                line = self.GetLine(l)
                line.ResetDimensions()

    # these are for UltimateListLineData usage only
    # get the backpointer to the list ctrl
    def GetListCtrl(self):

        return self.GetParent()


    # get the brush to use for the item highlighting
    def GetHighlightBrush(self):

        return (self._hasFocus and [self._highlightBrush] or [self._highlightUnfocusedBrush])[0]


    # get the line data for the given index
    def GetLine(self, n):

        if self.IsVirtual():

            self.CacheLineData(n)
            n = 0

        return self._lines[n]


    # force us to recalculate the range of visible lines
    def ResetVisibleLinesRange(self, reset=False):

        self._lineFrom = -1
        if self.IsShownOnScreen() and reset:
            self.ResetLineDimensions()


    # get the colour to be used for drawing the rules
    def GetRuleColour(self):

        return wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DLIGHT)


    def CacheLineData(self, line):

        listctrl = self.GetListCtrl()
        ld = self.GetDummyLine()

        countCol = self.GetColumnCount()
        for col in xrange(countCol):
            ld.SetText(col, listctrl.OnGetItemText(line, col))
            ld.SetImage(col, listctrl.OnGetItemColumnImage(line, col))
            kind = listctrl.OnGetItemColumnKind(line, col)
            ld.SetKind(col, kind)
            if kind > 0:
                ld.Check(col, listctrl.OnGetItemColumnCheck(line, col))

        ld.SetAttr(listctrl.OnGetItemAttr(line))


    def GetDummyLine(self):

        if self.IsEmpty():
            raise Exception("invalid line index")

        if not self.IsVirtual():
            raise Exception("GetDummyLine() shouldn't be called")

        # we need to recreate the dummy line if the number of columns in the
        # control changed as it would have the incorrect number of fields
        # otherwise
        if len(self._lines) > 0 and len(self._lines[0]._items) != self.GetColumnCount():
            self._lines = []

        if not self._lines:
            line = UltimateListLineData(self)
            self._lines.append(line)

        return self._lines[0]


# ----------------------------------------------------------------------------
# line geometry (report mode only)
# ----------------------------------------------------------------------------

    def GetLineHeight(self, item=None):

        # we cache the line height as calling GetTextExtent() is slow

        if item is None or not self.HasExtraFlag(ULC_HAS_VARIABLE_ROW_HEIGHT):

            if not self._lineHeight:
                dc = wx.ClientDC(self)
                dc.SetFont(self.GetFont())

                dummy, y = dc.GetTextExtent("H")
                if self._small_image_list and self._small_image_list.GetImageCount():
                    iw, ih = self._small_image_list.GetSize(0)
                    y = max(y, ih)

                y += EXTRA_HEIGHT
                self._lineHeight = y + LINE_SPACING

            return self._lineHeight

        else:

            line = self.GetLine(item)
            LH = line.GetHeight()
            if LH != -1:
                return LH

            dc = wx.ClientDC(self)

            allTextY = 0

            for col, items in enumerate(line._items):

                if items.GetCustomRenderer():
                    allTextY = max(allTextY, items.GetCustomRenderer().GetLineHeight())
                    continue

                if items.HasFont():
                    dc.SetFont(items.GetFont())
                else:
                    dc.SetFont(self.GetFont())

                text_x, text_y, dummy = dc.GetMultiLineTextExtent(items.GetText())
                allTextY = max(text_y, allTextY)

                if items.GetWindow():
                    xSize, ySize = items.GetWindowSize()
                    allTextY = max(allTextY, ySize)

                if self._small_image_list and self._small_image_list.GetImageCount():
                    for img in items._image:
                        iw, ih = self._small_image_list.GetSize(img)
                        allTextY = max(allTextY, ih)

            allTextY += EXTRA_HEIGHT
            line.SetHeight(allTextY)

            return allTextY


    def GetLineY(self, line):

        if self.IsVirtual():
            return LINE_SPACING + line*self.GetLineHeight()

        lineItem = self.GetLine(line)
        lineY = lineItem.GetY()
        if lineY != -1:
            return lineY

        lineY = 0
        for l in xrange(line):
            lineY += self.GetLineHeight(l)

        lineItem.SetY(LINE_SPACING + lineY)
        return LINE_SPACING + lineY


    def GetLineRect(self, line):

        if not self.InReportView():
            return self.GetLine(line)._gi._rectAll

        rect = wx.Rect(HEADER_OFFSET_X, self.GetLineY(line), self.GetHeaderWidth(), self.GetLineHeight(line))
        return rect


    def GetLineLabelRect(self, line):

        if not self.InReportView():
            return self.GetLine(line)._gi._rectLabel

        image_x = 0
        item = self.GetLine(line)
        if item.HasImage():
            ix, iy = self.GetImageSize(item.GetImage())
            image_x = ix

        if item.GetKind() in [1, 2]:
            image_x += self.GetCheckboxImageSize()[0]

        rect = wx.Rect(image_x + HEADER_OFFSET_X, self.GetLineY(line), self.GetColumnWidth(0) - image_x, self.GetLineHeight(line))
        return rect


    def GetLineIconRect(self, line):

        if not self.InReportView():
            return self.GetLine(line)._gi._rectIcon

        ld = self.GetLine(line)

        image_x = HEADER_OFFSET_X
        if ld.GetKind() in [1, 2]:
            image_x += self.GetCheckboxImageSize()[0]

        rect = wx.Rect(image_x, self.GetLineY(line), *self.GetImageSize(ld.GetImage()))
        return rect


    def GetLineCheckboxRect(self, line):

        if not self.InReportView():
            return self.GetLine(line)._gi._rectCheck

        ld = self.GetLine(line)
        LH = self.GetLineHeight(line)
        wcheck, hcheck = self.GetCheckboxImageSize()
        rect = wx.Rect(HEADER_OFFSET_X, self.GetLineY(line) + LH/2 - hcheck/2, wcheck, hcheck)
        return rect


    def GetLineHighlightRect(self, line):

        return (self.InReportView() and [self.GetLineRect(line)] or [self.GetLine(line)._gi._rectHighlight])[0]


    def HitTestLine(self, line, x, y):

        ld = self.GetLine(line)

        if self.InReportView() and not self.IsVirtual():

            lineY = self.GetLineY(line)
            xstart = HEADER_OFFSET_X

            for col, item in enumerate(ld._items):

                width = self.GetColumnWidth(col)
                xOld = xstart
                xstart += width
                ix = 0

                if (line, col) in self._shortItems:
                    rect = wx.Rect(xOld, lineY, width, self.GetLineHeight(line))
                    if rect.Contains((x, y)):
                        newItem = self.GetParent().GetItem(line, col)
                        return newItem, ULC_HITTEST_ONITEM

                if item.GetKind() in [1, 2]:
                    # We got a checkbox-type item
                    ix, iy = self.GetCheckboxImageSize()
                    LH = self.GetLineHeight(line)
                    rect = wx.Rect(xOld, lineY + LH/2 - iy/2, ix, iy)
                    if rect.Contains((x, y)):
                        newItem = self.GetParent().GetItem(line, col)
                        return newItem, ULC_HITTEST_ONITEMCHECK

                if item.IsHyperText():
                    start, end = self.GetItemTextSize(item)
                    rect = wx.Rect(xOld+start, lineY, end, self.GetLineHeight(line))
                    if rect.Contains((x, y)):
                        newItem = self.GetParent().GetItem(line, col)
                        return newItem, ULC_HITTEST_ONITEMLABEL

                    xOld += ix

        if ld.HasImage() and self.GetLineIconRect(line).Contains((x, y)):
            return self.GetParent().GetItem(line), ULC_HITTEST_ONITEMICON

        # VS: Testing for "ld.HasText() || InReportView()" instead of
        #     "ld.HasText()" is needed to make empty lines in report view
        #     possible
        if ld.HasText() or self.InReportView():
            if self.InReportView():
                rect = self.GetLineRect(line)
            else:
                checkRect = self.GetLineCheckboxRect(line)
                if checkRect.Contains((x, y)):
                    return self.GetParent().GetItem(line), ULC_HITTEST_ONITEMCHECK

                rect = self.GetLineLabelRect(line)

        if rect.Contains((x, y)):
            return self.GetParent().GetItem(line), ULC_HITTEST_ONITEMLABEL

        rect = self.GetLineRect(line)
        if rect.Contains((x, y)):
            return self.GetParent().GetItem(line), ULC_HITTEST_ONITEM

        return None, 0


# ----------------------------------------------------------------------------
# highlight (selection) handling
# ----------------------------------------------------------------------------

    def IsHighlighted(self, line):

        if self.IsVirtual():

            return self._selStore.IsSelected(line)

        else: # !virtual

            ld = self.GetLine(line)
            return ld.IsHighlighted()


    def HighlightLines(self, lineFrom, lineTo, highlight=True):

        if self.IsVirtual():
            linesChanged = self._selStore.SelectRange(lineFrom, lineTo, highlight)
            if not linesChanged:
                # many items changed state, refresh everything
                self.RefreshLines(lineFrom, lineTo)

            else: # only a few items changed state, refresh only them

                for n in xrange(len(linesChanged)):
                    self.RefreshLine(linesChanged[n])

        else: # iterate over all items in non report view

            for line in xrange(lineFrom, lineTo+1):
                if self.HighlightLine(line, highlight):
                    self.RefreshLine(line)


    def HighlightLine(self, line, highlight=True):

        changed = False

        if self.IsVirtual():

            changed = self._selStore.SelectItem(line, highlight)

        else: # !virtual

            ld = self.GetLine(line)
            changed = ld.Highlight(highlight)

        dontNotify = self.HasExtraFlag(ULC_STICKY_HIGHLIGHT) and self.HasExtraFlag(ULC_STICKY_NOSELEVENT)

        if changed and not dontNotify:
            self.SendNotify(line, (highlight and [wxEVT_COMMAND_LIST_ITEM_SELECTED] or [wxEVT_COMMAND_LIST_ITEM_DESELECTED])[0])

        return changed


    def RefreshLine(self, line):

        if self.InReportView():

            visibleFrom, visibleTo = self.GetVisibleLinesRange()
            if line < visibleFrom or line > visibleTo:
                return

        rect = self.GetLineRect(line)
        rect.x, rect.y  = self.CalcScrolledPosition(rect.x, rect.y)
        self.RefreshRect(rect)


    def RefreshLines(self, lineFrom, lineTo):

        if self.InReportView():

            visibleFrom, visibleTo = self.GetVisibleLinesRange()

            if lineFrom < visibleFrom:
                lineFrom = visibleFrom
            if lineTo > visibleTo:
                lineTo = visibleTo

            rect = wx.Rect()
            rect.x = 0
            rect.y = self.GetLineY(lineFrom)
            rect.width = self.GetClientSize().x
            rect.height = self.GetLineY(lineTo) - rect.y + self.GetLineHeight(lineTo)

            rect.x, rect.y  = self.CalcScrolledPosition(rect.x, rect.y)
            self.RefreshRect(rect)

        else: # !report

            # TODO: this should be optimized...
            for line in xrange(lineFrom, lineTo+1):
                self.RefreshLine(line)


    def RefreshAfter(self, lineFrom):

        if self.InReportView():

            visibleFrom, visibleTo = self.GetVisibleLinesRange()

            if lineFrom < visibleFrom:
                lineFrom = visibleFrom
            elif lineFrom > visibleTo:
                return

            rect = wx.Rect()
            rect.x = 0
            rect.y = self.GetLineY(lineFrom)
            rect.x, rect.y  = self.CalcScrolledPosition(rect.x, rect.y)

            size = self.GetClientSize()
            rect.width = size.x
            # refresh till the bottom of the window
            rect.height = size.y - rect.y

            self.RefreshRect(rect)

        else: # !report

            # TODO: how to do it more efficiently?
            self._dirty = True


    def RefreshSelected(self):

        if self.IsEmpty():
            return

        if self.InReportView():

            fromm, to = self.GetVisibleLinesRange()

        else: # !virtual

            fromm = 0
            to = self.GetItemCount() - 1

        if self.HasCurrent() and self._current >= fromm and self._current <= to:
            self.RefreshLine(self._current)

        for line in xrange(fromm, to+1):
            # NB: the test works as expected even if self._current == -1
            if line != self._current and self.IsHighlighted(line):
                self.RefreshLine(line)


    def HideWindows(self):
        """Hides the windows associated to the items. Used internally."""

        for child in self._itemWithWindow:
            wnd = child.GetWindow()
            if wnd:
                wnd.Hide()


    def OnPaint(self, event):

        # Note: a wxPaintDC must be constructed even if no drawing is
        # done (a Windows requirement).
        dc = wx.BufferedPaintDC(self)

        dc.SetBackgroundMode(wx.TRANSPARENT)

        self.PrepareDC(dc)

        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.Clear()

        self.TileBackground(dc)
        self.PaintWaterMark(dc)

        if self.IsEmpty():
            # nothing to draw or not the moment to draw it
            return

        if self._dirty:
            # delay the repainting until we calculate all the items positions
            self.RecalculatePositions(False)

        useVista, useGradient = self._vistaselection, self._usegradients
        dev_x, dev_y = self.CalcScrolledPosition(0, 0)

        dc.SetFont(self.GetFont())

        if self.InReportView():
            visibleFrom, visibleTo = self.GetVisibleLinesRange()

            # mrcs: draw additional items
            if visibleFrom > 0:
                visibleFrom -= 1

            if visibleTo < self.GetItemCount() - 1:
                visibleTo += 1

            xOrig = dc.LogicalToDeviceX(0)
            yOrig = dc.LogicalToDeviceY(0)

            # tell the caller cache to cache the data
            if self.IsVirtual():

                evCache = UltimateListEvent(wxEVT_COMMAND_LIST_CACHE_HINT, self.GetParent().GetId())
                evCache.SetEventObject(self.GetParent())
                evCache.m_oldItemIndex = visibleFrom
                evCache.m_itemIndex = visibleTo
                self.GetParent().GetEventHandler().ProcessEvent(evCache)

            no_highlight = self.HasExtraFlag(ULC_NO_HIGHLIGHT)

            for line in xrange(visibleFrom, visibleTo+1):
                rectLine = self.GetLineRect(line)

                if not self.IsExposed(rectLine.x + xOrig, rectLine.y + yOrig, rectLine.width, rectLine.height):
                    # don't redraw unaffected lines to avoid flicker
                    continue

                theLine = self.GetLine(line)
                enabled = theLine.GetItem(0, CreateListItem(line, 0)).IsEnabled()
                oldPN, oldBR = dc.GetPen(), dc.GetBrush()
                theLine.DrawInReportMode(dc, line, rectLine,
                                         self.GetLineHighlightRect(line),
                                         self.IsHighlighted(line) and not no_highlight,
                                         line==self._current, enabled, oldPN, oldBR)

            if self.HasFlag(ULC_HRULES):
                pen = wx.Pen(self.GetRuleColour(), 1, wx.SOLID)
                clientSize = self.GetClientSize()

                # Don't draw the first one
                start = (visibleFrom > 0 and [visibleFrom] or [1])[0]

                dc.SetPen(pen)
                dc.SetBrush(wx.TRANSPARENT_BRUSH)
                for i in xrange(start, visibleTo+1):
                    lineY = self.GetLineY(i)
                    dc.DrawLine(0 - dev_x, lineY, clientSize.x - dev_x, lineY)

                # Draw last horizontal rule
                if visibleTo == self.GetItemCount() - 1:
                    lineY = self.GetLineY(visibleTo) + self.GetLineHeight(visibleTo)
                    dc.SetPen(pen)
                    dc.SetBrush(wx.TRANSPARENT_BRUSH)
                    dc.DrawLine(0 - dev_x, lineY, clientSize.x - dev_x , lineY)

            # Draw vertical rules if required
            if self.HasFlag(ULC_VRULES) and not self.IsEmpty():
                pen = wx.Pen(self.GetRuleColour(), 1, wx.SOLID)

                firstItemRect = self.GetItemRect(visibleFrom)
                lastItemRect = self.GetItemRect(visibleTo)
                x = firstItemRect.GetX()
                dc.SetPen(pen)
                dc.SetBrush(wx.TRANSPARENT_BRUSH)
                for col in xrange(self.GetColumnCount()):

                    if not self.IsColumnShown(col):
                        continue

                    colWidth = self.GetColumnWidth(col)
                    x += colWidth

                    x_pos = x - dev_x
                    if col < self.GetColumnCount()-1:
                        x_pos -= 2

                    dc.DrawLine(x_pos, firstItemRect.GetY() - 1 - dev_y, x_pos, lastItemRect.GetBottom() + 1 - dev_y)


        else: # !report

            for i in xrange(self.GetItemCount()):
                self.GetLine(i).Draw(i, dc)

        if wx.Platform not in ["__WXMAC__", "__WXGTK__"]:
            # Don't draw rect outline under Mac at all.
            # Draw it elsewhere on GTK
            if self.HasCurrent():
                if self._hasFocus and not self.HasExtraFlag(ULC_NO_HIGHLIGHT) and not useVista and not useGradient \
                   and not self.HasExtraFlag(ULC_BORDER_SELECT) and not self.HasExtraFlag(ULC_NO_FULL_ROW_SELECT):
                    dc.SetPen(wx.BLACK_PEN)
                    dc.SetBrush(wx.TRANSPARENT_BRUSH)
                    dc.DrawRectangleRect(self.GetLineHighlightRect(self._current))


    def OnEraseBackground(self, event):

        pass


    def TileBackground(self, dc):
        """Tiles the background image to fill all the available area."""

        if not self._backgroundImage:
            return

        if self._imageStretchStyle != _StyleTile:
            # Can we actually do something here (or in OnPaint()) To Handle
            # background images that are stretchable or always centered?
            # I tried but I get enormous flickering...
            return

        sz = self.GetClientSize()
        w = self._backgroundImage.GetWidth()
        h = self._backgroundImage.GetHeight()

        x = 0

        while x < sz.width:
            y = 0

            while y < sz.height:
                dc.DrawBitmap(self._backgroundImage, x, y, True)
                y = y + h

            x = x + w


    def PaintWaterMark(self, dc):

        if not self._waterMark:
            return

        width, height = self.CalcUnscrolledPosition(*self.GetClientSize())

        bitmapW = self._waterMark.GetWidth()
        bitmapH = self._waterMark.GetHeight()

        x = width - bitmapW - 5
        y = height - bitmapH - 5

        dc.DrawBitmap(self._waterMark, x, y, True)


    def HighlightAll(self, on=True):

        if self.IsSingleSel():

            if on:
                raise Exception("can't do this in a single sel control")

            # we just have one item to turn off
            if self.HasCurrent() and self.IsHighlighted(self._current):
                self.HighlightLine(self._current, False)
                self.RefreshLine(self._current)

        else: # multi sel
            if not self.IsEmpty():
                self.HighlightLines(0, self.GetItemCount() - 1, on)


    def OnChildFocus(self, event):

        # Do nothing here.  This prevents the default handler in wxScrolledWindow
        # from needlessly scrolling the window when the edit control is
        # dismissed.  See ticket #9563.

        pass


    def SendNotify(self, line, command, point=wx.DefaultPosition):

        bRet = True
        le = UltimateListEvent(command, self.GetParent().GetId())
        le.SetEventObject(self.GetParent())
        le.m_itemIndex = line

        # set only for events which have position
        if point != wx.DefaultPosition:
            le.m_pointDrag = point

        # don't try to get the line info for virtual list controls: the main
        # program has it anyhow and if we did it would result in accessing all
        # the lines, even those which are not visible now and this is precisely
        # what we're trying to avoid
        if not self.IsVirtual():

            if line != -1:
                self.GetLine(line).GetItem(0, le.m_item)

            #else: this happens for wxEVT_COMMAND_LIST_ITEM_FOCUSED event

            #else: there may be no more such item

        self.GetParent().GetEventHandler().ProcessEvent(le)
        bRet = le.IsAllowed()

        return bRet


    def ChangeCurrent(self, current):

        self._current = current

        # as the current item changed, we shouldn't start editing it when the
        # "slow click" timer expires as the click happened on another item
        if self._renameTimer.IsRunning():
            self._renameTimer.Stop()

        self.SendNotify(current, wxEVT_COMMAND_LIST_ITEM_FOCUSED)


    def EditLabel(self, item):

        if item < 0 or item >= self.GetItemCount():
            raise Exception("wrong index in UltimateListCtrl.EditLabel()")

        le = UltimateListEvent(wxEVT_COMMAND_LIST_BEGIN_LABEL_EDIT, self.GetParent().GetId())
        le.SetEventObject(self.GetParent())
        le.m_itemIndex = item
        data = self.GetLine(item)
        le.m_item = data.GetItem(0, le.m_item)

        self._textctrl = UltimateListTextCtrl(self, item)

        if self.GetParent().GetEventHandler().ProcessEvent(le) and not le.IsAllowed():
            # vetoed by user code
            return

        # We have to call this here because the label in question might just have
        # been added and no screen update taken place.
        if self._dirty:
            wx.SafeYield()
            # Pending events dispatched by wx.SafeYield might have changed the item
            # count
            if item >= self.GetItemCount():
                return None

        # modified
        self._textctrl.SetFocus()

        return self._textctrl


    def OnRenameTimer(self):

        if not self.HasCurrent():
            raise Exception("unexpected rename timer")

        self.EditLabel(self._current)


    def OnRenameAccept(self, itemEdit, value):

        le = UltimateListEvent(wxEVT_COMMAND_LIST_END_LABEL_EDIT, self.GetParent().GetId())
        le.SetEventObject(self.GetParent())
        le.m_itemIndex = itemEdit

        data = self.GetLine(itemEdit)

        le.m_item = data.GetItem(0, le.m_item)
        le.m_item._text = value

        return not self.GetParent().GetEventHandler().ProcessEvent(le) or le.IsAllowed()


    def OnRenameCancelled(self, itemEdit):

        # let owner know that the edit was cancelled
        le = UltimateListEvent(wxEVT_COMMAND_LIST_END_LABEL_EDIT, self.GetParent().GetId())
        le.SetEditCanceled(True)

        le.SetEventObject(self.GetParent())
        le.m_itemIndex = itemEdit

        data = self.GetLine(itemEdit)
        le.m_item = data.GetItem(0, le.m_item)

        self.GetEventHandler().ProcessEvent(le)


    def OnMouse(self, event):

        if wx.Platform == "__WXMAC__":
            # On wxMac we can't depend on the EVT_KILL_FOCUS event to properly
            # shutdown the edit control when the mouse is clicked elsewhere on the
            # listctrl because the order of events is different (or something like
            # that,) so explicitly end the edit if it is active.
            if event.LeftDown() and self._textctrl:
                self._textctrl.AcceptChanges()
                self._textctrl.Finish()

        if event.LeftDown():
            self.SetFocusIgnoringChildren()

        event.SetEventObject(self.GetParent())
        if self.GetParent().GetEventHandler().ProcessEvent(event) :
            return

        if event.GetEventType() == wx.wxEVT_MOUSEWHEEL:
            # let the base handle mouse wheel events.
            self.Refresh()
            event.Skip()
            return

        if not self.HasCurrent() or self.IsEmpty():
            if event.RightDown():
                self.SendNotify(-1, wxEVT_COMMAND_LIST_ITEM_RIGHT_CLICK, event.GetPosition())

                evtCtx = wx.ContextMenuEvent(wx.EVT_CONTEXT_MENU, self.GetParent().GetId(),
                                             self.ClientToScreen(event.GetPosition()))
                evtCtx.SetEventObject(self.GetParent())
                self.GetParent().GetEventHandler().ProcessEvent(evtCtx)

            return

        if self._dirty:
            return

        if not (event.Dragging() or event.ButtonDown() or event.LeftUp() or \
                event.ButtonDClick() or event.Moving() or event.RightUp()):
            return

        x = event.GetX()
        y = event.GetY()
        x, y = self.CalcUnscrolledPosition(x, y)

        # where did we hit it (if we did)?
        hitResult = 0
        newItem = None
        count = self.GetItemCount()

        if self.InReportView():
            if not self.HasExtraFlag(ULC_HAS_VARIABLE_ROW_HEIGHT):
                current = y/self.GetLineHeight()
                if current < count:
                    newItem, hitResult = self.HitTestLine(current, x, y)
                else:
                    return
            else:
                for current in xrange(count):
                    newItem, hitResult = self.HitTestLine(current, x, y)
                    if hitResult:
                        break
        else:
            # TODO: optimize it too! this is less simple than for report view but
            #       enumerating all items is still not a way to do it!!
            for current in xrange(count):
                newItem, hitResult = self.HitTestLine(current, x, y)
                if hitResult:
                    break

        theItem = None

        if not self.IsVirtual():
            theItem = CreateListItem(current, 0)
            theItem = self.GetItem(theItem)

        if event.GetEventType() == wx.wxEVT_MOTION and not event.Dragging():

            if current >= 0 and current < count and self.HasExtraFlag(ULC_TRACK_SELECT) and not self._hoverTimer.IsRunning():
                self._hoverItem = current
                self._hoverTimer.Start(HOVER_TIME, wx.TIMER_ONE_SHOT)

            if newItem and newItem.IsHyperText() and (hitResult & ULC_HITTEST_ONITEMLABEL) and theItem and theItem.IsEnabled():
                self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
                self._isonhyperlink = True
            else:
                if self._isonhyperlink:
                    self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
                    self._isonhyperlink = False

            if self.HasExtraFlag(ULC_STICKY_HIGHLIGHT) and hitResult:
                if not self.IsHighlighted(current):
                    self.HighlightAll(False)
                    self.ChangeCurrent(current)
                    self.ReverseHighlight(self._current)

            if self.HasExtraFlag(ULC_SHOW_TOOLTIPS):
                if newItem and hitResult & ULC_HITTEST_ONITEM:
                    if (newItem._itemId, newItem._col) in self._shortItems:
                        text = newItem.GetText()
                        if self.GetToolTip() and self.GetToolTip().GetTip() != text:
                            self.SetToolTipString(text)
                    else:
                        self.SetToolTipString("")
                else:
                    self.SetToolTipString("")

            if self.HasExtraFlag(ULC_HOT_TRACKING):
                if hitResult:
                    if self._oldHotCurrent != current:
                        if self._oldHotCurrent is not None:
                            self.RefreshLine(self._oldHotCurrent)
                        self._newHotCurrent = current
                        self.RefreshLine(self._newHotCurrent)
                        self._oldHotCurrent = current

            event.Skip()
            return

        if event.Dragging():

            if not self._isDragging:

                if self._lineLastClicked == -1 or not hitResult or not theItem or not theItem.IsEnabled():
                    return

                if self._dragCount == 0:
                    # we have to report the raw, physical coords as we want to be
                    # able to call HitTest(event.m_pointDrag) from the user code to
                    # get the item being dragged
                    self._dragStart = event.GetPosition()

                self._dragCount += 1

                if self._dragCount != 3:
                    return

                command = (event.RightIsDown() and [wxEVT_COMMAND_LIST_BEGIN_RDRAG] or [wxEVT_COMMAND_LIST_BEGIN_DRAG])[0]
                le = UltimateListEvent(command, self.GetParent().GetId())
                le.SetEventObject(self.GetParent())
                le.m_itemIndex = self._lineLastClicked
                le.m_pointDrag = self._dragStart
                self.GetParent().GetEventHandler().ProcessEvent(le)

                # we're going to drag this item
                self._isDragging = True
                self._dragItem = current

                # remember the old cursor because we will change it while
                # dragging
                self._oldCursor = self._cursor
                self.SetCursor(self._dragCursor)

            else:

                if current != self._dropTarget:

                    self.SetCursor(self._dragCursor)
                    # unhighlight the previous drop target
                    if self._dropTarget is not None:
                        self.RefreshLine(self._dropTarget)

                    move = current
                    if self._dropTarget:
                        move = (current > self._dropTarget and [current+1] or [current-1])[0]

                    self._dropTarget = current
                    self.MoveToItem(move)

                else:

                    if self._dragItem == current:
                        self.SetCursor(wx.StockCursor(wx.CURSOR_NO_ENTRY))

            if self.HasFlag(ULC_REPORT) and self._dragItem != current:
                self.DrawDnDArrow()

            return

        else:

            self._dragCount = 0

        if theItem and not theItem.IsEnabled():
            self.DragFinish(event)
            event.Skip()
            return

        if not hitResult:
            # outside of any item
            if event.RightDown():
                self.SendNotify(-1, wxEVT_COMMAND_LIST_ITEM_RIGHT_CLICK, event.GetPosition())
                evtCtx = wx.ContextMenuEvent(wx.EVT_CONTEXT_MENU, self.GetParent().GetId(),
                                             self.ClientToScreen(event.GetPosition()))
                evtCtx.SetEventObject(self.GetParent())
                self.GetParent().GetEventHandler().ProcessEvent(evtCtx)
            else:
                self.HighlightAll(False)
                self.DragFinish(event)

            return

        forceClick = False
        if event.ButtonDClick():
            if self._renameTimer.IsRunning():
                self._renameTimer.Stop()

            self._lastOnSame = False

            if current == self._lineLastClicked:
                self.SendNotify(current, wxEVT_COMMAND_LIST_ITEM_ACTIVATED)

                if newItem and newItem.GetKind() in [1, 2] and (hitResult & ULC_HITTEST_ONITEMCHECK):
                    self.CheckItem(newItem, not self.IsItemChecked(newItem))

                return

            else:

                # The first click was on another item, so don't interpret this as
                # a double click, but as a simple click instead
                forceClick = True

        if event.LeftUp():

            if self.DragFinish(event):
                return
            if self._lineSelectSingleOnUp != - 1:
                # select single line
                self.HighlightAll(False)
                self.ReverseHighlight(self._lineSelectSingleOnUp)

            if self._lastOnSame:
                if (current == self._current) and (hitResult == ULC_HITTEST_ONITEMLABEL) and self.HasFlag(ULC_EDIT_LABELS):
                    if not self.InReportView() or self.GetLineLabelRect(current).Contains((x, y)):
                        # This wx.SYS_DCLICK_MSEC is not yet wrapped in wxPython...
                        # dclick = wx.SystemSettings.GetMetric(wx.SYS_DCLICK_MSEC)
                        # m_renameTimer->Start(dclick > 0 ? dclick : 250, True)
                        self._renameTimer.Start(250, True)

            self._lastOnSame = False
            self._lineSelectSingleOnUp = -1

        elif event.RightUp():

            if self.DragFinish(event):
                return

        else:

            # This is necessary, because after a DnD operation in
            # from and to ourself, the up event is swallowed by the
            # DnD code. So on next non-up event (which means here and
            # now) self._lineSelectSingleOnUp should be reset.
            self._lineSelectSingleOnUp = -1

        if event.RightDown():

            if self.SendNotify(current, wxEVT_COMMAND_LIST_ITEM_RIGHT_CLICK, event.GetPosition()):
                self._lineBeforeLastClicked = self._lineLastClicked
                self._lineLastClicked = current
                # If the item is already selected, do not update the selection.
                # Multi-selections should not be cleared if a selected item is clicked.

                if not self.IsHighlighted(current):
                    self.HighlightAll(False)
                    self.ChangeCurrent(current)
                    self.ReverseHighlight(self._current)

                # Allow generation of context menu event
                event.Skip()

        elif event.MiddleDown():
            self.SendNotify(current, wxEVT_COMMAND_LIST_ITEM_MIDDLE_CLICK)

        elif event.LeftDown() or forceClick:
            self._lineBeforeLastClicked = self._lineLastClicked
            self._lineLastClicked = current

            oldCurrent = self._current
            oldWasSelected = self.IsHighlighted(self._current)

            cmdModifierDown = event.CmdDown()
            if self.IsSingleSel() or not (cmdModifierDown or event.ShiftDown()):
                if self.IsSingleSel() or not self.IsHighlighted(current):
                    self.HighlightAll(False)
                    self.ChangeCurrent(current)
                    self.ReverseHighlight(self._current)

                else: # multi sel & current is highlighted & no mod keys
                    self._lineSelectSingleOnUp = current
                    self.ChangeCurrent(current) # change focus

            else: # multi sel & either ctrl or shift is down
                if cmdModifierDown:
                    self.ChangeCurrent(current)
                    self.ReverseHighlight(self._current)

                elif event.ShiftDown():
                    self.ChangeCurrent(current)
                    lineFrom, lineTo = oldCurrent, current

                    if lineTo < lineFrom:
                        lineTo = lineFrom
                        lineFrom = self._current

                    self.HighlightLines(lineFrom, lineTo)

                else: # !ctrl, !shift

                    # test in the enclosing if should make it impossible
                    raise Exception("how did we get here?")

            if newItem:
                if event.LeftDown():
                    if newItem.GetKind() in [1, 2] and (hitResult & ULC_HITTEST_ONITEMCHECK):
                        self.CheckItem(newItem, not self.IsItemChecked(newItem))
                    if newItem.IsHyperText():
                        self.SetItemVisited(newItem, True)
                        self.HandleHyperLink(newItem)

            if self._current != oldCurrent:
                self.RefreshLine(oldCurrent)

            # forceClick is only set if the previous click was on another item
            self._lastOnSame = not forceClick and (self._current == oldCurrent) and oldWasSelected

            if self.HasExtraFlag(ULC_STICKY_HIGHLIGHT) and self.HasExtraFlag(ULC_STICKY_NOSELEVENT) and self.HasExtraFlag(ULC_SEND_LEFTCLICK):
                self.SendNotify(current, wxEVT_COMMAND_LIST_ITEM_LEFT_CLICK, event.GetPosition())


    def DrawDnDArrow(self):

        dc = wx.ClientDC(self)
        lineY = self.GetLineY(self._dropTarget)
        width = self.GetTotalWidth()

        dc.SetPen(wx.Pen(wx.BLACK, 2))
        x, y = self.CalcScrolledPosition(HEADER_OFFSET_X, lineY+2*HEADER_OFFSET_Y)

        tri1 = [wx.Point(x+1, y-2), wx.Point(x+1, y+4), wx.Point(x+4, y+1)]
        tri2 = [wx.Point(x+width-1, y-2), wx.Point(x+width-1, y+4), wx.Point(x+width-4, y+1)]
        dc.DrawPolygon(tri1)
        dc.DrawPolygon(tri2)

        dc.DrawLine(x, y+1, width, y+1)


    def DragFinish(self, event):

        if not self._isDragging:
            return False

        self._isDragging = False
        self._dragCount = 0
        self._dragItem = None
        self.SetCursor(self._oldCursor)
        self.Refresh()

        le = UltimateListEvent(wxEVT_COMMAND_LIST_END_DRAG, self.GetParent().GetId())
        le.SetEventObject(self.GetParent())
        le.m_itemIndex = self._dropTarget
        le.m_pointDrag = event.GetPosition()
        self.GetParent().GetEventHandler().ProcessEvent(le)

        return True


    def HandleHyperLink(self, item):
        """
        Handles the hyperlink items. Put in a separate method to avoid repetitive
        calls to the same code spread aound the file.
        """

        if self.IsItemHyperText(item):
            self.SendNotify(item._itemId, wxEVT_COMMAND_LIST_ITEM_HYPERLINK)


    def OnHoverTimer(self, event):

        x, y = self.ScreenToClient(wx.GetMousePosition())
        x, y = self.CalcUnscrolledPosition(x, y)
        item, hitResult = self.HitTestLine(self._hoverItem, x, y)

        if item and item._itemId == self._hoverItem:
            if not self.IsHighlighted(self._hoverItem):

                dontNotify = self.HasExtraFlag(ULC_STICKY_HIGHLIGHT) and self.HasExtraFlag(ULC_STICKY_NOSELEVENT)
                if not dontNotify:
                    self.SendNotify(self._hoverItem, wxEVT_COMMAND_LIST_ITEM_SELECTED)

                self.HighlightAll(False)
                self.ChangeCurrent(self._hoverItem)
                self.ReverseHighlight(self._current)


    def MoveToItem(self, item):

        if item == -1:
            return

        if item >= self.GetItemCount():
            item = self.GetItemCount() - 1

        rect = self.GetLineRect(item)
        client_w, client_h = self.GetClientSize()
        hLine = self.GetLineHeight(item)

        view_x = SCROLL_UNIT_X*self.GetScrollPos(wx.HORIZONTAL)
        view_y = hLine*self.GetScrollPos(wx.VERTICAL)

        if self.InReportView():

            # the next we need the range of lines shown it might be different, so
            # recalculate it
            self.ResetVisibleLinesRange()

            if not self.HasExtraFlag(ULC_HAS_VARIABLE_ROW_HEIGHT):

                if rect.y < view_y:
                    self.Scroll(-1, rect.y/hLine)
                if rect.y+rect.height+5 > view_y+client_h:
                    self.Scroll(-1, (rect.y+rect.height-client_h+hLine)/hLine)

                if wx.Platform == "__WXMAC__":
                    # At least on Mac the visible lines value will get reset inside of
                    # Scroll *before* it actually scrolls the window because of the
                    # Update() that happens there, so it will still have the wrong value.
                    # So let's reset it again and wait for it to be recalculated in the
                    # next paint event.  I would expect this problem to show up in wxGTK
                    # too but couldn't duplicate it there.  Perhaps the order of events
                    # is different...  --Robin
                    self.ResetVisibleLinesRange()

            else:

                view_y = SCROLL_UNIT_Y*self.GetScrollPos(wx.VERTICAL)
                start_y, height = rect.y, rect.height

                if start_y < view_y:
                    while start_y > view_y:
                        start_y -= SCROLL_UNIT_Y

                    self.Scroll(-1, start_y/SCROLL_UNIT_Y)

                if start_y + height > view_y + client_h:
                    while start_y + height < view_y + client_h:
                        start_y += SCROLL_UNIT_Y

                    self.Scroll(-1, (start_y+height-client_h+SCROLL_UNIT_Y)/SCROLL_UNIT_Y)

        else: # !report


            sx = sy = -1

            if rect.x-view_x < 5:
                sx = (rect.x - 5)/SCROLL_UNIT_X
            if rect.x+rect.width-5 > view_x+client_w:
                sx = (rect.x + rect.width - client_w + SCROLL_UNIT_X)/SCROLL_UNIT_X

            if rect.y-view_y < 5:
                sy = (rect.y - 5)/hLine
            if rect.y + rect.height - 5 > view_y + client_h:
                sy = (rect.y + rect.height - client_h + hLine)/hLine

            self.Scroll(sx, sy)


# ----------------------------------------------------------------------------
# keyboard handling
# ----------------------------------------------------------------------------

    def GetNextActiveItem(self, item, down=True):
        """Returns the next active item. Used Internally at present. """

        count = self.GetItemCount()
        initialItem = item

        while 1:
            if item >= count or item < 0:
                return initialItem

            listItem = CreateListItem(item, 0)
            listItem = self.GetItem(listItem, 0)
            if listItem.IsEnabled():
                return item

            item = (down and [item+1] or [item-1])[0]


    def OnArrowChar(self, newCurrent, event):

        oldCurrent = self._current
        newCurrent = self.GetNextActiveItem(newCurrent, newCurrent > oldCurrent)

        # in single selection we just ignore Shift as we can't select several
        # items anyhow
        if event.ShiftDown() and not self.IsSingleSel():

            self.ChangeCurrent(newCurrent)

            # refresh the old focus to remove it
            self.RefreshLine(oldCurrent)

            # select all the items between the old and the new one
            if oldCurrent > newCurrent:
                newCurrent = oldCurrent
                oldCurrent = self._current

            self.HighlightLines(oldCurrent, newCurrent)

        else: # !shift

            # all previously selected items are unselected unless ctrl is held
            # in a multi-selection control
            if not event.ControlDown() or self.IsSingleSel():
                self.HighlightAll(False)

            self.ChangeCurrent(newCurrent)

            # refresh the old focus to remove it
            self.RefreshLine(oldCurrent)

            if not event.ControlDown() or self.IsSingleSel():
                self.HighlightLine(self._current, True)

        self.RefreshLine(self._current)
        self.MoveToFocus()


    def OnKeyDown(self, event):

        parent = self.GetParent()

        # we propagate the key event upwards
        ke = wx.KeyEvent(event.GetEventType())

        ke.SetEventObject(parent)
        if parent.GetEventHandler().ProcessEvent(ke):
            return

        event.Skip()


    def OnKeyUp(self, event):

        parent = self.GetParent()

        # we propagate the key event upwards
        ke = wx.KeyEvent(event.GetEventType())

        ke.SetEventObject(parent)
        if parent.GetEventHandler().ProcessEvent(ke):
            return

        event.Skip()


    def OnChar(self, event):

        parent = self.GetParent()

        # we send a list_key event up
        if self.HasCurrent():
            le = UltimateListEvent(wxEVT_COMMAND_LIST_KEY_DOWN, self.GetParent().GetId())
            le.m_itemIndex = self._current
            le.m_item = self.GetLine(self._current).GetItem(0, le.m_item)
            le.m_code = event.GetKeyCode()
            le.SetEventObject(parent)
            parent.GetEventHandler().ProcessEvent(le)

        keyCode = event.GetKeyCode()
        if  keyCode not in [wx.WXK_UP, wx.WXK_DOWN, wx.WXK_RIGHT, wx.WXK_LEFT, \
                            wx.WXK_PAGEUP, wx.WXK_PAGEDOWN, wx.WXK_END, wx.WXK_HOME]:

            # propagate the char event upwards
            ke = wx.KeyEvent(event.GetEventType())
            ke.SetEventObject(parent)
            if parent.GetEventHandler().ProcessEvent(ke):
                return

        if event.GetKeyCode() == wx.WXK_TAB:
            nevent = wx.NavigationKeyEvent()
            nevent.SetWindowChange(event.ControlDown())
            nevent.SetDirection(not event.ShiftDown())
            nevent.SetEventObject(self.GetParent().GetParent())
            nevent.SetCurrentFocus(self._parent)
            if self.GetParent().GetParent().GetEventHandler().ProcessEvent(nevent):
                return

        # no item . nothing to do
        if not self.HasCurrent():
            event.Skip()
            return

        keyCode = event.GetKeyCode()

        if keyCode == wx.WXK_UP:
            if self._current > 0:
                self.OnArrowChar(self._current - 1, event)
                if self.HasExtraFlag(ULC_HAS_VARIABLE_ROW_HEIGHT):
                    self._dirty = True

        elif keyCode == wx.WXK_DOWN:
            if self._current < self.GetItemCount() - 1:
                self.OnArrowChar(self._current + 1, event)
                if self.HasExtraFlag(ULC_HAS_VARIABLE_ROW_HEIGHT):
                    self._dirty = True

        elif keyCode == wx.WXK_END:
            if not self.IsEmpty():
                self.OnArrowChar(self.GetItemCount() - 1, event)
                self._dirty = True

        elif keyCode == wx.WXK_HOME:
            if not self.IsEmpty():
                self.OnArrowChar(0, event)
                self._dirty = True

        elif keyCode == wx.WXK_PRIOR:
            steps = (self.InReportView() and [self._linesPerPage - 1] or [self._current % self._linesPerPage])[0]
            index = self._current - steps

            if index < 0:
                index = 0

            self.OnArrowChar(index, event)
            self._dirty = True

        elif keyCode == wx.WXK_NEXT:

            steps = (self.InReportView() and [self._linesPerPage - 1] or [self._linesPerPage - (self._current % self._linesPerPage) - 1])[0]
            index = self._current + steps
            count = self.GetItemCount()

            if index >= count:
                index = count - 1

            self.OnArrowChar(index, event)
            self._dirty = True

        elif keyCode == wx.WXK_LEFT:
            if not self.InReportView():

                index = self._current - self._linesPerPage
                if index < 0:
                    index = 0

                self.OnArrowChar(index, event)

        elif keyCode == wx.WXK_RIGHT:
            if not self.InReportView():

                index = self._current + self._linesPerPage
                count = self.GetItemCount()

                if index >= count:
                    index = count - 1

                self.OnArrowChar(index, event)

        elif keyCode == wx.WXK_SPACE:
            if self.IsSingleSel():

                if event.ControlDown():
                    self.ReverseHighlight(self._current)
                else: # normal space press
                    self.SendNotify(self._current, wxEVT_COMMAND_LIST_ITEM_ACTIVATED)

            else:
                # select it in ReverseHighlight() below if unselected
                self.ReverseHighlight(self._current)

        elif keyCode in [wx.WXK_RETURN, wx.WXK_EXECUTE, wx.WXK_NUMPAD_ENTER]:
            self.SendNotify(self._current, wxEVT_COMMAND_LIST_ITEM_ACTIVATED)

        else:
            event.Skip()


# ----------------------------------------------------------------------------
# focus handling
# ----------------------------------------------------------------------------

    def OnSetFocus(self, event):

        if self.GetParent():
            event = wx.FocusEvent(wx.wxEVT_SET_FOCUS, self.GetParent().GetId())
            event.SetEventObject(self.GetParent())
            if self.GetParent().GetEventHandler().ProcessEvent(event):
                return

        # wxGTK sends us EVT_SET_FOCUS events even if we had never got
        # EVT_KILL_FOCUS before which means that we finish by redrawing the items
        # which are already drawn correctly resulting in horrible flicker - avoid
        # it
        if not self._hasFocus:
            self._hasFocus = True
            self.Refresh()


    def OnKillFocus(self, event):

        if self.GetParent():
            event = wx.FocusEvent(wx.wxEVT_KILL_FOCUS, self.GetParent().GetId())
            event.SetEventObject(self.GetParent())
            if self.GetParent().GetEventHandler().ProcessEvent(event):
                return

        self._hasFocus = False
        self.Refresh()


    def DrawImage(self, index, dc, x, y, enabled):

        if self.HasFlag(ULC_ICON) and self._normal_image_list:
            imgList = (enabled and [self._normal_image_list] or [self._normal_grayed_image_list])[0]
            imgList.Draw(index, dc, x, y, wx.IMAGELIST_DRAW_TRANSPARENT)

        elif self.HasFlag(ULC_SMALL_ICON) and self._small_image_list:
            imgList = (enabled and [self._small_image_list] or [self._small_grayed_image_list])[0]
            imgList.Draw(index, dc, x, y, wx.IMAGELIST_DRAW_TRANSPARENT)

        elif self.HasFlag(ULC_LIST) and self._small_image_list:
            imgList = (enabled and [self._small_image_list] or [self._small_grayed_image_list])[0]
            imgList.Draw(index, dc, x, y, wx.IMAGELIST_DRAW_TRANSPARENT)

        elif self.InReportView() and self._small_image_list:
            imgList = (enabled and [self._small_image_list] or [self._small_grayed_image_list])[0]
            imgList.Draw(index, dc, x, y, wx.IMAGELIST_DRAW_TRANSPARENT)


    def DrawCheckbox(self, dc, x, y, kind, checked, enabled):

        imgList = (enabled and [self._image_list_check] or [self._grayed_check_list])[0]
        if kind == 1:
            # checkbox
            index = (checked and [0] or [1])[0]
        else:
            # radiobutton
            index = (checked and [2] or [3])[0]

        imgList.Draw(index, dc, x, y, wx.IMAGELIST_DRAW_TRANSPARENT)


    def GetCheckboxImageSize(self):

        bmp = self._image_list_check.GetBitmap(0)
        return bmp.GetWidth(), bmp.GetHeight()


    def GetImageSize(self, index):

        width = height = 0

        if self.HasFlag(ULC_ICON) and self._normal_image_list:

            for indx in index:
                w, h = self._normal_image_list.GetSize(indx)
                width += w + MARGIN_BETWEEN_TEXT_AND_ICON
                height = max(height, h)

        elif self.HasFlag(ULC_SMALL_ICON) and self._small_image_list:

            for indx in index:
                w, h = self._small_image_list.GetSize(indx)
                width += w + MARGIN_BETWEEN_TEXT_AND_ICON
                height = max(height, h)

        elif self.HasFlag(ULC_LIST) and self._small_image_list:

            for indx in index:
                w, h = self._small_image_list.GetSize(indx)
                width += w + MARGIN_BETWEEN_TEXT_AND_ICON
                height = max(height, h)

        elif self.InReportView() and self._small_image_list:

            for indx in index:
                w, h = self._small_image_list.GetSize(indx)
                width += w + MARGIN_BETWEEN_TEXT_AND_ICON
                height = max(height, h)

        return width, height


    def GetTextLength(self, s):

        dc = wx.ClientDC(self)
        dc.SetFont(self.GetFont())

        lw, lh, dummy = dc.GetMultiLineTextExtent(s)

        return lw + AUTOSIZE_COL_MARGIN


    def SetImageList(self, imageList, which):

        self._dirty = True

        # calc the spacing from the icon size
        width = height = 0
        if imageList and imageList.GetImageCount():
            width, height = imageList.GetSize(0)

        if which == wx.IMAGE_LIST_NORMAL:
            self._normal_image_list = imageList
            self._normal_grayed_image_list = wx.ImageList(width, height, True, 0)

            for ii in xrange(imageList.GetImageCount()):
                bmp = imageList.GetBitmap(ii)
                image = wx.ImageFromBitmap(bmp)
                image = GrayOut(image)
                newbmp = wx.BitmapFromImage(image)
                self._normal_grayed_image_list.Add(newbmp)

            self._normal_spacing = width + 8

        if which == wx.IMAGE_LIST_SMALL:
            self._small_image_list = imageList
            self._small_spacing = width + 14

            self._small_grayed_image_list = wx.ImageList(width, height, True, 0)

            for ii in xrange(imageList.GetImageCount()):
                bmp = imageList.GetBitmap(ii)
                image = wx.ImageFromBitmap(bmp)
                image = GrayOut(image)
                newbmp = wx.BitmapFromImage(image)
                self._small_grayed_image_list.Add(newbmp)

        self._lineHeight = 0  # ensure that the line height will be recalc'd
        self.ResetLineDimensions()


    def SetImageListCheck(self, sizex, sizey, imglist=None):
        """Sets the check image list."""

        # Image list to hold disabled versions of each control
        self._grayed_check_list = wx.ImageList(sizex, sizey, True, 0)

        if imglist is None:

            self._image_list_check = wx.ImageList(sizex, sizey)

            # Get the Checkboxes
            self._image_list_check.Add(self.GetControlBmp(checkbox=True,
                                                          checked=True,
                                                          enabled=True,
                                                          x=sizex, y=sizey))
            self._grayed_check_list.Add(self.GetControlBmp(checkbox=True,
                                                           checked=True,
                                                           enabled=False,
                                                           x=sizex, y=sizey))

            self._image_list_check.Add(self.GetControlBmp(checkbox=True,
                                                          checked=False,
                                                          enabled=True,
                                                          x=sizex, y=sizey))
            self._grayed_check_list.Add(self.GetControlBmp(checkbox=True,
                                                           checked=False,
                                                           enabled=False,
                                                           x=sizex, y=sizey))
            # Get the Radio Buttons
            self._image_list_check.Add(self.GetControlBmp(checkbox=False,
                                                          checked=True,
                                                          enabled=True,
                                                          x=sizex, y=sizey))
            self._grayed_check_list.Add(self.GetControlBmp(checkbox=False,
                                                           checked=True,
                                                           enabled=False,
                                                           x=sizex, y=sizey))

            self._image_list_check.Add(self.GetControlBmp(checkbox=False,
                                                          checked=False,
                                                          enabled=True,
                                                          x=sizex, y=sizey))
            self._grayed_check_list.Add(self.GetControlBmp(checkbox=False,
                                                           checked=False,
                                                           enabled=False,
                                                           x=sizex, y=sizey))
        else:

            sizex, sizey = imglist.GetSize(0)
            self._image_list_check = imglist

            for ii in xrange(self._image_list_check.GetImageCount()):

                bmp = self._image_list_check.GetBitmap(ii)
                image = wx.ImageFromBitmap(bmp)
                image = GrayOut(image)
                newbmp = wx.BitmapFromImage(image)
                self._grayed_check_list.Add(newbmp)

        self._dirty = True

        if imglist:
            self.RecalculatePositions()


    def GetControlBmp(self, checkbox=True, checked=False,
                      enabled=True, x=16, y=16):
        """Get a native looking checkbox or radio button bitmap
        @keyword checkbox: Get a checkbox=True, radiobutton=False
        @keyword checked: contorl is marked or not

        """
        bmp = wx.EmptyBitmap(x, y)
        mdc = wx.MemoryDC(bmp)
        dc = wx.GCDC(mdc)
        render = wx.RendererNative.Get()

        if checked:
            flag = wx.CONTROL_CHECKED
        else:
            flag = 0

        if not enabled:
            flag |= wx.CONTROL_DISABLED

        if checkbox:
            render.DrawCheckBox(self, mdc, (0, 0, x, y), flag)
        else:
            render.DrawRadioButton(self, mdc, (0, 0, x, y), flag)

        mdc.SelectObject(wx.NullBitmap)
        return bmp


    def SetItemSpacing(self, spacing, isSmall=False):

        self._dirty = True

        if isSmall:
            self._small_spacing = spacing
        else:
            self._normal_spacing = spacing


    def GetItemSpacing(self, isSmall=False):

        return (isSmall and [self._small_spacing] or [self._normal_spacing])[0]


# ----------------------------------------------------------------------------
# columns
# ----------------------------------------------------------------------------

    def SetColumn(self, col, item):

        column = self._columns[col]

        if item._width == ULC_AUTOSIZE_USEHEADER:
            item._width = self.GetTextLength(item._text)

        column.SetItem(item)

        headerWin = self.GetListCtrl()._headerWin
        if headerWin:
            headerWin._dirty = True

        self._dirty = True

        # invalidate it as it has to be recalculated
        self._headerWidth = 0


    def SetColumnWidth(self, col, width):

        if col < 0:
            raise Exception("invalid column index")

        if not self.InReportView() and not self.InTileView() and not self.HasExtraFlag(ULC_HEADER_IN_ALL_VIEWS):
            raise Exception("SetColumnWidth() can only be called in report/tile modes or with the ULC_HEADER_IN_ALL_VIEWS extra flag set.")

        self._dirty = True
        headerWin = self.GetListCtrl()._headerWin
        footerWin = self.GetListCtrl()._footerWin

        if headerWin:
            headerWin._dirty = True

        if footerWin:
            footerWin._dirty = True

        column = self._columns[col]
        count = self.GetItemCount()

        if width == ULC_AUTOSIZE_USEHEADER:

            width = self.GetTextLength(column.GetText())
            width += 2*EXTRA_WIDTH

            if column.GetKind() in [1, 2]:
                ix, iy = self._owner.GetCheckboxImageSize()
                width += ix + HEADER_IMAGE_MARGIN_IN_REPORT_MODE

            # check for column header's image availability
            images = column.GetImage()
            for img in images:
                if self._small_image_list:
                    ix, iy = self._small_image_list.GetSize(img)
                    width += ix + HEADER_IMAGE_MARGIN_IN_REPORT_MODE

        elif width == ULC_AUTOSIZE:

            if self.IsVirtual() or not self.InReportView():
                # TODO: determine the max width somehow...
                width = WIDTH_COL_DEFAULT

            else: # !virtual

                maxW = AUTOSIZE_COL_MARGIN

                #  if the cached column width isn't valid then recalculate it
                if self._aColWidths[col]._bNeedsUpdate:

                    for i in xrange(count):

                        line = self.GetLine(i)
                        itemData = line._items[col]
                        item = UltimateListItem()

                        item = itemData.GetItem(item)
                        itemWidth = self.GetItemWidthWithImage(item)
                        if itemWidth > maxW and not item._overFlow:
                            maxW = itemWidth

                    self._aColWidths[col]._bNeedsUpdate = False
                    self._aColWidths[col]._nMaxWidth = maxW

                maxW = self._aColWidths[col]._nMaxWidth
                width = maxW + AUTOSIZE_COL_MARGIN

        column.SetWidth(width)

        # invalidate it as it has to be recalculated
        self._headerWidth = 0
        self._footerWidth = 0

        if footerWin:
            footerWin.Refresh()


    def GetHeaderWidth(self):

        if not self._headerWidth:

            count = self.GetColumnCount()
            for col in xrange(count):

                if not self.IsColumnShown(col):
                    continue

                self._headerWidth += self.GetColumnWidth(col)

        if self.HasExtraFlag(ULC_FOOTER):
            self._footerWidth = self._headerWidth

        return self._headerWidth


    def GetColumn(self, col):

        item = UltimateListItem()
        column = self._columns[col]
        item = column.GetItem(item)

        return item


    def GetColumnWidth(self, col):

        column = self._columns[col]
        return column.GetWidth()


    def GetTotalWidth(self):

        width = 0
        for column in self._columns:
            width += column.GetWidth()

        return width

# ----------------------------------------------------------------------------
# item state
# ----------------------------------------------------------------------------

    def SetItem(self, item):

        id = item._itemId

        if id < 0 or id >= self.GetItemCount():
            raise Exception("invalid item index in SetItem")

        if not self.IsVirtual():

            line = self.GetLine(id)
            line.SetItem(item._col, item)

            # Set item state if user wants
            if item._mask & ULC_MASK_STATE:
                self.SetItemState(item._itemId, item._state, item._state)

            if self.InReportView():

                #  update the Max Width Cache if needed
                width = self.GetItemWidthWithImage(item)

                if width > self._aColWidths[item._col]._nMaxWidth:
                    self._aColWidths[item._col]._nMaxWidth = width
                    self._aColWidths[item._col]._bNeedsUpdate = True

        if self.HasExtraFlag(ULC_HAS_VARIABLE_ROW_HEIGHT):
            line.ResetDimensions()

        # update the item on screen
        if self.InReportView():
            rectItem = self.GetItemRect(id)
            self.RefreshRect(rectItem)


    def SetItemStateAll(self, state, stateMask):

        if self.IsEmpty():
            return

        # first deal with selection
        if stateMask & ULC_STATE_SELECTED:

            # set/clear select state
            if self.IsVirtual():

                # optimized version for virtual listctrl.
                self._selStore.SelectRange(0, self.GetItemCount() - 1, state==ULC_STATE_SELECTED)
                self.Refresh()

            elif state & ULC_STATE_SELECTED:

                count = self.GetItemCount()
                for i in xrange(count):
                    self.SetItemState(i, ULC_STATE_SELECTED, ULC_STATE_SELECTED)

            else:

                # clear for non virtual (somewhat optimized by using GetNextItem())
                i = -1
                while 1:
                    i += 1
                    if self.GetNextItem(i, ULC_NEXT_ALL, ULC_STATE_SELECTED) == -1:
                        break

                    self.SetItemState(i, 0, ULC_STATE_SELECTED)

        if self.HasCurrent() and state == 0 and stateMask & ULC_STATE_FOCUSED:

            # unfocus all: only one item can be focussed, so clearing focus for
            # all items is simply clearing focus of the focussed item.
            self.SetItemState(self._current, state, stateMask)

        #(setting focus to all items makes no sense, so it is not handled here.)


    def SetItemState(self, litem, state, stateMask):

        if litem == -1:
            self.SetItemStateAll(state, stateMask)
            return

        if litem < 0 or litem >= self.GetItemCount():
            raise Exception("invalid item index in SetItemState")

        oldCurrent = self._current
        item = litem    # safe because of the check above

        # do we need to change the focus?
        if stateMask & ULC_STATE_FOCUSED:

            if state & ULC_STATE_FOCUSED:

                # don't do anything if this item is already focused
                if item != self._current:

                    self.ChangeCurrent(item)

                    if oldCurrent != - 1:

                        if self.IsSingleSel():

                            self.HighlightLine(oldCurrent, False)

                        self.RefreshLine(oldCurrent)

                    self.RefreshLine(self._current)

            else: # unfocus

                # don't do anything if this item is not focused
                if item == self._current:

                    self.ResetCurrent()

                    if self.IsSingleSel():

                        # we must unselect the old current item as well or we
                        # might end up with more than one selected item in a
                        # single selection control
                        self.HighlightLine(oldCurrent, False)

                    self.RefreshLine(oldCurrent)

        # do we need to change the selection state?
        if stateMask & ULC_STATE_SELECTED:

            on = (state & ULC_STATE_SELECTED) != 0

            if self.IsSingleSel():

                if on:

                    # selecting the item also makes it the focused one in the
                    # single sel mode
                    if self._current != item:

                        self.ChangeCurrent(item)

                        if oldCurrent != - 1:

                            self.HighlightLine(oldCurrent, False)
                            self.RefreshLine(oldCurrent)

                else: # off

                    # only the current item may be selected anyhow
                    if item != self._current:
                        return

            if self.HighlightLine(item, on):
                self.RefreshLine(item)


    def GetItemState(self, item, stateMask):

        if item < 0 or item >= self.GetItemCount():
            raise Exception("invalid item index in GetItemState")

        ret = ULC_STATE_DONTCARE

        if stateMask & ULC_STATE_FOCUSED:
            if item == self._current:
                ret |= ULC_STATE_FOCUSED

        if stateMask & ULC_STATE_SELECTED:
            if self.IsHighlighted(item):
                ret |= ULC_STATE_SELECTED

        return ret


    def GetItem(self, item, col=0):

        if item._itemId < 0 or item._itemId >= self.GetItemCount():
            raise Exception("invalid item index in GetItem")

        line = self.GetLine(item._itemId)
        item = line.GetItem(col, item)

        # Get item state if user wants it
        if item._mask & ULC_MASK_STATE:
            item._state = self.GetItemState(item._itemId, ULC_STATE_SELECTED | ULC_STATE_FOCUSED)

        return item


    def CheckItem(self, item, checked=True, sendEvent=True):
        """
        Actually checks/uncheks an item, sending (eventually) the two
        events EVT_LIST_ITEM_CHECKING/EVT_LIST_ITEM_CHECKED.
        """

        # Should we raise an error here?!?
        if item.GetKind() == 0 or not item.IsEnabled():
            return

        if sendEvent:

            parent = self.GetParent()
            le = UltimateListEvent(wxEVT_COMMAND_LIST_ITEM_CHECKING, parent.GetId())
            le.m_itemIndex = item._itemId
            le.m_item = item
            le.SetEventObject(parent)

            if parent.GetEventHandler().ProcessEvent(le):
                # Blocked by user
                return

        item.Check(checked)
        self.SetItem(item)
        self.RefreshLine(item._itemId)

        if not sendEvent:
            return

        le = UltimateListEvent(wxEVT_COMMAND_LIST_ITEM_CHECKED, parent.GetId())
        le.m_itemIndex = item._itemId
        le.m_item = item
        le.SetEventObject(parent)
        parent.GetEventHandler().ProcessEvent(le)


    def AutoCheckChild(self, isChecked, column):

        for indx in xrange(self.GetItemCount()):
            item = CreateListItem(indx, column)
            newItem = self.GetItem(item, column)
            self.CheckItem(newItem, not isChecked, False)


    def AutoToggleChild(self, column):

        for indx in xrange(self.GetItemCount()):
            item = CreateListItem(indx, column)
            newItem = self.GetItem(item, column)

            if newItem.GetKind() != 1:
                continue

            self.CheckItem(newItem, not item.IsChecked(), False)


    def IsItemChecked(self, item):
        """Returns whether an item is checked or not."""

        item = self.GetItem(item, item._col)
        return item.IsChecked()


    def IsItemEnabled(self, item):
        """Returns whether an item is enabled or not."""

        item = self.GetItem(item, item._col)
        return item.IsEnabled()


    def EnableItem(self, item, enable=True):

        item = self.GetItem(item, 0)
        if item.IsEnabled() == enable:
            return False

        item.Enable(enable)

        wnd = item.GetWindow()
        # Handles the eventual window associated to the item
        if wnd:
            wnd.Enable(enable)

        self.SetItem(item)

        return True


    def GetItemKind(self, item):

        item = self.GetItem(item, item._col)
        return item.GetKind()


    def SetItemKind(self, item, kind):

        item = self.GetItem(item, item._col)
        item.SetKind(kind)
        self.SetItem(item)

        return True


    def IsItemHyperText(self, item):
        """Returns whether an item is hypertext or not."""

        item = self.GetItem(item, item._col)
        return item.IsHyperText()


    def SetItemHyperText(self, item, hyper=True):

        item = self.GetItem(item, item._col)
        item.SetHyperText(hyper)
        self.SetItem(item)

        return True


    def GetHyperTextFont(self):
        """Returns the font used to render an hypertext item."""

        return self._hypertextfont


    def SetHyperTextFont(self, font):
        """Sets the font used to render an hypertext item."""

        self._hypertextfont = font
        self._dirty = True


    def SetHyperTextNewColour(self, colour):
        """Sets the colour used to render a non-visited hypertext item."""

        self._hypertextnewcolour = colour
        self._dirty = True


    def GetHyperTextNewColour(self):
        """Returns the colour used to render a non-visited hypertext item."""

        return self._hypertextnewcolour


    def SetHyperTextVisitedColour(self, colour):
        """Sets the colour used to render a visited hypertext item."""

        self._hypertextvisitedcolour = colour
        self._dirty = True


    def GetHyperTextVisitedColour(self):
        """Returns the colour used to render a visited hypertext item."""

        return self._hypertextvisitedcolour


    def SetItemVisited(self, item, visited=True):
        """Sets whether an hypertext item was visited."""

        newItem = self.GetItem(item, item._col)
        newItem.SetVisited(visited)
        self.SetItem(newItem)
        self.RefreshLine(item)

        return True


    def GetItemVisited(self, item):
        """Returns whether an hypertext item was visited."""

        item = self.GetItem(item, item._col)
        return item.GetVisited()


    def GetItemWindow(self, item):
        """Returns the window associated to the item (if any)."""

        item = self.GetItem(item, item._col)
        return item.GetWindow()


    def SetItemWindow(self, item, wnd, expand=False):
        """Sets the window for the given item"""

        if not self.InReportView() and not self.HasExtraFlag(ULC_HAS_VARIABLE_ROW_HEIGHT):
            raise Exception("Widgets are only allowed in repotr mode and with the ULC_HAS_VARIABLE_ROW_HEIGHT extra style.")

        item = self.GetItem(item, item._col)

        if wnd is not None:
            self._hasWindows = True
            if item not in self._itemWithWindow:
                self._itemWithWindow.append(item)
            else:
                self.DeleteItemWindow(item)
        else:
            self.DeleteItemWindow(item)

        item.SetWindow(wnd, expand)
        self.SetItem(item)
        self.RecalculatePositions()
        self.Refresh()


    def DeleteItemWindow(self, item):
        """Deletes the window associated to an item (if any). """

        if item.GetWindow() is None:
            return

        item.DeleteWindow()
        if item in self._itemWithWindow:
            self._itemWithWindow.remove(item)

        self.SetItem(item)
        self.RecalculatePositions()


    def GetItemWindowEnabled(self, item):
        """Returns whether the window associated to the item is enabled."""

        item = self.GetItem(item, item._col)
        return item.GetWindowEnabled()


    def SetItemWindowEnabled(self, item, enable=True):
        """Enables/disables the window associated to the item."""

        item = self.GetItem(item, item._col)
        item.SetWindowEnabled(enable)
        self.SetItem(item)
        self.Refresh()


    def GetItemCustomRenderer(self, item):

        item = self.GetItem(item, item._col)
        return item.GetCustomRenderer()


    def SetItemCustomRenderer(self, item, renderer=None):

        item = self.GetItem(item, item._col)
        item.SetCustomRenderer(renderer)
        self.SetItem(item)
        self.ResetLineDimensions()
        self.Refresh()


    def GetItemOverFlow(self, item):

        item = self.GetItem(item, item._col)
        return item.GetOverFlow()


    def SetItemOverFlow(self, item, over=True):

        item = self.GetItem(item, item._col)
        item.SetOverFlow(over)
        self.SetItem(item)
        self.Refresh()


# ----------------------------------------------------------------------------
# item count
# ----------------------------------------------------------------------------

    def GetItemCount(self):

        return (self.IsVirtual() and [self._countVirt] or [len(self._lines)])[0]


    def SetItemCount(self, count):

        self._selStore.SetItemCount(count)
        self._countVirt = count

        self.ResetVisibleLinesRange()

        # scrollbars must be reset
        self._dirty = True


    def GetSelectedItemCount(self):

        # deal with the quick case first
        if self.IsSingleSel():
            return (self.HasCurrent() and [self.IsHighlighted(self._current)] or [False])[0]

        # virtual controls remmebers all its selections itself
        if self.IsVirtual():
            return self._selStore.GetSelectedCount()

        # TODO: we probably should maintain the number of items selected even for
        #       non virtual controls as enumerating all lines is really slow...
        countSel = 0
        count = self.GetItemCount()
        for line in xrange(count):
            if self.GetLine(line).IsHighlighted():
                countSel += 1

        return countSel


# ----------------------------------------------------------------------------
# item position/size
# ----------------------------------------------------------------------------

    def GetViewRect(self):

        if self.HasFlag(ULC_LIST):
            raise Exception("UltimateListCtrl.GetViewRect() not implemented for list view")

        # we need to find the longest/tallest label
        xMax = yMax = 0
        count = self.GetItemCount()

        if count:
            for i in xrange(count):
                # we need logical, not physical, coordinates here, so use
                # GetLineRect() instead of GetItemRect()
                r = self.GetLineRect(i)
                x, y = r.GetRight(), r.GetBottom()

                if x > xMax:
                    xMax = x
                if y > yMax:
                    yMax = y

        # some fudge needed to make it look prettier
        xMax += 2*EXTRA_BORDER_X
        yMax += 2*EXTRA_BORDER_Y

        # account for the scrollbars if necessary
        sizeAll = self.GetClientSize()
        if xMax > sizeAll.x:
            yMax += wx.SystemSettings.GetMetric(wx.SYS_HSCROLL_Y)
        if yMax > sizeAll.y:
            xMax += wx.SystemSettings.GetMetric(wx.SYS_VSCROLL_X)

        return wx.Rect(0, 0, xMax, yMax)


    def GetSubItemRect(self, item, subItem):

        if not self.InReportView() and subItem == ULC_GETSUBITEMRECT_WHOLEITEM:
            raise Exception("GetSubItemRect only meaningful in report view")

        if item < 0 or item >= self.GetItemCount():
            raise Exception("invalid item in GetSubItemRect")

        # ensure that we're laid out, otherwise we could return nonsense
        if self._dirty:
            self.RecalculatePositions(True)

        rect = self.GetLineRect(item)

        # Adjust rect to specified column
        if subItem != ULC_GETSUBITEMRECT_WHOLEITEM:
            if subItem < 0 or subItem >= self.GetColumnCount():
                raise Exception("invalid subItem in GetSubItemRect")

            for i in xrange(subItem):
                rect.x += self.GetColumnWidth(i)

            rect.width = self.GetColumnWidth(subItem)

        rect.x, rect.y = self.CalcScrolledPosition(rect.x, rect.y)
        return rect


    def GetItemRect(self, item):

        return self.GetSubItemRect(item, ULC_GETSUBITEMRECT_WHOLEITEM)


    def GetItemPosition(self, item):

        rect = self.GetItemRect(item)
        return wx.Point(rect.x, rect.y)


# ----------------------------------------------------------------------------
# geometry calculation
# ----------------------------------------------------------------------------

    def RecalculatePositions(self, noRefresh=False):

        count = self.GetItemCount()

        if self.HasFlag(ULC_ICON) and self._normal_image_list:
            iconSpacing = self._normal_spacing
        elif self.HasFlag(ULC_SMALL_ICON) and self._small_image_list:
            iconSpacing = self._small_spacing
        else:
            iconSpacing = 0

        # Note that we do not call GetClientSize() here but
        # GetSize() and subtract the border size for sunken
        # borders manually. This is technically incorrect,
        # but we need to know the client area's size WITHOUT
        # scrollbars here. Since we don't know if there are
        # any scrollbars, we use GetSize() instead. Another
        # solution would be to call SetScrollbars() here to
        # remove the scrollbars and call GetClientSize() then,
        # but this might result in flicker and - worse - will
        # reset the scrollbars to 0 which is not good at all
        # if you resize a dialog/window, but don't want to
        # reset the window scrolling. RR.
        # Furthermore, we actually do NOT subtract the border
        # width as 2 pixels is just the extra space which we
        # need around the actual content in the window. Other-
        # wise the text would e.g. touch the upper border. RR.
        clientWidth, clientHeight = self.GetSize()

        if self.InReportView():

            self.ResetVisibleLinesRange()

            if not self.HasExtraFlag(ULC_HAS_VARIABLE_ROW_HEIGHT):
                # all lines have the same height and we scroll one line per step

                lineHeight = self.GetLineHeight()
                entireHeight = count*lineHeight + LINE_SPACING
                decrement = 0
                if entireHeight > self.GetClientSize()[1]:
                    decrement = SCROLL_UNIT_X

                self._linesPerPage = clientHeight/lineHeight

                self.SetScrollbars(SCROLL_UNIT_X, lineHeight,
                                   (self.GetHeaderWidth()-decrement)/SCROLL_UNIT_X,
                                   (entireHeight + lineHeight - 1)/lineHeight,
                                   self.GetScrollPos(wx.HORIZONTAL),
                                   self.GetScrollPos(wx.VERTICAL),
                                   True)

            else:

                if count > 0:
                    entireHeight = self.GetLineY(count-1) + self.GetLineHeight(count-1) + LINE_SPACING
                    lineFrom, lineTo = self.GetVisibleLinesRange()
                    self._linesPerPage = lineTo - lineFrom + 1
                else:
                    lineHeight = self.GetLineHeight()
                    entireHeight = count*lineHeight + LINE_SPACING
                    self._linesPerPage = clientHeight/lineHeight

                decrement = 0
                if entireHeight > self.GetClientSize()[1]:
                    decrement = SCROLL_UNIT_X

                self.SetScrollbars(SCROLL_UNIT_X, SCROLL_UNIT_Y,
                                   (self.GetHeaderWidth()-decrement)/SCROLL_UNIT_X,
                                   (entireHeight + SCROLL_UNIT_Y - 1)/SCROLL_UNIT_Y,
                                   self.GetScrollPos(wx.HORIZONTAL),
                                   self.GetScrollPos(wx.VERTICAL),
                                   True)

        else: # !report

            dc = wx.ClientDC(self)
            dc.SetFont(self.GetFont())

            lineHeight = self.GetLineHeight()

            # we have 3 different layout strategies: either layout all items
            # horizontally/vertically (ULC_ALIGN_XXX styles explicitly given) or
            # to arrange them in top to bottom, left to right (don't ask me why
            # not the other way round...) order
            if self.HasFlag(ULC_ALIGN_LEFT | ULC_ALIGN_TOP):

                x = EXTRA_BORDER_X
                y = EXTRA_BORDER_Y
                widthMax = 0

                for i in xrange(count):

                    line = self.GetLine(i)
                    line.CalculateSize(dc, iconSpacing)
                    line.SetPosition(x, y, iconSpacing)

                    sizeLine = self.GetLineSize(i)

                    if self.HasFlag(ULC_ALIGN_TOP):

                        if sizeLine.x > widthMax:
                            widthMax = sizeLine.x

                        y += sizeLine.y

                    else: # ULC_ALIGN_LEFT

                        x += sizeLine.x + MARGIN_BETWEEN_ROWS

                if self.HasFlag(ULC_ALIGN_TOP):

                    # traverse the items again and tweak their sizes so that they are
                    # all the same in a row
                    for i in xrange(count):

                        line = self.GetLine(i)
                        line._gi.ExtendWidth(widthMax)

                self.SetScrollbars(SCROLL_UNIT_X, lineHeight,
                                   (x + SCROLL_UNIT_X)/SCROLL_UNIT_X,
                                   (y + lineHeight)/lineHeight,
                                   self.GetScrollPos(wx.HORIZONTAL),
                                   self.GetScrollPos(wx.VERTICAL),
                                   True)

            else: # "flowed" arrangement, the most complicated case

                # at first we try without any scrollbars, if the items don't fit into
                # the window, we recalculate after subtracting the space taken by the
                # scrollbar

                entireWidth = 0

                for tries in xrange(2):

                    entireWidth = 2*EXTRA_BORDER_X

                    if tries == 1:

                        # Now we have decided that the items do not fit into the
                        # client area, so we need a scrollbar
                        entireWidth += SCROLL_UNIT_X

                    x = EXTRA_BORDER_X
                    y = EXTRA_BORDER_Y
                    maxWidthInThisRow = 0

                    self._linesPerPage = 0
                    currentlyVisibleLines = 0

                    for i in xrange(count):

                        currentlyVisibleLines += 1
                        line = self.GetLine(i)
                        line.CalculateSize(dc, iconSpacing)
                        line.SetPosition(x, y, iconSpacing)

                        sizeLine = self.GetLineSize(i)

                        if maxWidthInThisRow < sizeLine.x:
                            maxWidthInThisRow = sizeLine.x

                        y += sizeLine.y
                        if currentlyVisibleLines > self._linesPerPage:
                            self._linesPerPage = currentlyVisibleLines

                        if y + sizeLine.y >= clientHeight:

                            currentlyVisibleLines = 0
                            y = EXTRA_BORDER_Y
                            maxWidthInThisRow += MARGIN_BETWEEN_ROWS
                            x += maxWidthInThisRow
                            entireWidth += maxWidthInThisRow
                            maxWidthInThisRow = 0

                        # We have reached the last item.
                        if i == count - 1:
                            entireWidth += maxWidthInThisRow

                        if tries == 0 and entireWidth + SCROLL_UNIT_X > clientWidth:
                            clientHeight -= wx.SystemSettings.GetMetric(wx.SYS_HSCROLL_Y)
                            self._linesPerPage = 0
                            break

                        if i == count - 1:
                            break  # Everything fits, no second try required.

                self.SetScrollbars(SCROLL_UNIT_X, lineHeight,
                                   (entireWidth + SCROLL_UNIT_X)/SCROLL_UNIT_X,
                                   0,
                                   self.GetScrollPos(wx.HORIZONTAL),
                                   0,
                                   True)

        self._dirty = False
        if not noRefresh:
            # FIXME: why should we call it from here?
            self.UpdateCurrent()
            self.RefreshAll()


    def RefreshAll(self):

        self._dirty = False
        self.Refresh()

        headerWin = self.GetListCtrl()._headerWin
        if headerWin and headerWin._dirty:
            headerWin._dirty = False
            headerWin.Refresh()


    def UpdateCurrent(self):

        if not self.HasCurrent() and not self.IsEmpty():
            self.ChangeCurrent(0)


    def GetNextItem(self, item, geometry=ULC_NEXT_ALL, state=ULC_STATE_DONTCARE):

        ret = item
        maxI = self.GetItemCount()

        # notice that we start with the next item (or the first one if item == -1)
        # and this is intentional to allow writing a simple loop to iterate over
        # all selected items
        ret += 1

        if ret == maxI:
            # this is not an error because the index was ok initially, just no
            # such item
            return -1

        if not state:
            # any will do
            return ret

        for line in xrange(ret, maxI):
            if state & ULC_STATE_FOCUSED and line == self._current:
                return line

            if state & ULC_STATE_SELECTED and self.IsHighlighted(line):
                return line

        return -1


# ----------------------------------------------------------------------------
# deleting stuff
# ----------------------------------------------------------------------------

    def DeleteItem(self, lindex):

        count = self.GetItemCount()
        if lindex < 0 or lindex >= self.GetItemCount():
            raise Exception("invalid item index in DeleteItem")

        # we don't need to adjust the index for the previous items
        if self.HasCurrent() and self._current >= lindex:

            # if the current item is being deleted, we want the next one to
            # become selected - unless there is no next one - so don't adjust
            # self._current in this case
            if self._current != lindex or self._current == count - 1:
                self._current -= 1

        if self.InReportView():

            #  mark the Column Max Width cache as dirty if the items in the line
            #  we're deleting contain the Max Column Width
            line = self.GetLine(lindex)
            item = UltimateListItem()

            for i in xrange(len(self._columns)):
                itemData = line._items[i]
                item = itemData.GetItem(item)
                itemWidth = self.GetItemWidthWithImage(item)

                if itemWidth >= self._aColWidths[i]._nMaxWidth:
                    self._aColWidths[i]._bNeedsUpdate = True

                if item.GetWindow():
                    self.DeleteItemWindow(item)

            self.ResetVisibleLinesRange(True)
            self._current = -1

        self.SendNotify(lindex, wxEVT_COMMAND_LIST_DELETE_ITEM)

        if self.IsVirtual():
            self._countVirt -= 1
            self._selStore.OnItemDelete(lindex)

        else:
            self._lines.pop(lindex)

        # we need to refresh the (vert) scrollbar as the number of items changed
        self._dirty = True
        self._lineHeight = 0
        self.ResetLineDimensions(True)
        self.RecalculatePositions()
        self.RefreshAfter(lindex)


    def DeleteColumn(self, col):

        self._columns.pop(col)
        self._dirty = True

        if not self.IsVirtual():
            # update all the items
            for i in xrange(len(self._lines)):
                line = self.GetLine(i)
                line._items.pop(col)

        if self.InReportView():   #  we only cache max widths when in Report View
            self._aColWidths.pop(col)

        # invalidate it as it has to be recalculated
        self._headerWidth = 0


    def DoDeleteAllItems(self):

        if self.IsEmpty():
            # nothing to do - in particular, don't send the event
            return

        self.ResetCurrent()

        # to make the deletion of all items faster, we don't send the
        # notifications for each item deletion in this case but only one event
        # for all of them: this is compatible with wxMSW and documented in
        # DeleteAllItems() description

        event = UltimateListEvent(wxEVT_COMMAND_LIST_DELETE_ALL_ITEMS, self.GetParent().GetId())
        event.SetEventObject(self.GetParent())
        self.GetParent().GetEventHandler().ProcessEvent(event)

        if self.IsVirtual():
            self._countVirt = 0
            self._selStore.Clear()

        if self.InReportView():
            self.ResetVisibleLinesRange(True)
            for i in xrange(len(self._aColWidths)):
                self._aColWidths[i]._bNeedsUpdate = True

        for item in self._itemWithWindow:
            wnd = item.GetWindow()
            wnd.Destroy()

        self._lines = []
        self._itemWithWindow = []
        self._hasWindows = False


    def DeleteAllItems(self):

        self.DoDeleteAllItems()
        self.RecalculatePositions()


    def DeleteEverything(self):

        self._columns = []
        self._aColWidths = []

        self.DeleteAllItems()


# ----------------------------------------------------------------------------
# scanning for an item
# ----------------------------------------------------------------------------

    def EnsureVisible(self, index):

        if index < 0 or index >= self.GetItemCount():
            raise Exception("invalid item index in EnsureVisible")

        # We have to call this here because the label in question might just have
        # been added and its position is not known yet
        if self._dirty:
            self.RecalculatePositions(True)

        self.MoveToItem(index)


    def FindItem(self, start, string, partial=False):

        if start < 0:
            start = 0

        str_upper = string.upper()
        count = self.GetItemCount()

        for i in xrange(start, count):
            line = self.GetLine(i)
            text = line.GetText(0)
            line_upper = text.upper()
            if not partial:
                if line_upper == str_upper:
                    return i
            else:
                if line_upper.find(str_upper) == 0:
                    return i

        return wx.NOT_FOUND


    def FindItemData(self, start, data):

        if start < 0:
            start = 0

        count = self.GetItemCount()

        for i in xrange(start, count):
            line = self.GetLine(i)
            item = UltimateListItem()
            item = line.GetItem(0, item)

            if item._data == data:
                return i

        return wx.NOT_FOUND


    def FindItemAtPos(self, pt):

        topItem, dummy = self.GetVisibleLinesRange()
        p = self.GetItemPosition(self.GetItemCount()-1)

        if p.y == 0:
            return topItem

        id = int(math.floor(pt.y*float(self.GetItemCount()-topItem-1)/p.y+topItem))

        if id >= 0 and id < self.GetItemCount():
            return id

        return wx.NOT_FOUND


    def HitTest(self, x, y):

        x, y = self.CalcUnscrolledPosition(x, y)
        count = self.GetItemCount()

        if self.InReportView():
            if not self.HasExtraFlag(ULC_HAS_VARIABLE_ROW_HEIGHT):
                current = y/self.GetLineHeight()
                if current < count:
                    newItem, flags = self.HitTestLine(current, x, y)
                    if flags:
                        return current, flags
            else:
                for current in xrange(self._lineFrom, count):
                    newItem, flags = self.HitTestLine(current, x, y)
                    if flags:
                        return current, flags

        else:
            # TODO: optimize it too! this is less simple than for report view but
            #       enumerating all items is still not a way to do it!!
            for current in xrange(count):
                newItem, flags = self.HitTestLine(current, x, y)
                if flags:
                    return current, flags

        return wx.NOT_FOUND, None


# ----------------------------------------------------------------------------
# adding stuff
# ----------------------------------------------------------------------------

    def InsertItem(self, item):

        if self.IsVirtual():
            raise Exception("can't be used with virtual control")

        count = self.GetItemCount()
        if item._itemId < 0:
            raise Exception("invalid item index")

        CheckVariableRowHeight(self, item._text)

        if item._itemId > count:
            item._itemId = count

        id = item._itemId
        self._dirty = True

        if self.InReportView():
            self.ResetVisibleLinesRange(True)

            # calculate the width of the item and adjust the max column width
            pWidthInfo = self._aColWidths[item.GetColumn()]
            width = self.GetItemWidthWithImage(item)
            item.SetWidth(width)

            if width > pWidthInfo._nMaxWidth:
                pWidthInfo._nMaxWidth = width

        line = UltimateListLineData(self)
        line.SetItem(item._col, item)

        self._lines.insert(id, line)
        self._dirty = True

        # If an item is selected at or below the point of insertion, we need to
        # increment the member variables because the current row's index has gone
        # up by one
        if self.HasCurrent() and self._current >= id:
            self._current += 1

        self.SendNotify(id, wxEVT_COMMAND_LIST_INSERT_ITEM)
        self.RefreshLines(id, self.GetItemCount() - 1)


    def InsertColumn(self, col, item):

        self._dirty = True

        if self.InReportView() or self.InTileView() or self.HasExtraFlag(ULC_HEADER_IN_ALL_VIEWS):

            if item._width == ULC_AUTOSIZE_USEHEADER:
                item._width = self.GetTextLength(item._text)

            column = UltimateListHeaderData(item)
            colWidthInfo = ColWidthInfo()

            insert = (col >= 0) and (col < len(self._columns))

            if insert:
                self._columns.insert(col, column)
                self._aColWidths.insert(col, colWidthInfo)

            else:

                self._columns.append(column)
                self._aColWidths.append(colWidthInfo)

            if not self.IsVirtual():

                # update all the items
                for i in xrange(len(self._lines)):
                    line = self.GetLine(i)
                    data = UltimateListItemData(self)
                    if insert:
                        line._items.insert(col, data)
                    else:
                        line._items.append(data)

            # invalidate it as it has to be recalculated
            self._headerWidth = 0


    def GetItemWidthWithImage(self, item):

        if item.GetCustomRenderer():
            return item.GetCustomRenderer().GetSubItemWidth()

        width = 0
        dc = wx.ClientDC(self)

        if item.GetFont().IsOk():
            font = item.GetFont()
        else:
            font = self.GetFont()

        dc.SetFont(font)

        if item.GetKind() in [1, 2]:
            ix, iy = self.GetCheckboxImageSize()
            width += ix

        if item.GetImage():
            ix, iy = self.GetImageSize(item.GetImage())
            width += ix + IMAGE_MARGIN_IN_REPORT_MODE

        if item.GetText():
            w, h, dummy = dc.GetMultiLineTextExtent(item.GetText())
            width += w

        if item.GetWindow():
            width += item._windowsize.x + 5

        return width


    def GetItemTextSize(self, item):

        width = ix = iy = start = end = 0
        dc = wx.ClientDC(self)

        if item.HasFont():
            font = item.GetFont()
        else:
            font = self.GetFont()

        dc.SetFont(font)

        if item.GetKind() in [1, 2]:
            ix, iy = self.GetCheckboxImageSize()
            start += ix

        if item.GetImage():
            ix, iy = self.GetImageSize(item.GetImage())
            start += ix + IMAGE_MARGIN_IN_REPORT_MODE

        if item.GetText():
            w, h, dummy = dc.GetMultiLineTextExtent(item.GetText())
            end = w

        return start, end


# ----------------------------------------------------------------------------
# sorting
# ----------------------------------------------------------------------------

    def OnCompareItems(self, line1, line2):
        """
        Override this function in the derived class to change the sort order of the items
        in the UltimateListCtrl. The function should return a negative, zero or positive
        value if the first item is less than, equal to or greater than the second one.

        The base class version compares items by their index.
        """

        item = UltimateListItem()
        item1 = line1.GetItem(0, item)
        item = UltimateListItem()
        item2 = line2.GetItem(0, item)

        data1 = item1._data
        data2 = item2._data

        if self.__func:
            return self.__func(data1, data2)
        else:
            return cmp(data1, data2)


    def SortItems(self, func):

        self.HighlightAll(False)
        self.ResetCurrent()

        if self._hasWindows:
            self.HideWindows()

        if not func:
            self.__func = None
            self._lines.sort(self.OnCompareItems)
        else:
            self.__func = func
            self._lines.sort(self.OnCompareItems)

        if self.IsShownOnScreen():
            self._dirty = True
            self._lineHeight = 0
            self.ResetLineDimensions(True)

        self.RecalculatePositions(True)


# ----------------------------------------------------------------------------
# scrolling
# ----------------------------------------------------------------------------

    def OnScroll(self, event):

        event.Skip()

        # update our idea of which lines are shown when we redraw the window the
        # next time
        self.ResetVisibleLinesRange()

        if self.HasExtraFlag(ULC_HAS_VARIABLE_ROW_HEIGHT):
            wx.CallAfter(self.RecalculatePositions, True)

        if event.GetOrientation() == wx.HORIZONTAL:
            lc = self.GetListCtrl()

            if self.HasHeader():
                lc._headerWin.Refresh()
                lc._headerWin.Update()

            if self.HasFooter():
                lc._footerWin.Refresh()
                lc._footerWin.Update()


    def GetCountPerPage(self):

        if not self.HasExtraFlag(ULC_HAS_VARIABLE_ROW_HEIGHT):
            if not self._linesPerPage:
                self._linesPerPage = self.GetClientSize().y/self.GetLineHeight()

            return self._linesPerPage

        visibleFrom, visibleTo = self.GetVisibleLinesRange()
        self._linesPerPage = visibleTo - visibleFrom + 1

        return self._linesPerPage


    def GetVisibleLinesRange(self):

        if not self.InReportView():
            raise Exception("this is for report mode only")

        if self._lineFrom == -1:

            count = self.GetItemCount()

            if count:

                if self.HasExtraFlag(ULC_HAS_VARIABLE_ROW_HEIGHT):

                    view_x, view_y = self.GetViewStart()
                    view_y *= SCROLL_UNIT_Y

                    for i in xrange(0, count):
                        rc = self.GetLineY(i)
                        if rc > view_y:
                            self._lineFrom = i - 1
                            break

                    if self._lineFrom < 0:
                        self._lineFrom = 0

                    self._lineTo = self._lineFrom
                    clientWidth, clientHeight = self.GetClientSize()

                    for i in xrange(self._lineFrom, count):
                        rc = self.GetLineY(i) + self.GetLineHeight(i)
                        if rc > view_y + clientHeight - 5:
                            break
                        self._lineTo += 1

                else:

                    # No variable row height
                    self._lineFrom = self.GetScrollPos(wx.VERTICAL)

                    # this may happen if SetScrollbars() hadn't been called yet
                    if self._lineFrom >= count:
                        self._lineFrom = count - 1

                    self._lineTo = self._lineFrom + self._linesPerPage

                # we redraw one extra line but this is needed to make the redrawing
                # logic work when there is a fractional number of lines on screen
                if self._lineTo >= count:
                    self._lineTo = count - 1

            else: # empty control

                self._lineFrom = -1
                self._lineTo = -1

        return self._lineFrom, self._lineTo


    def ResetTextControl(self):
        """Called by UltimateListTextCtrl when it marks itself for deletion."""

        self._textctrl.Destroy()
        self._textctrl = None

        self.RecalculatePositions()
        self.Refresh()


    def SetFirstGradientColour(self, colour=None):
        """Sets the first gradient colour."""

        if colour is None:
            colour = wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHT)

        self._firstcolour = colour
        if self._usegradients:
            self.RefreshSelected()


    def SetSecondGradientColour(self, colour=None):
        """Sets the second gradient colour."""

        if colour is None:
            # No colour given, generate a slightly darker from the
            # UltimateListCtrl background colour
            colour = self.GetBackgroundColour()
            r, g, b = int(colour.Red()), int(colour.Green()), int(colour.Blue())
            colour = ((r >> 1) + 20, (g >> 1) + 20, (b >> 1) + 20)
            colour = wx.Colour(colour[0], colour[1], colour[2])

        self._secondcolour = colour

        if self._usegradients:
            self.RefreshSelected()


    def GetFirstGradientColour(self):
        """Returns the first gradient colour."""

        return self._firstcolour


    def GetSecondGradientColour(self):
        """Returns the second gradient colour."""

        return self._secondcolour


    def EnableSelectionGradient(self, enable=True):
        """Globally enables/disables drawing of gradient selection."""

        self._usegradients = enable
        self._vistaselection = False
        self.RefreshSelected()


    def SetGradientStyle(self, vertical=0):
        """
        Sets the gradient style:
        0: horizontal gradient
        1: vertical gradient
        """

        # 0 = Horizontal, 1 = Vertical
        self._gradientstyle = vertical

        if self._usegradients:
            self.RefreshSelected()


    def GetGradientStyle(self):
        """
        Returns the gradient style:
        0: horizontal gradient
        1: vertical gradient
        """

        return self._gradientstyle


    def EnableSelectionVista(self, enable=True):
        """Globally enables/disables drawing of Windows Vista selection."""

        self._usegradients = False
        self._vistaselection = enable
        self.RefreshSelected()


    def SetBackgroundImage(self, image):
        """Sets the UltimateListCtrl background image (can be None)."""

        self._backgroundImage = image
        self.Refresh()


    def GetBackgroundImage(self):
        """Returns the UltimateListCtrl background image (can be None)."""

        return self._backgroundImage


    def SetWaterMark(self, watermark):
        """Sets the UltimateListCtrl watermark image (can be None)."""

        self._waterMark = watermark
        self.Refresh()


    def GetWaterMark(self):
        """Returns the UltimateListCtrl watermark image (can be None)."""

        return self._waterMark


    def SetDisabledTextColour(self, colour):
        """Sets the items disabled colour."""

        # Disabled items colour
        self._disabledColour = colour
        self.Refresh()


    def GetDisabledTextColour(self):
        """Returns the items disabled colour."""

        return self._disabledColour


    def ScrollList(self, dx, dy):

        if not self.InReportView():
            # TODO: this should work in all views but is not implemented now
            return False

        top, bottom = self.GetVisibleLinesRange()

        if bottom == -1:
            return 0

        self.ResetVisibleLinesRange()

        if not self.HasExtraFlag(ULC_HAS_VARIABLE_ROW_HEIGHT):
            hLine = self.GetLineHeight()
            self.Scroll(-1, top + dy/hLine)
        else:
            self.Scroll(-1, top + dy/SCROLL_UNIT_Y)

        if wx.Platform == "__WXMAC__":
            # see comment in MoveToItem() for why we do this
            self.ResetVisibleLinesRange()

        return True

# -------------------------------------------------------------------------------------
# UltimateListCtrl
# -------------------------------------------------------------------------------------

class UltimateListCtrl(wx.PyControl):

    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=0, extraStyle=0, validator=wx.DefaultValidator, name="UltimateListCtrl"):

        self._imageListNormal = None
        self._imageListSmall = None
        self._imageListState = None

        if not style & ULC_MASK_TYPE:
            raise Exception("UltimateListCtrl style should have exactly one mode bit set")

        if not (style & ULC_REPORT) and extraStyle & ULC_HAS_VARIABLE_ROW_HEIGHT:
            raise Exception("Extra Style ULC_HAS_VARIABLE_ROW_HEIGHT can only be used in report, non-virtual mode")

        if extraStyle & ULC_STICKY_HIGHLIGHT and extraStyle & ULC_TRACK_SELECT:
            raise Exception("Extra styles ULC_STICKY_HIGHLIGHT and ULC_TRACK_SELECT can not be combined")

        if style & ULC_NO_HEADER and extraStyle & ULC_HEADER_IN_ALL_VIEWS:
            raise Exception("Style ULC_NO_HEADER and extra style ULC_HEADER_IN_ALL_VIEWS can not be combined")

        wx.PyControl.__init__(self, parent, id, pos, size, style|wx.CLIP_CHILDREN, validator, name)

        self._mainWin = None
        self._headerWin = None
        self._footerWin = None

        self._headerHeight = wx.RendererNative.Get().GetHeaderButtonHeight(self)
        self._footerHeight = self._headerHeight

        if wx.Platform == "__WXGTK__":
            style &= ~wx.BORDER_MASK
            style |= wx.BORDER_THEME
        else:
            if style & wx.BORDER_THEME:
                style -= wx.BORDER_THEME

        self._extraStyle = extraStyle
        if style & wx.SUNKEN_BORDER:
            style -= wx.SUNKEN_BORDER

        self._mainWin = UltimateListMainWindow(self, wx.ID_ANY, wx.Point(0, 0), size, style)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._mainWin, 1, wx.GROW)
        self.SetSizer(sizer)

        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.CreateOrDestroyHeaderWindowAsNeeded()
        self.CreateOrDestroyFooterWindowAsNeeded()

        self.SetInitialSize(size)
        wx.CallAfter(self.Layout)


    def CreateOrDestroyHeaderWindowAsNeeded(self):

        needs_header = self.HasHeader()
        has_header = self._headerWin is not None
        if needs_header == has_header:
            return

        if needs_header:

            self._headerWin = UltimateListHeaderWindow(self, wx.ID_ANY, self._mainWin,
                                                       wx.Point(0, 0),
                                                       wx.Size(self.GetClientSize().x, self._headerHeight),
                                                       wx.TAB_TRAVERSAL, isFooter=False)

            # ----------------------------------------------------
            # How do you translate all this blah-blah to wxPython?
            # ----------------------------------------------------
            #if defined( __WXMAC__ ) && wxOSX_USE_COCOA_OR_CARBON
            #        wxFont font
            #if wxOSX_USE_ATSU_TEXT
            #        font.MacCreateFromThemeFont( kThemeSmallSystemFont )
            #else
            #        font.MacCreateFromUIFont( kCTFontSystemFontType )
            #endif
            #        m_headerWin->SetFont( font )
            #endif

            self.GetSizer().Prepend(self._headerWin, 0, wx.GROW)

        else:

            self.GetSizer().Detach(self._headerWin)
            self._headerWin.Destroy()
            self._headerWin = None


    def CreateOrDestroyFooterWindowAsNeeded(self):

        needs_footer = self.HasFooter()
        has_footer = self._footerWin is not None
        if needs_footer == has_footer:
            return

        if needs_footer:

            self._footerWin = UltimateListHeaderWindow(self, wx.ID_ANY, self._mainWin,
                                                       wx.Point(0, 0),
                                                       wx.Size(self.GetClientSize().x, self._footerHeight),
                                                       wx.TAB_TRAVERSAL, isFooter=True)

            # ----------------------------------------------------
            # How do you translate all this blah-blah to wxPython?
            # ----------------------------------------------------
            #if defined( __WXMAC__ ) && wxOSX_USE_COCOA_OR_CARBON
            #        wxFont font
            #if wxOSX_USE_ATSU_TEXT
            #        font.MacCreateFromThemeFont( kThemeSmallSystemFont )
            #else
            #        font.MacCreateFromUIFont( kCTFontSystemFontType )
            #endif
            #        m_headerWin->SetFont( font )
            #endif

            self.GetSizer().Add(self._footerWin, 0, wx.GROW)

        else:

            self.GetSizer().Detach(self._footerWin)
            self._footerWin.Destroy()
            self._footerWin = None


    def HasHeader(self):

        return self._mainWin.HasHeader()


    def HasFooter(self):

        return self._mainWin.HasFooter()


    def GetDefaultBorder(self):

        return wx.BORDER_THEME


    def SetSingleStyle(self, style, add=True):

        if style & ULC_VIRTUAL:
            raise Exception("ULC_VIRTUAL can't be [un]set")

        flag = self.GetWindowStyle()

        if add:

            if style & ULC_MASK_TYPE:
                flag &= ~(ULC_MASK_TYPE | ULC_VIRTUAL)
            if style & ULC_MASK_ALIGN:
                flag &= ~ULC_MASK_ALIGN
            if style & ULC_MASK_SORT:
                flag &= ~ULC_MASK_SORT

        if add:
            flag |= style
        else:
            flag &= ~style

        # some styles can be set without recreating everything (as happens in
        # SetWindowStyleFlag() which calls ListMainWindow.DeleteEverything())
        if not style & ~(ULC_HRULES | ULC_VRULES):
            self.Refresh()
            wx.PyControl.SetWindowStyleFlag(self, flag)
        else:
            self.SetWindowStyleFlag(flag)


    def SetExtraStyle(self, style):

        if style & ULC_HAS_VARIABLE_ROW_HEIGHT and not self.HasFlag(ULC_REPORT):
            raise Exception("ULC_HAS_VARIABLE_ROW_HEIGHT extra style can be used only in report mode")

        self._extraStyle = style

        if style & ULC_HAS_VARIABLE_ROW_HEIGHT:
            self._mainWin.ResetLineDimensions()
            self._mainWin.ResetVisibleLinesRange()

        self.CreateOrDestroyFooterWindowAsNeeded()

        self.GetSizer().Layout()
        self.Refresh()


    def SetWindowStyleFlag(self, flag):

        if self._mainWin:

            self.CreateOrDestroyHeaderWindowAsNeeded()
            self.GetSizer().Layout()

        wx.PyControl.SetWindowStyleFlag(self, flag)


    def GetColumn(self, col):

        return self._mainWin.GetColumn(col)


    def SetColumn(self, col, item):

        self._mainWin.SetColumn(col, item)
        return True


    def GetColumnWidth(self, col):

        return self._mainWin.GetColumnWidth(col)


    def SetColumnWidth(self, col, width):

        self._mainWin.SetColumnWidth(col, width)
        return True


    def GetCountPerPage(self):

        return self._mainWin.GetCountPerPage()  # different from Windows ?


    def GetItem(self, itemOrId, col=0):

        item = CreateListItem(itemOrId, col)
        return self._mainWin.GetItem(item, col)


    def SetItem(self, info):

        self._mainWin.SetItem(info)
        return True


    def SetStringItem(self, index, col, label, imageIds=[], it_kind=0):

        info = UltimateListItem()
        info._text = label
        info._mask = ULC_MASK_TEXT

        if it_kind:
            info._mask |= ULC_MASK_KIND
            info._kind = it_kind

        info._itemId = index
        info._col = col

        for ids in to_list(imageIds):
            if ids > -1:
                info._image.append(ids)

        if info._image:
            info._mask |= ULC_MASK_IMAGE

        self._mainWin.SetItem(info)
        return index


    def GetItemState(self, item, stateMask):

        return self._mainWin.GetItemState(item, stateMask)


    def SetItemState(self, item, state, stateMask):

        self._mainWin.SetItemState(item, state, stateMask)
        return True


    def SetItemImage(self, item, image, selImage=-1):

        return self.SetItemColumnImage(item, 0, image)


    def SetItemColumnImage(self, item, column, image):

        info = UltimateListItem()
        info._image = to_list(image)
        info._mask = ULC_MASK_IMAGE
        info._itemId = item
        info._col = column
        self._mainWin.SetItem(info)

        return True


    def GetItemText(self, item):

        return self._mainWin.GetItemText(item)


    def SetItemText(self, item, str):

        self._mainWin.SetItemText(item, str)


    def GetItemData(self, item):

        info = UltimateListItem()
        info._mask = ULC_MASK_DATA
        info._itemId = item
        self._mainWin.GetItem(info)
        return info._data


    def SetItemData(self, item, data):

        info = UltimateListItem()
        info._mask = ULC_MASK_DATA
        info._itemId = item
        info._data = data
        self._mainWin.SetItem(info)
        return True


    def GetItemPyData(self, item):

        info = UltimateListItem()
        info._mask = ULC_MASK_PYDATA
        info._itemId = item
        self._mainWin.GetItem(info)
        return info._pyData


    def SetItemPyData(self, item, pyData):

        info = UltimateListItem()
        info._mask = ULC_MASK_PYDATA
        info._itemId = item
        info._pyData = pyData
        self._mainWin.SetItem(info)
        return True


    SetPyData = SetItemPyData
    GetPyData = GetItemPyData


    def GetViewRect(self):

        return self._mainWin.GetViewRect()


    def GetItemRect(self, item, code=ULC_RECT_BOUNDS):

        return self.GetSubItemRect(item, ULC_GETSUBITEMRECT_WHOLEITEM, code)


    def GetSubItemRect(self, item, subItem, code):

        rect = self._mainWin.GetSubItemRect(item, subItem)
        if self._mainWin.HasHeader():
            rect.y += self._headerHeight + 1

        return rect


    def GetItemPosition(self, item):

        return self._mainWin.GetItemPosition(item)


    def SetItemPosition(item, pos):

        return False


    def GetItemCount(self):

        return self._mainWin.GetItemCount()


    def GetColumnCount(self):

        return self._mainWin.GetColumnCount()


    def SetItemSpacing(self, spacing, isSmall=False):

        self._mainWin.SetItemSpacing(spacing, isSmall)


    def GetItemSpacing(self, isSmall=False):

        return self._mainWin.GetItemSpacing(isSmall)


    def SetItemTextColour(self, item, col):

        info = UltimateListItem()
        info._itemId = item
        info.SetTextColour(col)
        self._mainWin.SetItem(info)


    def GetItemTextColour(self, item):

        info = UltimateListItem()
        info._itemId = item
        info = self._mainWin.GetItem(info)

        return info.GetTextColour()


    def SetItemBackgroundColour(self, item, col):

        info = UltimateListItem()
        info._itemId = item
        info.SetBackgroundColour(col)
        self._mainWin.SetItem(info)


    def GetItemBackgroundColour(self, item):

        info = UltimateListItem()
        info._itemId = item
        info = self._mainWin.GetItem(info)
        return info.GetBackgroundColour()


    def SetItemFont(self, item, f):

        info = UltimateListItem()
        info._itemId = item
        info.SetFont(f)
        self._mainWin.SetItem(info)


    def GetItemFont(self, item):

        info = UltimateListItem()
        info._itemId = item
        info = self._mainWin.GetItem(info)
        return info.GetFont()


    def GetSelectedItemCount(self):

        return self._mainWin.GetSelectedItemCount()


    def GetTextColour(self):

        return self.GetForegroundColour()


    def SetTextColour(self, col):

        self.SetForegroundColour(col)


    def GetTopItem(self):

        top, dummy = self._mainWin.GetVisibleLinesRange()
        return top


    def GetNextItem(self, item, geometry=ULC_NEXT_ALL, state=ULC_STATE_DONTCARE):

        return self._mainWin.GetNextItem(item, geometry, state)


    def GetImageList(self, which):

        if which == wx.IMAGE_LIST_NORMAL:
            return self._imageListNormal

        elif which == wx.IMAGE_LIST_SMALL:
            return self._imageListSmall

        elif which == wx.IMAGE_LIST_STATE:
            return self._imageListState

        return None


    def SetImageList(self, imageList, which):

        if which == wx.IMAGE_LIST_NORMAL:
            self._imageListNormal = imageList

        elif which == wx.IMAGE_LIST_SMALL:
            self._imageListSmall = imageList

        elif which == wx.IMAGE_LIST_STATE:
            self._imageListState = imageList

        self._mainWin.SetImageList(imageList, which)


    def AssignImageList(self, imageList, which):

        self.SetImageList(imageList, which)


    def Arrange(self, flag):

        return 0


    def DeleteItem(self, item):

        self._mainWin.DeleteItem(item)
        return True


    def DeleteAllItems(self):

        self._mainWin.DeleteAllItems()
        return True


    def DeleteAllColumns(self):

        count = len(self._mainWin._columns)
        for n in xrange(count):
            self.DeleteColumn(0)

        return True


    def ClearAll(self):

        self._mainWin.DeleteEverything()


    def DeleteColumn(self, col):

        self._mainWin.DeleteColumn(col)
        return True


    def EditLabel(self, item):

        self._mainWin.EditLabel(item)


    def EnsureVisible(self, item):

        self._mainWin.EnsureVisible(item)
        return True


    def FindItem(self, start, str, partial=False):

        return self._mainWin.FindItem(start, str, partial)


    def FindItemData(self, start, data):

        return self._mainWin.FindItemData(start, data)


    def FindItemAtPos(self, start, pt, direction):

        return self._mainWin.FindItemAtPos(pt)


    def HitTest(self, pointOrTuple):

        if isinstance(pointOrTuple, wx.Point):
            x, y = pointOrTuple.x, pointOrTuple.y
        else:
            x, y = pointOrTuple

        return self._mainWin.HitTest(x, y)


    def InsertItem(self, info):

        self._mainWin.InsertItem(info)
        return info._itemId


    def InsertStringItem(self, index, label, it_kind=0):

        info = UltimateListItem()
        info._text = label
        info._mask = ULC_MASK_TEXT

        if it_kind:
            info._mask |= ULC_MASK_KIND
            info._kind = it_kind

        info._itemId = index
        return self.InsertItem(info)


    def InsertImageItem(self, index, imageIds, it_kind=0):

        info = UltimateListItem()
        info._mask = ULC_MASK_IMAGE

        if it_kind:
            info._mask |= ULC_MASK_KIND
            info._kind = it_kind

        info._image = to_list(imageIds)
        info._itemId = index

        return self.InsertItem(info)


    def InsertImageStringItem(self, index, label, imageIds, it_kind=0):

        info = UltimateListItem()
        info._text = label
        info._image = to_list(imageIds)
        info._mask = ULC_MASK_TEXT | ULC_MASK_IMAGE

        if it_kind:
            info._mask |= ULC_MASK_KIND
            info._kind = it_kind

        info._itemId = index
        return self.InsertItem(info)


    def InsertColumnInfo(self, col, item):

        if not self._mainWin.InReportView() and not self.HasExtraFlag(ULC_HEADER_IN_ALL_VIEWS) and \
           not self._mainWin.InTileView():
            raise Exception("Can't add column in non report/tile modes or without the ULC_HEADER_IN_ALL_VIEWS extra style set")

        self._mainWin.InsertColumn(col, item)
        if self._headerWin:
            self._headerWin.Refresh()

        return 0


    def InsertColumn(self, col, heading, format=ULC_FORMAT_LEFT, width=-1):

        item = UltimateListItem()
        item._mask = ULC_MASK_TEXT | ULC_MASK_FORMAT | ULC_MASK_FONT
        item._text = heading

        if width >= -2:
            item._mask |= ULC_MASK_WIDTH
            item._width = width

        item._format = format

        return self.InsertColumnInfo(col, item)


    def IsColumnShown(self, column):

        if self._headerWin:
            return self._mainWin.IsColumnShown(column)

        raise Exception("Showing/hiding columns works only with the header shown")


    def SetColumnShown(self, column, shown=True):

        col = self.GetColumn(column)
        col._mask |= ULC_MASK_SHOWN
        col.SetShown(shown)
        self._mainWin.SetColumn(column, col)
        self.Update()


    def ScrollList(self, dx, dy):

        return self._mainWin.ScrollList(dx, dy)


# Sort items.
# func is a function which takes 3 long arguments: item1, item2, data.
# The return value is a negative number if the first item should precede the second
# item, a positive number of the second item should precede the first,
# or zero if the two items are equivalent.

    def SortItems(self, func=None):

        self._mainWin.SortItems(func)

        return True


# ----------------------------------------------------------------------------
# event handlers
# ----------------------------------------------------------------------------

    def OnSize(self, event):

        if not self.IsShownOnScreen():
            return

        if not self._mainWin:
            return

        # We need to override OnSize so that our scrolled
        # window a) does call Layout() to use sizers for
        # positioning the controls but b) does not query
        # the sizer for their size and use that for setting
        # the scrollable area as set that ourselves by
        # calling SetScrollbar() further down.

        self.Layout()

        self._mainWin.ResetVisibleLinesRange(True)
        self._mainWin.RecalculatePositions()
        self._mainWin.AdjustScrollbars()

        if self._headerWin:
            self._headerWin.Refresh()

        if self._footerWin:
            self._footerWin.Refresh()


    def OnInternalIdle(self):

        wx.PyControl.OnInternalIdle(self)

        # do it only if needed
        if self._mainWin._dirty:
            self._mainWin._shortItems = []
            self._mainWin.RecalculatePositions()


# ----------------------------------------------------------------------------
# font/colours
# ----------------------------------------------------------------------------

    def SetBackgroundColour(self, colour):

        if self._mainWin:
            self._mainWin.SetBackgroundColour(colour)
            self._mainWin._dirty = True

        return True


    def SetForegroundColour(self, colour):

        if not wx.PyControl.SetForegroundColour(self, colour):
            return False

        if self._mainWin:
            self._mainWin.SetForegroundColour(colour)
            self._mainWin._dirty = True

        if self._headerWin:
            self._headerWin.SetForegroundColour(colour)

        return True


    def SetFont(self, font):

        if not wx.PyControl.SetFont(self, font):
            return False

        if self._mainWin:
            self._mainWin.SetFont(font)
            self._mainWin._dirty = True

        if self._headerWin:
            self._headerWin.SetFont(font)

        self.Refresh()

        return True


    def GetClassDefaultAttributes(self, variant):

        attr = wx.VisualAttributes()
        attr.colFg = wx.SystemSettings.GetColour(wx.SYS_COLOUR_LISTBOXTEXT)
        attr.colBg = wx.SystemSettings.GetColour(wx.SYS_COLOUR_LISTBOX)
        attr.font  = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        return attr


    def GetScrolledWin(self):

        return self._headerWin.GetOwner()


# ----------------------------------------------------------------------------
# methods forwarded to self._mainWin
# ----------------------------------------------------------------------------

    def SetDropTarget(self, dropTarget):

        self._mainWin.SetDropTarget(dropTarget)


    def GetDropTarget(self):

        return self._mainWin.GetDropTarget()


    def SetCursor(self, cursor):

        return (self._mainWin and [self._mainWin.SetCursor(cursor)] or [False])[0]


    def GetBackgroundColour(self):

        return (self._mainWin and [self._mainWin.GetBackgroundColour()] or [wx.NullColour])[0]


    def GetForegroundColour(self):

        return (self._mainWin and [self._mainWin.GetForegroundColour()] or [wx.NullColour])[0]


    def PopupMenu(self, menu, pos=wx.DefaultPosition):

        return self._mainWin.PopupMenu(menu, pos)


    def ClientToScreen(self, x, y):

        return self._mainWin.ClientToScreen(x, y)


    def ScreenToClient(self, x, y):

        return self._mainWin.ScreenToClient(x, y)


    def SetFocus(self):

        # The test in window.cpp fails as we are a composite
        # window, so it checks against "this", but not self._mainWin.
        if wx.Window.FindFocus() != self:
            self._mainWin.SetFocusIgnoringChildren()


    def DoGetBestSize(self):

        # Something is better than nothing...
        # 100x80 is what the MSW version will get from the default
        # wx.Control.DoGetBestSize
        return wx.Size(100, 80)


# ----------------------------------------------------------------------------
# virtual list control support
# ----------------------------------------------------------------------------

    def OnGetItemText(self, item, col):

        # this is a pure virtual function, in fact - which is not really pure
        # because the controls which are not virtual don't need to implement it
        raise Exception("UltimateListCtrl.OnGetItemText not supposed to be called")


    def OnGetItemImage(self, item):

        if self.GetImageList(wx.IMAGE_LIST_SMALL):
            raise Exception("List control has an image list, OnGetItemImage should be overridden.")

        return []


    def OnGetItemColumnImage(self, item, column=0):

        if column == 0:
            return self.OnGetItemImage(item)

        return []


    def OnGetItemAttr(self, item):

        if item < 0 or item > self.GetItemCount():
            raise Exception("Invalid item index in OnGetItemAttr()")

        # no attributes by default
        return None


    def OnGetItemCheck(self, item):

        return []


    def OnGetItemColumnCheck(self, item, column=0):

        if column == 0:
            return self.OnGetItemCheck(item)

        return []


    def OnGetItemKind(self, item):

        return 0


    def OnGetItemColumnKind(self, item, column=0):

        if column == 0:
            return self.OnGetItemKind(item)

        return 0


    def SetItemCount(self, count):

        if not self._mainWin.IsVirtual():
            raise Exception("This is for virtual controls only")

        self._mainWin.SetItemCount(count)


    def RefreshItem(self, item):

        self._mainWin.RefreshLine(item)


    def RefreshItems(self, itemFrom, itemTo):

        self._mainWin.RefreshLines(itemFrom, itemTo)


#
# Generic UltimateListCtrl is more or less a container for two other
# windows which drawings are done upon. These are namely
# 'self._headerWin' and 'self._mainWin'.
# Here we override 'virtual wxWindow::Refresh()' to mimic the
# behaviour UltimateListCtrl has under wxMSW.
#

    def Refresh(self, eraseBackground=True, rect=None):

        if not rect:

            # The easy case, no rectangle specified.
            if self._headerWin:
                self._headerWin.Refresh(eraseBackground)

            if self._mainWin:
                self._mainWin.Refresh(eraseBackground)

        else:

            # Refresh the header window
            if self._headerWin:

                rectHeader = self._headerWin.GetRect()
                rectHeader.Intersect(rect)
                if rectHeader.GetWidth() and rectHeader.GetHeight():
                    x, y = self._headerWin.GetPosition()
                    rectHeader.OffsetXY(-x, -y)
                    self._headerWin.Refresh(eraseBackground, rectHeader)

            # Refresh the main window
            if self._mainWin:

                rectMain = self._mainWin.GetRect()
                rectMain.Intersect(rect)
                if rectMain.GetWidth() and rectMain.GetHeight():
                    x, y = self._mainWin.GetPosition()
                    rectMain.OffsetXY(-x, -y)
                    self._mainWin.Refresh(eraseBackground, rectMain)


    def Update(self):

        self._mainWin.ResetVisibleLinesRange(True)
        wx.PyControl.Update(self)


    def GetEditControl(self):

        retval = None

        if self._mainWin:
            retval = self._mainWin.GetEditControl()

        return retval


    def Select(self, idx, on=1):
        '''[de]select an item'''

        item = CreateListItem(idx, 0)
        item = self._mainWin.GetItem(item, 0)
        if not item.IsEnabled():
            return

        if on:
            state = ULC_STATE_SELECTED
        else:
            state = 0


        self.SetItemState(idx, state, ULC_STATE_SELECTED)


    def Focus(self, idx):
        '''Focus and show the given item'''

        self.SetItemState(idx, ULC_STATE_FOCUSED, ULC_STATE_FOCUSED)
        self.EnsureVisible(idx)


    def GetFocusedItem(self):
        '''get the currently focused item or -1 if none'''
        return self.GetNextItem(-1, ULC_NEXT_ALL, ULC_STATE_FOCUSED)


    def GetFirstSelected(self, *args):
        '''return first selected item, or -1 when none'''
        return self.GetNextSelected(-1)


    def GetNextSelected(self, item):
        '''return subsequent selected items, or -1 when no more'''
        return self.GetNextItem(item, ULC_NEXT_ALL, ULC_STATE_SELECTED)


    def IsSelected(self, idx):
        '''return True if the item is selected'''
        return (self.GetItemState(idx, ULC_STATE_SELECTED) & ULC_STATE_SELECTED) != 0


    def IsItemChecked(self, itemOrId, col=0):

        item = CreateListItem(itemOrId, col)
        return self._mainWin.IsItemChecked(item)


    def IsItemEnabled(self, itemOrId, col=0):

        item = CreateListItem(itemOrId, col)
        return self._mainWin.IsItemEnabled(item)


    def GetItemKind(self, itemOrId, col=0):
        """
        Returns the item type:
        0: normal
        1: checkbox item
        2: radiobutton item
        """

        item = CreateListItem(itemOrId, col)
        return self._mainWin.GetItemKind(item)


    def SetItemKind(self, itemOrId, col=0, kind=0):

        item = CreateListItem(itemOrId, col)
        return self._mainWin.SetItemKind(item, kind)


    def EnableItem(self, itemOrId, col=0, enable=True):

        item = CreateListItem(itemOrId, col)
        return self._mainWin.EnableItem(item, enable)


    def IsItemHyperText(self, itemOrId, col=0):
        """Returns whether an item is hypertext or not."""

        item = CreateListItem(itemOrId, col)
        return self._mainWin.IsItemHyperText(item)


    def SetItemHyperText(self, itemOrId, col=0):
        """Returns whether an item is hypertext or not."""

        item = CreateListItem(itemOrId, col)
        return self._mainWin.SetItemHyperText(item)


    def SetColumnImage(self, col, image):
        item = self.GetColumn(col)
        # preserve all other attributes too

        item.SetMask(ULC_MASK_STATE      |
                     ULC_MASK_TEXT       |
                     ULC_MASK_IMAGE      |
                     ULC_MASK_DATA       |
                     ULC_SET_ITEM        |
                     ULC_MASK_WIDTH      |
                     ULC_MASK_FORMAT     |
                     ULC_MASK_FONTCOLOUR |
                     ULC_MASK_FONT       |
                     ULC_MASK_BACKCOLOUR |
                     ULC_MASK_KIND       |
                     ULC_MASK_CHECK
                     )
        item.SetImage(image)
        self.SetColumn(col, item)

    def ClearColumnImage(self, col):
        self.SetColumnImage(col, -1)

    def Append(self, entry):
        '''Append an item to the list control.  The entry parameter should be a
           sequence with an item for each column'''
        if len(entry):
            if wx.USE_UNICODE:
                cvtfunc = unicode
            else:
                cvtfunc = str
            pos = self.GetItemCount()
            self.InsertStringItem(pos, cvtfunc(entry[0]))
            for i in range(1, len(entry)):
                self.SetStringItem(pos, i, cvtfunc(entry[i]))
            return pos


    def SetFirstGradientColour(self, colour=None):
        """Sets the first gradient colour."""

        self._mainWin.SetFirstGradientColour(colour)


    def SetSecondGradientColour(self, colour=None):
        """Sets the second gradient colour."""

        self._mainWin.SetSecondGradientColour(colour)


    def GetFirstGradientColour(self):
        """Returns the first gradient colour."""

        return self._mainWin.GetFirstGradientColour()


    def GetSecondGradientColour(self):
        """Returns the second gradient colour."""

        return self._mainWin.GetSecondGradientColour()


    def EnableSelectionGradient(self, enable=True):
        """Globally enables/disables drawing of gradient selection."""

        self._mainWin.EnableSelectionGradient(enable)


    def SetGradientStyle(self, vertical=0):
        """
        Sets the gradient style:
        0: horizontal gradient
        1: vertical gradient
        """

        self._mainWin.SetGradientStyle(vertical)


    def GetGradientStyle(self):
        """
        Returns the gradient style:
        0: horizontal gradient
        1: vertical gradient
        """

        return self._mainWin.GetGradientStyle()


    def EnableSelectionVista(self, enable=True):
        """Globally enables/disables drawing of Windows Vista selection."""

        self._mainWin.EnableSelectionVista(enable)


    def SetBackgroundImage(self, image=None):
        """Sets the UltimateListCtrl background image (can be None)."""

        self._mainWin.SetBackgroundImage(image)


    def GetBackgroundImage(self):
        """Returns the UltimateListCtrl background image (can be None)."""

        return self._mainWin.GetBackgroundImage()


    def SetWaterMark(self, watermark=None):
        """Sets the UltimateListCtrl watermark image (can be None)."""

        self._mainWin.SetWaterMark(watermark)


    def GetWaterMark(self):
        """Returns the UltimateListCtrl watermark image (can be None)."""

        return self._mainWin.GetWaterMark()


    def SetDisabledTextColour(self, colour):
        """Sets the items disabled colour."""

        self._mainWin.SetDisabledTextColour(colour)


    def GetDisabledTextColour(self):
        """Returns the items disabled colour."""

        return self._mainWin.GetDisabledTextColour()


    def GetHyperTextFont(self):
        """Returns the font used to render an hypertext item."""

        return self._mainWin.GetHyperTextFont()


    def SetHyperTextFont(self, font):
        """Sets the font used to render an hypertext item."""

        self._mainWin.SetHyperTextFont(font)


    def SetHyperTextNewColour(self, colour):
        """Sets the colour used to render a non-visited hypertext item."""

        self._mainWin.SetHyperTextNewColour(colour)


    def GetHyperTextNewColour(self):
        """Returns the colour used to render a non-visited hypertext item."""

        return self._mainWin.GetHyperTextNewColour()


    def SetHyperTextVisitedColour(self, colour):
        """Sets the colour used to render a visited hypertext item."""

        self._mainWin.SetHyperTextVisitedColour(colour)


    def GetHyperTextVisitedColour(self):
        """Returns the colour used to render a visited hypertext item."""

        return self._mainWin.GetHyperTextVisitedColour()


    def SetItemVisited(self, itemOrId, col=0, visited=True):
        """Sets whether an hypertext item was visited."""

        item = CreateListItem(itemOrId, col)
        return self._mainWin.SetItemVisited(item, visited)


    def GetItemVisited(self, itemOrId, col=0):
        """Returns whether an hypertext item was visited."""

        item = CreateListItem(itemOrId, col)
        return self._mainWin.GetItemVisited(item)


    def GetItemWindow(self, itemOrId, col=0):
        """Returns the window associated to the item (if any)."""

        item = CreateListItem(itemOrId, col)
        return self._mainWin.GetItemWindow(item)


    def SetItemWindow(self, itemOrId, col=0, wnd=None, expand=False):
        """Sets the window for the given item"""

        item = CreateListItem(itemOrId, col)
        return self._mainWin.SetItemWindow(item, wnd, expand)


    def DeleteItemWindow(self, itemOrId, col=0):
        """Deletes the window associated to an item (if any). """

        item = CreateListItem(itemOrId, col)
        return self._mainWin.DeleteItemWindow(item)


    def GetItemWindowEnabled(self, itemOrId, col=0):
        """Returns whether the window associated to the item is enabled."""

        item = CreateListItem(itemOrId, col)
        return self._mainWin.GetItemWindowEnabled(item)


    def SetItemWindowEnabled(self, itemOrId, col=0, enable=True):
        """Enables/disables the window associated to the item."""

        item = CreateListItem(itemOrId, col)
        return self._mainWin.SetItemWindowEnabled(item, enable)


    def GetItemCustomRenderer(self, itemOrId, col=0):

        item = CreateListItem(itemOrId, col)
        return self._mainWin.GetItemCustomRenderer(item)


    def SetItemCustomRenderer(self, itemOrId, col=0, renderer=None):

        if not self.HasFlag(ULC_REPORT) or not self.HasExtraFlag(ULC_HAS_VARIABLE_ROW_HEIGHT):
            raise Exception("Custom renderers can be used on with style = ULC_REPORT and extraStyle = ULC_HAS_VARIABLE_ROW_HEIGHT")

        item = CreateListItem(itemOrId, col)
        return self._mainWin.SetItemCustomRenderer(item, renderer)


    def SetItemOverFlow(self, itemOrId, col=0, over=True):

        if not self.HasFlag(ULC_REPORT) or self._mainWin.IsVirtual():
            raise Exception("Overflowing items can be used only in report, non-virtual mode")

        item = CreateListItem(itemOrId, col)
        return self._mainWin.SetItemOverFlow(item, over)


    def GetItemOverFlow(self, itemOrId, col=0):

        item = CreateListItem(itemOrId, col)
        return self._mainWin.GetItemOverFlow(item)


    def HasExtraFlag(self, flag):

        return self._extraStyle & flag


    def IsVirtual(self):

        return self._mainWin.IsVirtual()

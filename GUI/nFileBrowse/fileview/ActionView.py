import os
from scene import *
from .FileViewWrapper import GenericNTP
from ..FBNodeLayer import TextLayer
from .. import themes


def view_actions(browser, cpath):
  return ActionView, ((browser, cpath), {}), 1


class ActionView (GenericNTP):
  
  def __init__(self, frame, browser, cpath):
    GenericNTP.__init__(self, frame)
    self.browser = browser
    self.cpath = cpath
    bcwd = browser.cwd
    bcwdbase = os.path.basename(bcwd)
    relpath = os.path.relpath(cpath, bcwd)
    _theme = themes.cur_theme()
    
    headf = TextLayer(relpath, (_theme._TITLE_ALT_FONT, 22))
    headf.frame.x = 4
    headfbg = Layer(Rect(0, frame.h-30, frame.w, 30))
    headfbg.background = _theme.NODE_BG_COLOR
    headfbg.add_layer(headf)
    self.add_layer(headfbg)
    
    headd = TextLayer(bcwdbase + os.sep, (_theme._TITLE_FONT, 22))
    headd.frame.x = 4
    headdbg = Layer(Rect(0, 120 if frame.h > 360 else 60, frame.w, 30))
    headdbg.background = _theme.NODE_BG_COLOR
    headdbg.add_layer(headd)
    self.add_layer(headdbg)


class GridLayout (Layer):
  
  pass

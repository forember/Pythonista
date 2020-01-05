from __future__ import division
from scene import *
from . import themes


def color_flash(layer, flash_color, normal_color=None):
  '''Set the background color of the layer to the flash color, then fade back to the normal color, which defaults to the current background color.'''
  if normal_color is None:
    normal_color = layer.background
  layer.background = flash_color
  layer.animate('background', normal_color)
  
  
def draw_loading(cx, cy):
  _theme = themes.cur_theme()
  fill(*_theme.LOADING_BG_COLOR)
  no_stroke()
  rect(cx - 128, cy - 128, 256, 256)
  tint(*_theme.LOADING_HILITE_TINT)
  text(_theme.LOADING_TEXT, *_theme.LOADING_FONT, x=cx, y=cy - 1)
  tint(*_theme.LOADING_TINT)
  text(_theme.LOADING_TEXT, *_theme.LOADING_FONT, x=cx, y=cy)

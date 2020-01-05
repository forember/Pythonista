from scene import Color
Font = lambda x, y: (x, y)


_black = lambda a=1: \
  Color(0, 0, 0, a)
  
_red = lambda a=1: \
  Color(0, 0, 0, a)
_green = lambda a=1: \
  Color(0, 0, 0, a)


_TITLE_ALT_FONT = 'AvenirNextCondensed-Bold'
_WIDE_FONT = 'AvenirNext-Heavy'


NFB_FONT = Font(_TITLE_ALT_FONT, 32)

LOADING_BG_COLOR = _black(0)
LOADING_TEXT = 'Loading'
LOADING_FONT = Font(_WIDE_FONT, 32)
LOADING_TINT = _red()
LOADING_HILITE_TINT = _black(0)

SCROLLBAR_BG_COLOR = _green()

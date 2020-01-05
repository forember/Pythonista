from ._default import *
from scene import Color
from ..scenefont import Font
from . import _utils


_black = lambda a=1: \
  Color(0, 0, 0, a)
_white = lambda a=1: \
  Color(1, 1, 1, a)
_grayf = lambda w, b, a=1: \
  _utils.wavg_color((w, _white(a)), (b, _black(a)))
_gray = lambda a=1: \
  _grayf(1, 1, a)
_dark_gray = lambda a=1: \
  _grayf(1, 3, a)
_light_gray = lambda a=1: \
  _grayf(4, 1, a)

_red = lambda a=1: \
  Color(1, 0.2, 0.2, a)
_dark_red = lambda a=1: \
  _utils.wavg_color((1, _red(a)), (4, _grayf(1, 7, a)))
_orange = lambda a=1: \
  Color(1, 0.45, 0.15, a)
_green = lambda a=1: \
  Color(0.15, 1, 0.3, a)
_blue = lambda a=1: \
  Color(0.15, 0.3, 1, a)
_dark_blue = lambda a=1: \
  _utils.wavg_color((1, _blue(a)), (3, _black(a)))
_navy_blue = lambda a=1: \
  _utils.wavg_color((1, _dark_blue(a)), (1, _black(a)))

_REGULAR_FONT = 'AvenirNext-Regular'
_MONO_FONT = 'DejaVuSansMono'
_MONO_ALT_FONT = 'Monofur'
_CONDENSED_FONT = 'AvenirNextCondensed-Regular'
_TITLE_FONT = 'AvenirNext-BoldItalic'
_TITLE_ALT_FONT = 'AvenirNextCondensed-Bold'
_WIDE_FONT = 'AvenirNext-Heavy'
_FANCY_FONT = 'SnellRoundhand-Black'

BG_COLOR = _black()

REFRESH_PULL_COLOR = _orange(0.75)
REFRESH_RELEASE_COLOR = _green(0.75)
REFRESH_IMG = 'Typicons96_Refresh'
REFRESH_TEXT_FONT = Font(_WIDE_FONT, 16)
REFRESH_TIME_FONT = Font(_TITLE_ALT_FONT, 16)
REFRESH_TINT = _white()
REFRESH_HILITE_TINT = _black()

LOADING_BG_COLOR = _dark_gray(0.5)
LOADING_TEXT = 'Loading'
LOADING_FONT = Font(_FANCY_FONT, 32)
LOADING_TINT = _dark_red()
LOADING_HILITE_TINT = _light_gray()

SCROLLBAR_BG_COLOR = _green()
END_STOP_BG_COLOR = _blue()

NODE_BG_COLOR = _dark_blue(0.5)
NODE_FAIL_BG_COLOR = _dark_red(0.75)
NODE_STROKE_COLOR = _green(0.25)
NODE_STROKE_WEIGHT = 2
NODE_TINT = _white()
NODE_FONT = Font(_REGULAR_FONT, 32)
NODE_CONDENSED_FONT = Font(_CONDENSED_FONT, 32)

NODE_ICON_START_BG = Color(*NODE_BG_COLOR)
NODE_ICON_TARGET_BG = _white(0)

PATH_BG_COLOR = _black(0.8)
PATH_FONT = Font(_TITLE_FONT, 32)
PATH_TINT = _gray()
PATH_HILITE_TINT = Color(*SCROLLBAR_BG_COLOR)


NTPL_BG_COLOR = _dark_red(0.5)
NTPL_ARROW_IMG = 'Typicons96_Next'
GENERIC_NTP_BG = _black()

IMAGE_VIEW_BG = _black()


TEXTPANE_BG = _navy_blue()
TEXTPANE_TINT = _white()

TEXTPANE_PAGED_LOAD = _red()
TEXTPANE_SCROLL_LOAD = _red(SCROLLBAR_BG_COLOR.a)
TEXTPANE_SCROLL_NORM = Color(*SCROLLBAR_BG_COLOR)
TEXTPANE_SCROLL_STROKE = Color(*SCROLLBAR_STROKE_COLOR)
TEXTPANE_SCROLL_STROKEW = SCROLLBAR_STROKE_WEIGHT


SOUND_IMG_TINT = _dark_blue()
SOUND_IMG = 'Typicons192_Music'

SOUND_BTN_BG = _white()
SOUND_BTN_BG_DOWN = _gray()
SOUND_BTN_STROKE = _light_gray()
SOUND_BTN_STROKEW = 4
SOUND_BTN_PLAY_COLOR = _dark_gray()
SOUND_BTN_PLAY_WEIGHT = 8
SOUND_BTN_PAUSE_COLOR = _dark_gray()

SOUND_SLIDER_BG = _light_gray()
SOUND_SLIDER_BG_STROKE = _gray()
SOUND_SLIDER_BG_STROKEW = 1
SOUND_SLIDER_FILL = _blue()
SOUND_SLIDER_FILL_STROKE = _gray(0.5)
SOUND_SLIDER_FILL_STROKEW = 1
SOUND_SLIDER_HANDLE_BG = _gray(0.5)
SOUND_SLIDER_HANDLE_STROKE = _white()
SOUND_SLIDER_HANDLE_STROKEW = 2

SOUND_TIME_FONT = Font(_MONO_ALT_FONT, 20)
SOUND_ETIME_TINT = _gray()
SOUND_RTIME_TINT = _gray()

SOUND_VOLUME_TEXT = 'Volume'
SOUND_VOLUME_FONT = Font(_MONO_ALT_FONT, 20)
SOUND_VOLUME_TINT = _dark_gray()

SOUND_TITLE_FONT = Font(_MONO_ALT_FONT, 28)
SOUND_TITLE_TINT = _white()

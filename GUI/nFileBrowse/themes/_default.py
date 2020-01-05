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

_red = lambda a=1: \
  Color(1, 0, 0, a)
_green = lambda a=1: \
  Color(0, 1, 0, a)
_blue = lambda a=1: \
  Color(0.15, 0.3, 1, a)

_REGULAR_FONT = 'AvenirNext-Regular'
_MONO_FONT = 'DejaVuSansMono'
_CONDENSED_FONT = 'AvenirNextCondensed-Regular'
_TITLE_FONT = 'AvenirNext-BoldItalic'
_TITLE_ALT_FONT = 'AvenirNextCondensed-Bold'
_WIDE_FONT = 'AvenirNext-Heavy'

BG_COLOR = _black()

REFRESH_PULL_COLOR = _red()
REFRESH_RELEASE_COLOR = _green()
REFRESH_IMG = 'Typicons96_Refresh'
REFRESH_PULL_TEXT = 'pull to refresh'
REFRESH_RELEASE_TEXT = 'release to refresh'
REFRESH_TIME_PREFIX = 'last refreshed: '
REFRESH_TEXT_FONT = Font(_WIDE_FONT, 16)
REFRESH_TIME_FONT = Font(_TITLE_ALT_FONT, 16)
REFRESH_TINT = _white()
REFRESH_HILITE_TINT = _black(0)

NFB_FONT = Font(_TITLE_ALT_FONT, 32)

LOADING_BG_COLOR = _black(0)
LOADING_TEXT = 'Loading'
LOADING_FONT = Font(_WIDE_FONT, 32)
LOADING_TINT = _red()
LOADING_HILITE_TINT = _black(0)

SCROLLBAR_BG_COLOR = _green()
SCROLLBAR_STROKE_COLOR = _white()
SCROLLBAR_STROKE_WEIGHT = 0
END_STOP_BG_COLOR = _red()

FPS_FONT = Font(_MONO_FONT, 24)

FILE_TEXT_FONT = Font(_MONO_FONT, 11)
FILE_PY_FONT = FILE_TEXT_FONT
FILE_READ_FONT = Font(_REGULAR_FONT, 12)
FILE_ERROR_FONT = FILE_TEXT_FONT
FILE_ERROR_TINT = _red()

NODE_BG_COLOR = _black(0)
NODE_FAIL_BG_COLOR = _red()
NODE_STROKE_COLOR = _white()
NODE_STROKE_WEIGHT = 0
NODE_TINT = _white()
NODE_FONT = Font(_REGULAR_FONT, 32)
NODE_CONDENSED_FONT = Font(_CONDENSED_FONT, 32)

NODE_ICON_START_BG = _black()
NODE_ICON_TARGET_BG = _white(0)
NODE_ICON_STROKE_COLOR = _black(0)
NODE_ICON_STROKE_WEIGHT = 0

FILE_ICON = _utils.load_app_img('FileOther.png')
PYFILE_ICON = _utils.load_app_img('FilePY.png')
FOLDER_ICON = _utils.load_app_img('Folder.png')
NOACCESS_ICON = 'Typicons96_Locked'
SYMLINK_BADGE = 'Typicons48_Back'
UPDIR_ICON = 'Typicons96_Up'

PATH_BG_COLOR = _black()
PATH_STROKE_COLOR = _black(0)
PATH_STROKE_WEIGHT = 0
PATH_FONT = Font(_TITLE_FONT, 32)
PATH_TINT = _white()
PATH_HILITE_TINT = _black(0)


NTPL_BG_COLOR = _black(0)
NTPL_FADE_TARGET = _black(0)
NTPL_ARROW_IMG = 'Typicons96_Next'
NTPL_ARROW_TINT = _white()
GENERIC_NTP_BG = _black()

IMAGE_VIEW_BG = _black()


TEXTPANE_BG = _black()
TEXTPANE_TINT = _white()
TEXTPANE_TEXT_X = 4

TEXTPANE_PAGED_LOAD = _red()
TEXTPANE_SCROLL_LOAD = _red(SCROLLBAR_BG_COLOR.a)
TEXTPANE_SCROLL_NORM = Color(*SCROLLBAR_BG_COLOR)
TEXTPANE_SCROLL_STROKE = Color(*SCROLLBAR_STROKE_COLOR)
TEXTPANE_SCROLL_STROKEW = SCROLLBAR_STROKE_WEIGHT


SOUND_BG = GENERIC_NTP_BG
SOUND_IMG_TINT = _white()
SOUND_IMG = 'Typicons192_Music'

SOUND_BTN_BG = _white()
SOUND_BTN_BG_DOWN = _gray()
SOUND_BTN_STROKE = _white()
SOUND_BTN_STROKEW = 0
SOUND_BTN_PLAY_COLOR = _black()
SOUND_BTN_PLAY_WEIGHT = 8
SOUND_BTN_PAUSE_COLOR = _black()

SOUND_SLIDER_BG = _white()
SOUND_SLIDER_BG_STROKE = _white()
SOUND_SLIDER_BG_STROKEW = 0
SOUND_SLIDER_FILL = _blue()
SOUND_SLIDER_FILL_STROKE = _white()
SOUND_SLIDER_FILL_STROKEW = 0
SOUND_SLIDER_HANDLE_BG = _gray()
SOUND_SLIDER_HANDLE_STROKE = _white()
SOUND_SLIDER_HANDLE_STROKEW = 0

SOUND_TIME_FONT = Font(_MONO_FONT, 20)
SOUND_ETIME_TINT = _white()
SOUND_RTIME_TINT = _white()

SOUND_VOLUME_TEXT = 'Volume'
SOUND_VOLUME_FONT = Font(_MONO_FONT, 20)
SOUND_VOLUME_TINT = _white()

SOUND_TITLE_FONT = Font(_MONO_FONT, 28)
SOUND_TITLE_TINT = _white()

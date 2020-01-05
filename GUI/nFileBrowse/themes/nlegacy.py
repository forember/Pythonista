from ._default import *
from scene import Color
from ..scenefont import Font

BG_COLOR = Color(0, 0, 0)

REFRESH_PULL_COLOR = Color(1, 0.45, 0.15, 0.75)
REFRESH_RELEASE_COLOR = Color(0.15, 0.9, 0.3, 0.75)
REFRESH_PULL_TEXT = 'pull to refresh'
REFRESH_RELEASE_TEXT = 'release to refresh'
REFRESH_TIME_PREFIX = 'last refreshed: '
REFRESH_TEXT_FONT = Font('AvenirNext-Heavy', 16)
REFRESH_TIME_FONT = Font('AvenirNextCondensed-Bold', 16)
REFRESH_TINT = Color(1, 1, 1)
REFRESH_HILITE_TINT = Color(0, 0, 0)

NFB_FONT = Font('AvenirNextCondensed-Bold', 32)

LOADING_BG_COLOR = Color(0.25, 0.25, 0.25, 0.48)
LOADING_TEXT = 'Loading'
LOADING_FONT = Font('SnellRoundhand-Black', 32)
LOADING_TINT = Color(0.22, 0.12, 0.12)
LOADING_HILITE_TINT = Color(0.8, 0.8, 0.8)

SCROLLBAR_BG_COLOR = Color(0.1, 0.9, 0.6)
SCROLLBAR_STROKE_COLOR = Color()
SCROLLBAR_STROKE_WEIGHT = 0
END_STOP_BG_COLOR = Color(0.2, 0.4, 0.8)

FPS_FONT = Font('Courier', 24)

FILE_TEXT_FONT = Font('Courier', 10)
FILE_PY_FONT = Font('DejaVuSansMono', 10)
FILE_READ_FONT = Font('AvenirNext-Regular', 12)
FILE_ERROR_FONT = FILE_TEXT_FONT

NODE_BG_COLOR = Color(0, 0, 0.2, 0.5)
NODE_FAIL_BG_COLOR = Color(1, 0, 0, 0.2)
NODE_STROKE_COLOR = Color(0.25, 0.85, 0.6, 0.25)
NODE_STROKE_WEIGHT = 2
NODE_TINT = Color(1, 1, 1)
NODE_FONT = Font('AvenirNext-Regular', 32)
NODE_CONDENSED_FONT = Font('AvenirNextCondensed-Regular', 32)

NODE_ICON_START_BG = Color(*NODE_BG_COLOR)
NODE_ICON_TARGET_BG = Color(1, 1, 1, 0)
NODE_ICON_STROKE_COLOR = Color()
NODE_ICON_STROKE_WEIGHT = 0

PATH_BG_COLOR = Color(0, 0, 0, 0.8)
PATH_STROKE_COLOR = Color()
PATH_STROKE_WEIGHT = 0
PATH_FONT = Font('AvenirNext-BoldItalic', 32)
PATH_TINT = Color(0.5, 0.5, 0.5)
PATH_HILITE_TINT = Color(*SCROLLBAR_BG_COLOR)


NTPL_BG_COLOR = Color(0.2, 0, 0, 0.5)
NTPL_FADE_TARGET = Color(0, 0, 0, 0)
NTPL_ARROW_TINT = Color(1, 1, 1)
GENERIC_NTP_BG = Color(0, 0, 0)

IMAGE_VIEW_BG = Color(0, 0, 0)


TEXTPANE_BG = Color(0, 0.01, 0.1)
TEXTPANE_TINT = Color(1, 1, 1)

TEXTPANE_PAGED_LOAD = Color(1, 0, 0)
TEXTPANE_SCROLL_LOAD = Color(1, 0, 0, 0.5)
TEXTPANE_SCROLL_NORM = Color(0.2, 0.5, 0.8, 0.5)
TEXTPANE_SCROLL_STROKE = Color(0.25, 0.25, 0.25, 0.75)
TEXTPANE_SCROLL_STROKEW = 0.5


SOUND_IMG_TINT = Color(0.25, 0.25, 0.3)
SOUND_IMG = 'Typicons192_Music'

SOUND_BTN_BG = Color(1, 1, 1)
SOUND_BTN_BG_DOWN = Color(1, 1, 1, 0.5)
SOUND_BTN_STROKE = Color()
SOUND_BTN_STROKEW = 0
SOUND_BTN_PLAY_COLOR = Color(0, 0, 0)
SOUND_BTN_PLAY_WEIGHT = 8
SOUND_BTN_PAUSE_COLOR = Color(0, 0, 0)

SOUND_SLIDER_BG = Color(1, 1, 1)
SOUND_SLIDER_BG_STROKE = Color()
SOUND_SLIDER_BG_STROKEW = 0
SOUND_SLIDER_FILL = Color(0, 0, 1, 0.75)
SOUND_SLIDER_FILL_STROKE = Color()
SOUND_SLIDER_FILL_STROKEW = 0
SOUND_SLIDER_HANDLE_BG = Color(0.75, 0.75, 0.75, 0.75)
SOUND_SLIDER_HANDLE_STROKE = Color()
SOUND_SLIDER_HANDLE_STROKEW = 0

SOUND_TIME_FONT = Font('Monofur', 20)
SOUND_ETIME_TINT = Color(1, 1, 1)
SOUND_RTIME_TINT = Color(1, 1, 1)

SOUND_VOLUME_TEXT = 'Volume'
SOUND_VOLUME_FONT = Font('Monofur', 20)
SOUND_VOLUME_TINT = Color(1, 1, 1)

SOUND_TITLE_FONT = Font('Monofur', 28)
SOUND_TITLE_TINT = Color(1, 1, 1)

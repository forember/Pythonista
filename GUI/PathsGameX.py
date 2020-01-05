import sys
# Pythonista 1.4
sys.modules.pop('PathsGame', None)

import traceback
sys.excepthook = traceback.print_exception

import PathsGame
PathsGame.main()

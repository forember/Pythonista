import sys
sys.dont_write_bytecode = False
# Pythonista 1.4
sys.modules.pop('nFileBrowse', None)

import traceback
sys.excepthook = traceback.print_exception

import nFileBrowse
#nFileBrowse._opts.theme_name = 'nnlegacy'
nFileBrowse.main()

if __name__ != 'PathsGame':
  raise ImportError

__all__ = ['InstallPathsGame', 'PathsMain']

import InstallPathsGame

def _set_path():
  import os
  absfile = os.path.abspath(__file__)
  pathsdir = os.path.dirname(absfile)
  pydir = os.path.join(pathsdir, 'py')
  pyzip = os.path.join(pathsdir, 'py.zip')
  global __path__
  __path__ = [pydir, pyzip]
_set_path()

def _clear_pathsgame_modules():
  import sys
  for name in sys.modules.keys():
    if name.startswith('PathsGame.'):
      del sys.modules[name]
_clear_pathsgame_modules()

def main():
  from . import PathsMain
  PathsMain.main()

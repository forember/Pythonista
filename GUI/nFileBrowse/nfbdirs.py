import os
from os.path import join

REAL_FILE = os.path.realpath(__file__)

PKG = os.path.dirname(REAL_FILE)
DYN = join(PKG, '--dyn')
CACHES = join(DYN, 'caches')
TREE_CACHE = join(CACHES, 'tree')

UHOME = os.path.expanduser('~')
DOCUMENTS = join(UHOME, 'Documents')
PYTHONISTA = join(UHOME, 'Pythonista.app')

_mkdir_list = [DYN, CACHES, TREE_CACHE]
def _mkdirs():
  for nfbdir in _mkdir_list:
    try:
      os.mkdir(nfbdir)
    except OSError:
      pass
_mkdirs()

def to_treepath(path, mk=True):
  treepath = os.path.join(TREE_CACHE, to_hexpath(path))
  if mk:
    try:
      dirname = os.path.dirname(treepath)
      os.makedirs(dirname)
    except OSError:
      pass
  return treepath
  
def from_treepath(treepath):
  return from_hexpath(os.path.relpath(treepath, TREE_CACHE))

hexsep = '-'

def to_hexpath(path, start=DOCUMENTS):
  path = os.path.abspath(path)
  path = os.path.relpath(path, start)
  hexpath = None
  while path:
    path, comp = os.path.split(path)
    hexcomp = comp.encode('hex')
    if hexpath is None:
      hexpath = hexcomp
    else:
      hexpath = join(hexcomp, hexpath)
  hexpath = os.path.normpath(hexpath)
  hexpath = hexpath.replace(os.sep, hexsep)
  return hexpath

def from_hexpath(hexpath, start=DOCUMENTS):
  hexpath = hexpath.replace(hexsep, os.sep)
  path = None
  while hexpath:
    hexpath, hexcomp = os.path.split(hexpath)
    comp = hexcomp.decode('hex')
    if path is None:
      path = comp
    else:
      path = join(comp, path)
  path = join(start, path)
  return path

# -*- coding: utf-8 -*-

import sys, os, shutil
from os import path
import cProfile, pstats
import scene
sys.modules.pop('FileBrowseLoad', None)
sys.modules.pop('nFileBrowse.' 'FileBrowseLoad', None)
from . import FileBrowseLoad
FileBrowseLoad.clear_nfb_sys_modules()
FileBrowseLoad._verbose = True
from . import FileBrowseOpts as _opts
_opts.theme_name = 'nnlegacy'
Fbls = FileBrowseLoad.FileBrowseLoadScene
from . import nfbdirs
FBPROF_DIR = path.join(nfbdirs.DYN, 'fbprof_tmp')
FBPROF_FILE = path.join(nfbdirs.DYN, 'fbprof.prof')

class Fbps (Fbls):
  def _draw(self, dt):
    filename = path.join(FBPROF_DIR, repr(self.t))
    cProfile.runctx('Fbls._draw(self, dt)', globals(), locals(), filename)
  
  def stop(self):
    FileBrowseLoad.clear_nfb_sys_modules()
    
def run():
  try: os.mkdir(nfbdirs.DYN)
  except OSError: pass
  try: os.remove(FBPROF_FILE)
  except OSError: pass
  try: shutil.rmtree(FBPROF_DIR)
  except OSError: pass
  try: os.mkdir(FBPROF_DIR)
  except OSError: pass
  scene.run(Fbps())

def process_results(force_refresh=False):
  if os.path.exists(FBPROF_FILE) and not force_refresh:
    return pstats.Stats(FBPROF_FILE)
  ls = os.listdir(FBPROF_DIR)
  stats = pstats.Stats(path.join(FBPROF_DIR, ls[0]))
  for node in ls[1:]:
    stats.add(path.join(FBPROF_DIR, node))
  stats.dump_stats(FBPROF_FILE)
  return stats

_printmethod = pstats.Stats.print_callees
def print_stats(stats, method=_printmethod):
  import console
  console.set_font('DejaVuSansMono', 6)
  method(stats)
  console.set_font()
  
def main(force_process=True, return_stats=False, force_refresh=False, do_print=True, sort='cumulative', printmethod=_printmethod):
  stats = None
  if (force_process or os.path.exists(FBPROF_DIR) and not os.path.exists(FBPROF_FILE)) and force_process != -1:
    stats = process_results(force_refresh)
    stats.strip_dirs()
    if sort:
      stats.sort_stats(sort)
    if do_print:
      print_stats(stats, printmethod)
  else:
    run()
  FileBrowseLoad.clear_nfb_sys_modules()
  if return_stats:
    return stats

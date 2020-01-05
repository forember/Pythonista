# -*- coding: utf-8 -*-

from __future__ import division

NFB_MODULE_NAMES = ['*']
# old list: update if you feel like it
#NFB_MODULE_NAMES = ['themes', 'themes.*', 'dsmap', 'fbdraw', 'FBNodeLayer', 'FileBrowse', 'FileBrowseLoadDefaultTheme', 'FileBrowseOpts', 'FileViewWrapper', 'ImageView', 'nfbdirs', 'scenefont', 'SceneLayer', 'SoundPlayer', 'TextPane', 'touchtracking', 'UnicodeBreakAfter']

def clear_nfb_sys_modules(defnmspc=False):
  # makes sure the script files are reloaded in Pythonista 1.4
  #smk = sys.modules.keys(); smk.sort(); print smk
  for modname in NFB_MODULE_NAMES:
    if modname.endswith('*'):
      modname = modname[:-1]
      nfbmodname = 'nFileBrowse.' + modname
      matches = []
      for modname2 in sys.modules:
        if modname2.startswith(nfbmodname) or (defnmspc and modname2.startswith(modname)):
          matches.append(modname2)
      for match in matches:
        #print match
        sys.modules.pop(match, None)
    if defnmspc:
      sys.modules.pop(modname, None)
    sys.modules.pop('nFileBrowse.' + modname, None)

import sys
# Pythonista 1.4
sys.modules.pop('scene', None)

from scene import *

_show_fps = False
_verbose = False

from . import FileBrowseLoadDefaultTheme as _theme

def _load_theme():
  global _theme
  from . import themes
  _theme = themes.cur_theme()

class FileBrowseLoadScene (Scene):
  preload_modules = ['collections', 'weakref', '.scenefont', '.themes', _load_theme, 'PIL', 'Image', '.nfbdirs']
  
  def setup(self):
    stages = []
    self.ipm = iter(self.preload_modules)
    from importlib import import_module
    def _import():
      module_name = self.ipm.next()
      if callable(module_name):
        module_name()
        return
      if _verbose: print module_name
      import_module(module_name, __package__)
    stages.extend([_import] * len(self.preload_modules))
    stages.extend(self.genlaststages())
    self.stage_ct = len(stages)
    self.stages = iter(stages)
    self.stage = 1
    
  def draw_loading(self):
    background(0, 0, 0)
    
    fill(*_theme.LOADING_BG_COLOR)
    no_stroke()
    cx, cy = self.bounds.center()
    rect(cx - 128, cy - 128, 256, 256)
    tint(*_theme.LOADING_HILITE_TINT)
    text(_theme.LOADING_TEXT, *_theme.LOADING_FONT, x=cx, y=cy - 1)
    tint(*_theme.LOADING_TINT)
    text(_theme.LOADING_TEXT, *_theme.LOADING_FONT, x=cx, y=cy)
    
    tint(*_theme.SCROLLBAR_BG_COLOR)
    text('nFileBrowse', *_theme.NFB_FONT, x=cx, y=cy + 63)
    no_tint()
    text('nFileBrowse', *_theme.NFB_FONT, x=cx, y=cy + 64)
    no_fill()
    stroke(*_theme.SCROLLBAR_BG_COLOR)
    stroke_weight(0.5)
    rect(cx-97.5, cy-49.5, 195, 11)
    fill(*_theme.LOADING_TINT)
    no_stroke()
    progress = ((self.stage-1) / self.stage_ct)
    rect(cx-96, cy-48, 192*progress, 8)
    
  def genlaststages(self):
    def f():
      if _verbose: print 'Image.init()'
      from PIL import Image
      Image.init()
    yield f
    def f():
      if _verbose: print 'pass'
      pass
    yield f
    def f():
      if _verbose: print '.FBNodeLayer'
      from . import FBNodeLayer
    yield f
    def f():
      if _verbose: print '.FileBrowse'
      from .FileBrowse import mk_file_browser
      self.mk_file_browser = mk_file_browser
    yield f
    def f():
      if _verbose: print 'mk_file_browser()'
      from . import FileBrowseOpts as _opts
      sfps = _show_fps if _opts._show_fps is None else _opts._show_fps
      self.file_browser = self.mk_file_browser(show_fps=sfps)
    yield f
    def f():
      if _verbose: print 'SceneLayer()'
      from .SceneLayer import SceneLayer
      self.root_layer = self.scene_layer = SceneLayer(self.file_browser, self.bounds)
    yield f
    def f():
      if _verbose: print 'load_ls_next()'
      self.file_browser.load_ls_next()
    yield f
    def f():
      if _verbose: print 'draw()'
      self.file_browser.draw()
    yield f
    
  def draw(self):
    if self.stage:
      self.draw_loading()
      self.stage += 1
      try:
        if _verbose:
          import time
          t = time.time()
        self.stages.next()()
        if _verbose:
          print ' ', time.time() - t
      except StopIteration:
        self.stage = 0
        del self.stages
    else:
      self.root_layer.frame = self.bounds
      self.root_layer.update(self.dt)
      self.root_layer.draw()
      
  def should_rotate(self, orientation):
    if hasattr(self, 'scene_layer'):
      return self.scene_layer.should_rotate(orientation)
    else:
      return True
      
  def pause(self):
    if hasattr(self, 'scene_layer'):
      return self.scene_layer.pause()
    
  def resume(self):
    if hasattr(self, 'scene_layer'):
      return self.scene_layer.resume()
    
  def stop(self):
    r = None
    if hasattr(self, 'scene_layer'):
      r = self.scene_layer.stop()
    # == Pythonista 1.4 ==
    #import sys
    sys.dont_write_bytecode = True
    #sys.modules.pop('sys', None)
    #import sys
    #sys._clear_type_cache()
    # ====================
    return r
    

def main():
  run(FileBrowseLoadScene())

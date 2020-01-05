# -*- coding: utf-8 -*-

from __future__ import division

import os, time
from scene import *

from . import nfbdirs
from . import FileBrowseOpts as _opts
from . import themes
from . import fbdraw
from . import FBNodeLayer
from . import touchtracking


class OldDirListError (Exception):
  pass



class FileBrowser (Scene):
  
  def should_rotate(self, orientation):
    return True
  
  # == Setup =============================
  
  def __init__(self, start_dir='/', show_fps=True):
    Scene.__init__(self)
    self.set_cwd(start_dir)
    self.show_fps = show_fps
    self.disp_y_over = 0
    self.velocity = 0
    self.long_operation = 0
    self.thumbresfactor = get_screen_scale()
    from weakref import WeakValueDictionary
    self.disp_layer_cache = WeakValueDictionary()
    self.cwd_dirty = True
    self.dtrn = 10
    self.draw_sub = None
    self.cur_iconl = None
    self.touchtracker = touchtracking.TouchTracker()
    # Pythonista 1.4
    self.do_setup = True
  
  
  def setup(self):
    # initalize dummy layers
    self.root_layer = Layer(self.bounds)
    self.disp_layer = Layer()
    self.path_layer = Layer()
    self.file_view = None
    
    # initialize a few more attributes
    self.prev_size = self.size
    # load the directory entries
    self.load_ls()
    
    # install the touch tracker
    self.touchtracker.install(self)
    # Pythonista 1.4
    self.do_setup = False
    
  # ======================================
  
  
  # == Updating ==========================
  
  def draw(self):
    # Pythonista 1.4
    if self.do_setup:
      self.setup()
    
    if self.draw_sub is not None:
      draw_sub = self.draw_sub
      self.draw_sub = None
      return draw_sub()
    
    # ensure that the root layer has the same bounds as the scene in case of rotation
    self.root_layer.frame = self.bounds
    # do scrolling kinetics
    self.do_scroll_kinetics()
    # pre-load resources (e.g. thumbnails)
    self.preload_resources()
    # rotation mechanism
    self.update_rotation()
    # draw the scene
    self.draw_scene()
    
    
  def preload_resources(self):
    disp = self.disp_layer
    if disp.next_preload < len(disp.items):
      speed = abs(self.velocity)
      dt = self.dt
      self.dtrn = (3*self.dtrn + dt*dt) / 4
      preload_det = speed*dt*self.dtrn
      detthres = 0.03125
      if preload_det < detthres:
        n = int(256 * (detthres - preload_det))
        disp.preload_icons(n)
  
  
  def update_rotation(self):
    # rotation mechanism compatible with older versions of Pythonista
    prev_size = self.prev_size
    self.prev_size = self.size
    if self.size != prev_size:
      self.reload_ls()
      self.correct_disp_bottom()
  
  # ======================================
  
  
  # == Drawing ===========================
  
  def draw_scene(self):
    _theme = themes.cur_theme()
    bg = _theme.BG_COLOR
    background(bg.r, bg.g, bg.b)
    self.root_layer.update(self.dt)
    self.root_layer.draw()
    self.draw_after_root()
      
      
  def draw_after_root(self):
    # draw loading panel
    if self.long_operation > 0:
      cx, cy = self.bounds.center()
      fbdraw.draw_loading(cx, cy)
    if self.long_operation <= 60:
      self.long_operation -= 1
    # draw scrollbar
    self.draw_scrollbar()
    # draw fps
    if self.show_fps:
      self.draw_fps()
  
  
  def draw_scrollbar(self):
    _theme = themes.cur_theme()
    sbbgc = Color(*_theme.SCROLLBAR_BG_COLOR)
    sbbgc.a *= abs(self.velocity)
    fill(*sbbgc)
    stroke(*_theme.SCROLLBAR_STROKE_COLOR)
    stroke_weight(min(abs(self.velocity), 1) * _theme.SCROLLBAR_STROKE_WEIGHT)
    w, h = self.size
    sbsf = -h / ((len(self.ls) + 1) * 48)
    rect(w - 2, h + self.disp_layer.frame.y * sbsf, 2, h * sbsf)
  
  
  def draw_fps(self):
    _theme = themes.cur_theme()
    h = self.size.h
    fps = 1 / self.dt
    fill(*_theme.PATH_BG_COLOR)
    no_stroke()
    rect(0, h - 48, 32, 48)
    tint(1 - fps / 60, fps / 60, 0.2)
    text('%02d' % fps, *_theme.FPS_FONT, x=4, y=h - 8, alignment=3)
    
  # ======================================
  
  
  # == Scrolling =========================
    
  def do_scroll_kinetics(self):
    # move the display layer
    self.move_disp(self.velocity)
    # apply 20% friction
    self.velocity *= 0.8
    # stop conditions
    if abs(self.velocity) < 0.1:
      self.velocity = 0
      self.clear_disp_y_over()
    if self.disp_layer.frame.y < 0:
      self.velocity = 0

    
  def move_disp(self, y_change):
    '''Moves the display layer.'''
    frame = self.disp_layer.frame
    y = frame.y + y_change
    if y < 0:
      self.velocity = 0
      y -= 0.75 * y_change * frame.h / 480 # automatically pull the frame back up if the "pull to refresh" panel is showing
      if y > 0:
        y = 0
    if y < -64:
      y = -64
    frame.y = y
    self.correct_disp_bottom()
  
  
  def correct_disp_bottom(self):
    '''Fix and keep track of the display layer overshooting the bottom.'''
    frame = self.disp_layer.frame
    if frame.y > self.disp_layer.bottom:
      disp_layer = self.disp_layer
      self.disp_y_over += frame.y - disp_layer.bottom
      disp_layer.end_layer.alpha = self.disp_y_over / 256
      self.disp_y_over *= 0.8
      frame.y = disp_layer.bottom
      if self.velocity == 0:
        self.clear_disp_y_over()
        
        
  def clear_disp_y_over(self):
    '''Clear the display layer bottom overshoot tracking.'''
    if self.disp_y_over > 0:
      self.disp_y_over = 0
      self.disp_layer.end_layer.alpha = 0
  
  
  def scroll_to_top(self):
    self.velocity = 0
    f = self.disp_layer.frame
    def completion():
      f.y = 0
    self.disp_layer.animate('frame', Rect(f.x, 0, f.w, f.h), 0.1, completion=lambda: self.delay(0.1, completion))
  
  # ======================================
  
  
  # == Touches ===========================
  
  def touch_began(self, touch):
    layer = touch.layer
    if layer is None or layer.superlayer is not self.disp_layer:
      return
    layer.alpha = 0.3
    layer.active = True
    
    tis = self.touchtracker.touches
    tinfo = tis[touch.touch_id]
    frame = layer.frame
    origin2 = layer.superlayer.convert_to_screen(frame.origin())
    frame2 = Rect(origin2.x, origin2.y, frame.w, frame.h)
    tinfo.add_exit_box(frame2, 'lfcp')
  
  
  def touch_moved(self, touch):
    layer = touch.layer
    if layer is None or layer.superlayer is not self.disp_layer:
      return
    y_change = touch.location.y - touch.prev_location.y
    
    tis = self.touchtracker.touches
    tinfo = tis[touch.touch_id]
    pdx = touch.prev_location.x - tinfo.start_loc.x
    if pdx <= -30 or pdx >= 30:
      self._reset_nodelayer(layer)
    if tinfo.exited_boxes['lfcp'][1]:
      layer.alpha = 1
      self.velocity = y_change
    else:
      dx = touch.location.x - tinfo.start_loc.x
      from .themes import _utils
      _theme = themes.cur_theme()
      if dx <= -30:
        layer.alpha = 1
        layer.background = _utils.wavg_color((420+dx, _theme.NODE_BG_COLOR), (-4*dx, Color(1.5, 0.75, 0)))
      elif dx >= 30:
        layer.alpha = 0.7
        layer.background = _utils.wavg_color((420-dx, _theme.NODE_BG_COLOR), (4*dx, Color(0, 0.75, 1)))
        import math
        a = 1/math.sqrt(0.5*(dx-30)+1)
        self.path_layer.alpha = a
        self.disp_layer.alpha = 0.5*(a+1)
        self.disp_layer.frame.x = 0.5*(dx-30)
      else:
        layer.alpha = 0.3
        self.velocity = y_change
    layer.active = False
  
  
  def touch_ended(self, touch):
    layer = touch.layer
    # scroll to the top when the top bar is touched
    if layer is self.path_layer and touch.location in self.path_layer.frame:
      self.scroll_to_top()
    
    if layer is None or layer.superlayer is not self.disp_layer:
      return
    self.clear_disp_y_over()
    frame = self.disp_layer.frame
    # refresh if "release to refresh" is showing
    if frame.y <= -48:
      self.reload_ls(True)
      self.disp_layer.frame = frame
    # automatically pull the frame back up if the "pull to refresh" panel is showing
    if frame.y < 0:
      self.disp_layer.animate('frame', Rect(0, 0, self.size.w, self.size.h), 0.3)
    # prevent scrolling past bottom
    elif frame.y > self.disp_layer.bottom:
      frame.y = self.disp_layer.bottom
    # get touch info object
    tis = self.touchtracker.touches
    tinfo = tis[touch.touch_id]
    # open node when touched
    self.node_touched(layer, tinfo)
  
  
  def node_touched(self, nodelayer, tinfo):
    if self.touches or not hasattr(nodelayer, 'canonical_path'):
      self._reset_nodelayer(nodelayer)
      return
    
    if hasattr(nodelayer, 'active') and nodelayer.active:
      # load the node icon
      if hasattr(nodelayer, 'icon_layer'):
        self.cur_iconl = nodelayer.icon_layer
      else:
        self.cur_iconl = None
      # open the node
      cpath = nodelayer.canonical_path
      if not self.open_node(cpath):
        # if node access fails, flash red
        _theme = themes.cur_theme()
        fbdraw.color_flash(nodelayer, _theme.NODE_FAIL_BG_COLOR, _theme.NODE_BG_COLOR)
    
    elif not tinfo.exited_boxes['lfcp'][1]:
      dx = tinfo.touch.location.x - tinfo.start_loc.x
      if dx <= -30:
        cpath = nodelayer.canonical_path
        from .fileview import ActionView
        vfr = ActionView.view_actions(self, cpath)
        self.set_file_view(*vfr)
      elif dx >= 30:
        dpath = os.path.dirname(self.cwd)
        dpath = os.path.normpath(dpath)
        self.open_node(dpath)
      
    # make node layer inactive
    self._reset_nodelayer(nodelayer)
  
  
  def _reset_nodelayer(self, nodelayer):
    _theme = themes.cur_theme()
    nodelayer.active = False
    nodelayer.alpha = 1
    nodelayer.background = _theme.NODE_BG_COLOR
    self.path_layer.alpha = 1
    disp = self.disp_layer
    disp.alpha = 1
    if 'frame' not in disp.animations:
      disp.frame.x = 0

  # ======================================


  # == Opening ===========================
    
  def open_node(self, cpath):
    # attempt to open as directory
    cwd_different = self.cwd != cpath
    cwd_set = self.set_cwd(cpath)
    access = True
    # if opening as a directory is successful, reload the entry list
    if cwd_set and cwd_different:
      self.reload_ls()
      #self.disp_layer.frame.y = 0
    # if opening as a directory fails, and the node is a file, attempt to view
    elif os.path.isfile(cpath):
      access = self.view_file(cpath)
    return (cwd_set and cwd_different and access)
  
  
  
  # == Opening - Directories - CWD ==
    
  def set_cwd(self, cwd):
    '''Attempt to set the current working directory and update the entry list.
    
    Return True if the cwd was successfully set, otherwise return False.
    Note that the file browser cwd is not the os cwd.'''
    try:
      if hasattr(self, 'cwd'):
        relpath = os.path.relpath(cwd, self.cwd)
        if relpath == os.curdir:
          self.fromdircmp = 0
        elif relpath == os.pardir:
          self.fromdircmp = -1
        else:
          self.fromdircmp = 1
      else:
        self.fromdircmp = 0
      self.cwd_timestamp = time.localtime()
      self.ls = [os.pardir] + os.listdir(cwd)
      self.cwd = cwd
      self.cwd_dirty = True
      dsmappath = os.path.join(cwd, _opts.dsmapfile)
      if os.path.exists(dsmappath):
        with open(dsmappath) as f:
          dsmapstr = f.read()
        from .dsmap import dsmap_eval
        self.dsmap = dsmap_eval(dsmapstr)
      else:
        self.dsmap = {}
      self.cwd_dirty = False
      return True
    except OSError:
      return False
  
  
  # == Opening - Directories - Load ls ==
  
  def reload_ls(self, force_refresh=False):
    '''Reload the directory entries and load them into the display layer.'''
    if force_refresh or self.cwd_dirty:
      self.set_cwd(self.cwd)
    curlenls_sq = self.disp_layer.len_ls
    curlenls_sq *= curlenls_sq
    if len(self.ls) * curlenls_sq > 4096:
      self.load_ls(force_refresh)
    else:
      self.load_ls_next(force_refresh, now=True)
  
  
  def load_ls(self, force_refresh=False):
    '''Load the directory entries into the display layer.'''
    self.long_operation = 61
    dt = self.dt
    self.delay(dt, lambda: self.delay(dt, lambda: self.load_ls_next(force_refresh)))
    
    
  def load_ls_next(self, force_refresh=False, now=False):
    '''Load the directory entries into the display layer in this draw loop.'''
    # remove the current layers
    root = self.root_layer
    self.finalize_disp()
    if self.path_layer is not None:
      root.remove_layer(self.path_layer)
    if force_refresh or self.cwd in self.disp_layer_cache:
      disp_data = None
    else:
      filename = nfbdirs.to_treepath(self.cwd) + '.dsp'
      try:
        import gzip
        with gzip.open(filename, 'rb') as f:
          disp_data = f.read()
      except IOError as e:
        disp_data = e
    self.draw_sub = lambda: self._load_ls_now(disp_data, force_refresh)
    if now:
      self.draw()
    
    
  def _load_ls_now(self, disp_data=None, force_refresh=False):
    root = self.root_layer
    if self.disp_layer is not None:
      root.remove_layer(self.disp_layer)
    # create and add the new layers
    w, h = self.size
    memcached_disp = self.disp_layer_cache.get(self.cwd)
    y = 0 if memcached_disp is None else memcached_disp.frame.y
    frame = Rect(0, y, w, h)
    #print os.path.basename(self.cwd),
    if force_refresh or memcached_disp is None:
      if force_refresh or not disp_data:
        disp_layer = self.create_new_disp(frame)
        #print 'created:', 'refresh forced' if force_refresh else 'no cache data'
      else:
        try:
          disp_layer = self.unpickle_disp(disp_data)
          #print 'unpickled'
        except (IOError, OldDirListError) as e:
          disp_layer = self.create_new_disp(frame)
          #print 'created:', e
      self.disp_layer_cache[self.cwd] = disp_layer
      anim_in_delay = 0.25
    else:
      anim_in_delay = 0
      disp_layer = memcached_disp
      disp_layer.update_orientation(frame)
      #print 'in memory'
    disp_layer.animate_in(self.fromdircmp, delay=anim_in_delay)
    root.add_layer(disp_layer)
    self.disp_layer = disp_layer
    # automatically pull the frame back up if the "pull to refresh" panel is showing
    y = disp_layer.frame.y
    if y < 0:
      disp_layer.animate('frame', Rect(0, 0, w, h), 0.3 * y / -64)
    
    self.path_layer = PathLayer(self.cwd, Rect(32 if self.show_fps else 0, h - 48, w, 48))
    root.add_layer(self.path_layer)
    self.long_operation = 2*force_refresh
    
    
  # == Opening - Directories - Disp ==
    
  def create_new_disp(self, frame):
    return DisplayLayer(self.cwd, self.ls, frame, self.thumbresfactor, self.cwd_timestamp)
    
    
  def unpickle_disp(self, disp_data):
    if isinstance(disp_data, IOError):
      raise disp_data
    import cPickle
    disp_layer = cPickle.loads(disp_data)
    if hash(frozenset(self.ls)) != disp_layer.ls_hash:
      raise OldDirListError
    disp_layer.do_postunpickle()
    w, h = self.size
    y = disp_layer.frame.y
    frame = Rect(0, y, w, h)
    disp_layer.update_orientation(frame)
    return disp_layer
    
    
  def finalize_disp(self):
    root = self.root_layer
    disp_layer = self.disp_layer
    if disp_layer is None:
      return
    root.remove_layer(disp_layer)
    self.disp_layer = Layer()
    root.add_layer(self.disp_layer)
    if not isinstance(disp_layer, DisplayLayer):
      return
    abscwd = os.path.normpath(os.path.join(nfbdirs.DOCUMENTS, disp_layer.rel_cwd))
    if disp_layer.new_icon and not abscwd.startswith(nfbdirs.DYN):
      filename = nfbdirs.to_treepath(abscwd) + '.dsp'
      disp_layer.do_prepickle()
      #print disp_layer.__dict__
      import gzip
      with gzip.open(filename, 'wb', _opts.dispcache_gzip_lvl) as f:
        import cPickle
        cPickle.dump(disp_layer, f, 2)
      
      
      
  # == Opening - Files ==
      
  def view_file(self, file_path):
    '''Attempt to open the file for viewing.
    
    Return True if the file could successfully be opened for viewing, otherwise return False.'''
    try:
      self.long_operation = 61
      fileobj = open(file_path)
      self.root_layer.ignores_touches = True
      vfn = lambda: self.view_file_now(file_path, fileobj)
      dt = self.dt
      self.delay(dt, lambda: self.delay(dt, vfn))
      return True 
    except IOError:
      self.long_operation = 0
    except:
      self.long_operation = 0
      raise 
    return False
    
    
  def view_file_now(self, file_path, fileobj=None):
    from .fileview import autoview
    vfr = autoview.view_file(self, file_path, fileobj)
    self.set_file_view(*vfr)
    
  
  def set_file_view(self, NTP, args2, longop):
    if hasattr(self.file_view, 'root'):
      oldntp = self.file_view.root.ntp
      oldntp.close_view()
    args, kwargs = args2
    from .fileview import FileViewWrapper
    self.file_view = fv = FileViewWrapper.FileViewLayer(NTP, self.bounds, *args, **kwargs)
    self.add_layer(fv)
    self.long_operation = longop
    self.root_layer.ignores_touches = False
    
  # ======================================


  # == Stopping ==========================

  def stop(self):
    if self.file_view is not None:
      self.file_view.stop()
    self.finalize_disp()
    if _opts._print_cache_sizes:
      self.print_cache_sizes()
    
    
  def print_cache_sizes(self):
    print 'gzip level:', _opts.dispcache_gzip_lvl
    tcls = os.listdir(nfbdirs.TREE_CACHE)
    for node in tcls:
      if not node.endswith('.dsp'):
        continue
      decoded = nfbdirs.from_treepath(os.path.splitext(node)[0])
      absnode = os.path.join(nfbdirs.TREE_CACHE, node)
      print os.path.basename(decoded), os.path.getsize(absnode)
    print
    
  # ======================================
    
    
    
class PathLayer (Layer):
  '''A simple text layer that displays the base name of a path.'''
  
  def __init__(self, cwd, frame):
    Layer.__init__(self, frame)
    _theme = themes.cur_theme()
    self.background = _theme.PATH_BG_COLOR
    self.stroke = _theme.PATH_STROKE_COLOR
    self.stroke_weight = _theme.PATH_STROKE_WEIGHT
    basename = os.path.basename(cwd)
    path_img = render_text(basename, *_theme.PATH_FONT)
    def add_text_layer(y, tint=Color()):
      path_text_layer = Layer(Rect(0, y, path_img[1].w, path_img[1].h))
      path_text_layer.image = path_img[0]
      path_text_layer.ignores_touches = True
      path_text_layer.tint = tint
      self.add_layer(path_text_layer)
    add_text_layer(3, _theme.PATH_HILITE_TINT)
    add_text_layer(4, _theme.PATH_TINT)
    
    
    
class DisplayLayer (Layer):
  '''The main display layer for the file browser.'''
  
  def __init__(self, cwd, ls, frame, thumbresfactor=2, timestamp=None):
    # initialize layer
    Layer.__init__(self, frame)
    self.len_ls = len(ls)
    self.ls_hash = hash(frozenset(ls))
    self.next_preload = 0
    self.rel_cwd = os.path.relpath(cwd, nfbdirs.DOCUMENTS)
    self.new_icon = True
    # default value for timestamp
    if timestamp is None:
      timestamp = time.localtime()
    self.set_timestamp(timestamp)
    # add an invisible dummy layer to the bottom
    self.mk_drag_layer()
    
    # create and add a node layer for each directory entry
    for i, node in enumerate(ls, 2):
      layer = FBNodeLayer.NodeLayer(cwd, node, self.get_node_frame(i), thumbresfactor, self)
      self.add_layer(layer)
    
    # remove all sublayers in preparation for visible items optimization
    self.items = self.sublayers
    self.sublayers = []
    self.calc_num_vis()
    
    
  def update_orientation(self, frame):
    self.frame = frame
    self.mk_drag_layer()
    self.calc_num_vis()
    self.set_timestamp(self.timestamp)
    
  
  def set_timestamp(self, timestamp=None):
    if timestamp is None:
      timestamp = time.localtime()
    self.timestamp = timestamp
    _theme = themes.cur_theme()
    self.timestamp_text = _theme.REFRESH_TIME_PREFIX + time.strftime('%c', timestamp)
    
    
  def _calc_bottom(self):
    self.bottom = (self.len_ls + 1) * 48 - self.frame.h
    
    
  def mk_drag_layer(self):
    if hasattr(self, 'drag_layer'):
      self.drag_layer.remove_layer()
    self._calc_bottom()
    frame = self.frame
    if self.bottom < 0:
      drag_layer = Layer(Rect(0, 0, frame.w, 16 + frame.h - self.bottom))
      self.bottom = 0
    else:
      drag_layer = Layer()
    end_layer = Layer(Rect(0, 0, frame.w, 4))
    _theme = themes.cur_theme()
    end_layer.background = _theme.END_STOP_BG_COLOR
    end_layer.alpha = 0
    drag_layer.add_layer(end_layer)
    self.end_layer = end_layer
    self.add_layer(drag_layer)
    self.drag_layer = drag_layer
    if hasattr(self, 'items'):
      self.items[0] = self.drag_layer
    
    
  def animate_in(self, wf, duration=0.25, delay=0):
    oldframe = self.frame
    self.frame = frame = Rect(*oldframe)
    frame.x = frame.w * wf
    self.animate('frame', oldframe, duration, delay)
    
    
  def get_node_frame(self, i):
    return Rect(0, self.frame.h - (i * 48), self.frame.w, 48)
    
    
  def load_node_frame(self, i, dst_r):
    dst_r.y = self.frame.h - (i * 48)
    dst_r.w = self.frame.w
    
    
  def calc_num_vis(self):
    self.num_vis = int(size()[1] / 48 + 3)
      
      
  def update(self, dt):
    # draw only visible items
    top_vis, end_vis = self.get_visible_span()
    if self.next_preload < end_vis:
      self.next_preload = end_vis
    vis_items = self.items[top_vis:end_vis]
    self.sublayers = vis_items
    for i, item in enumerate(vis_items, top_vis + 1):
      self.load_node_frame(i, item.frame)
    Layer.update(self, dt)
  
  
  def draw(self, a=1):
    if self.frame.y < 0:
      self.draw_refresh_panel()
    Layer.draw(self, a)
    self.end_layer.draw()
    
  
  def draw_refresh_panel(self):
    _theme = themes.cur_theme()
    frame = self.frame
    if frame.y > -48:
      tintc = _theme.REFRESH_PULL_COLOR
      utext = _theme.REFRESH_PULL_TEXT
    else:
      tintc = _theme.REFRESH_RELEASE_COLOR
      utext = _theme.REFRESH_RELEASE_TEXT
    w2 = frame.w / 2
    h = frame.h
    a = frame.y / -64
    self.draw_refresh_arrow(tintc, w2,h,a)
    self.draw_refresh_text(utext, w2,h,a)
  
  
  def draw_refresh_arrow(self, tint_color, w2, h, a):
    _theme = themes.cur_theme()
    push_matrix()
    translate(w2, h - 72)
    rotate(-(360 ** a))
    c = Color(*tint_color)
    c.a *= a
    tint(*c)
    image(_theme.REFRESH_IMG, -24, -24, 48, 48)
    pop_matrix()
  
  
  def draw_refresh_text(self, update_text, w2, h, a):
    _theme = themes.cur_theme()
    textfont = _theme.REFRESH_TEXT_FONT
    timefont = _theme.REFRESH_TIME_FONT
    time_text = self.timestamp_text
    c = Color(*_theme.REFRESH_HILITE_TINT)
    c.a *= a
    tint(*c)
    text(update_text, *textfont, x=w2, y=h - 65)
    text(time_text, *timefont, x=w2, y=h - 81)
    c = Color(*_theme.REFRESH_TINT)
    c.a *= a
    tint(*c)
    text(update_text, *textfont, x=w2, y=h - 64)
    text(time_text, *timefont, x=w2, y=h - 80)
    
    
  def get_visible_span(self):
    '''Determine which items should currently be visible'''
    top_vis = int(self.frame.y / 48 - 1)
    if top_vis < 0:
      top_vis = 0
    end_vis = top_vis + self.num_vis
    return top_vis, end_vis
  
  
  def preload_icons(self, n):
    npl = self.next_preload
    if npl >= len(self.items):
      return
    items = self.items[npl:npl+n]
    if not items:
      return
    for i, item in enumerate(items):
      item.update((n-i)*0.01)
    first = items[0]
    if not isinstance(first, FBNodeLayer.NodeLayer) or first.icon_layer.image:
      self.next_preload += 1
  
  
  def do_prepickle(self):
    self.update(1)
    self.remove_layer()
    self.new_icon = False
    self.items[0] = None
    self.superlayer = None
    self.sublayers = []
    #del self.frame
    del self.bottom, self.drag_layer, self.end_layer, self.num_vis, self.timestamp_text
    
    
  def do_postunpickle(self):
    for item in self.items:
      if item is None:
        continue 
      item.add_layer(item.icon_layer)
      if item.text_layer is not None:
        item.add_layer(item.text_layer)
      self.add_layer(item)




    
    
def mk_file_browser(path=None, show_fps=None):
  if path is None:
    path = _opts.start_path
  if show_fps is None:
    show_fps = _opts._show_fps
  return FileBrowser(path, show_fps)

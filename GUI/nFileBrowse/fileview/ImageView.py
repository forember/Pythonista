from __future__ import division

from scene import *
from .FileViewWrapper import GenericNTP
from .. import themes
#import clipboard, photos


class ImageViewPane (GenericNTP):
  def __init__(self, frame, image, file_path, is_icon=False, iconl=None):
    GenericNTP.__init__(self, frame)
    _theme = themes.cur_theme()
    self.background = _theme.IMAGE_VIEW_BG
    self.file_path = file_path
    self.is_icon = is_icon
    self.iconl = iconl
    from PIL import Image
    self.isize = Image.open(file_path).size
    self.ifile = None
    self.iparser = None
    self.pil_image = None
    self.pil_rgba = None
    self.image_layer = Layer()
    self.image_layer.frame = self.get_init_frame()
    self.image_layer.image = image
    self.image_layer.ignores_touches = True
    self.add_layer(self.image_layer)
    self.do_refresh = False
    self.do_load = False
    self.stage_load = 0
    
  def set_frame(self, frame, **kwargs):
    self.frame = frame
    self.image_layer.frame = self.get_init_frame()
    
  def start(self, **kwargs):
    if self.is_icon:
      self.do_refresh = True
  
  def stop(self, duration=0, **kwargs):
    self.do_refresh = False
    if self.do_load:
      self.do_load = False
      self.load_fin(False)
    if not duration and self.pil_image:
      unload_image(self.image_layer.image)
    
  def refresh(self):
    self.ifile = open(self.file_path, 'rb')
    from PIL import ImageFile
    self.iparser = ImageFile.Parser()
    self.do_load = True
  
  def load_step(self, n=4096):
    s = self.ifile.read(n)
    fin = 0
    if s:
      try:
        self.iparser.feed(s)
      except IOError:
        self.load_fin(False)
    else:
      self.load_fin()
    
  def load_fin(self, actually_try=True):
    self.do_load = False
    self.ifile.close()
    self.ifile = None
    try:
      if not actually_try:
        return False
      img = self.iparser.close()
    except IOError:
      return False
    finally:
      self.iparser = None
    self.isize = img.size
    self.pil_image = img
    self.is_icon = False
    self.stage_load = 1
    return True
  
  def update(self, dt):
    GenericNTP.update(self, dt)
    if self.do_refresh:
      self.do_refresh = False
      self.refresh()
    if self.do_load:
      self.load_step(32768)
    elif self.stage_load:
      stage = self.stage_load
      self.stage_load += 1
      if stage == 2:
        self.pil_rgba = self.pil_image.convert('RGBA')
      elif stage == 4:
        self.image_layer.image = load_pil_image(self.pil_rgba)
        self.image_layer.frame = self.get_init_frame()
      elif stage == 6:
        if self.iconl is not None:
          img = self.pil_rgba
          self.iconl.skip_load_delay(img)
        self.stage_load = 0
  
  def draw(self, a=1):
    GenericNTP.draw(self, a)
    if self.do_load or self.stage_load:
      from .. import fbdraw
      cx, cy = self.frame.center()
      fbdraw.draw_loading(cx, cy)
  
  def __del__(self):
    unload_image(self.image_layer.image)
    try:
      GenericNTP.__del__(self)
    except AttributeError:
      pass
  
  def get_init_frame(self):
    '''Recalculate the frame of the image layer.'''
    lf = self.frame
    max_idim = max(self.isize)
    if self.is_icon:
      #iw = ih = max_idim
      iw, ih = self.isize
    else:
      iw, ih = self.isize
    iwhr = float(iw) / ih
    lfwhr = float(lf.w) / lf.h
    c = Point(lf.w / 2, lf.h / 2)
    if iwhr > lfwhr:
      bw = lf.w
      bh = bw * float(ih) / iw
    else:
      bh = lf.h
      bw = bh * iwhr
    max_idim /= 68
    if self.is_icon:
      bw = bh = max(bw, bh)
    elif max_idim < 1:
      bw *= max_idim
      bh *= max_idim
    bounds = Rect(c.x - bw / 2, c.y - bh / 2, bw, bh)
    return bounds

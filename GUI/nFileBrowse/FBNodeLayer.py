from __future__ import division

import os
from scene import *
from PIL import Image

from . import nfbdirs
from . import themes

Image.init()



class TextLayer (Layer):
  
  def __init__(self, text, font, maxw=None, condensed_font=None):
    Layer.__init__(self)
    self.ignores_touches = True
    img, size = render_text(text, *font)
    if maxw is not None and size.w > maxw:
      if condensed_font is not None:
        font = condensed_font
      from .scenefont import truncate_text
      text = truncate_text(text, font, maxw)
      img, size = render_text(text, *font)
    self.text = text
    self.font = font
    self.image = img
    self.frame = Rect(0, 0, size.w, size.h)
    self.do_refresh = False
  
  
  def update(self, dt):
    if self.do_refresh:
      self.image, size = render_text(self.text, *self.font)
      self.frame.w = size.w
      self.frame.h = size.h
      self.do_refresh = False
    Layer.update(self, dt)
    
    
  def __getstate__(self):
    return self.text, self.font, self.frame.x, self.frame.y
    
    
  def __setstate__(self, state):
    Layer.__init__(self)
    self.ignores_touches = True
    self.text, self.font, x, y = state
    self.frame = Rect(x, y, 0, 0)
    self.do_refresh = True
    
    
    
class NodeLayer (Layer):
  '''A selectable icon-and-text layer representing a single directory entry.'''
  
  def __init__(self, cwd, node, frame, thumbresfactor=2, disp_layer=None):
    # initialize layer
    Layer.__init__(self, frame)
    self.copy_constants()
    
    # create and add the icon layer
    absnode = os.path.normpath(os.path.join(cwd, node))
    relnode = os.path.relpath(absnode, nfbdirs.DOCUMENTS)
    self.icon_layer = NodeIconLayer(relnode, resfactor=thumbresfactor, disp_layer=disp_layer)
    if node == os.pardir:
      _theme = themes.cur_theme()
      icon = _theme.UPDIR_ICON
      imgpath = get_image_path(icon)
      if imgpath is None:
        imgpath = icon
      iconl = self.icon_layer
      iconl.pil_image = imgpath
      iconl.do_load = False
      iconl.do_refresh = True
      iconl.background = _theme.NODE_ICON_TARGET_BG
    self.add_layer(self.icon_layer)
    
    self.node = node
    self.canonical_path = absnode
    self.text_layer = None
    self.framew = None
    
    
  def copy_constants(self):
    _theme = themes.cur_theme()
    self.background = _theme.NODE_BG_COLOR
    self.stroke = _theme.NODE_STROKE_COLOR
    self.stroke_weight = _theme.NODE_STROKE_WEIGHT
    self.tint = _theme.NODE_TINT
    
    
  def __getstate__(self):
    return self.node, self.canonical_path, self.text_layer, self.icon_layer, self.framew
    
    
  def __setstate__(self, state):
    Layer.__init__(self)
    self.copy_constants()
    self.node, self.canonical_path, self.text_layer, self.icon_layer, self.framew = state
    self.frame = Rect(0, 0, 0, 48)
    if self.text_layer is not None:
      self.text_layer.tint = self.tint
    
    
  def update(self, dt):
    Layer.update(self, dt)
    if self.framew != self.frame.w:
      self.refresh_text()
  
  
  def refresh_text(self):
    # create and add text layer
    if self.text_layer is not None:
      self.text_layer.remove_layer()
    self.framew = self.frame.w
    _theme = themes.cur_theme()
    text_layer = TextLayer(self.node, _theme.NODE_FONT, maxw=self.framew - 50, condensed_font= _theme.NODE_CONDENSED_FONT)
    tlf = text_layer.frame
    tlf.x, tlf.y = 48, 2
    text_layer.tint = self.tint
    self.add_layer(text_layer)
    self.text_layer = text_layer
    
    
    
class NodeIconLayer (Layer):
  '''A self-configuring icon layer for a node layer.'''
  
  def __init__(self, relnode, frame=None, link_badge_frame=None, resfactor=2, disp_layer=None):
    # default frame values
    if frame is None:
      frame = Rect(7, 7, 34, 34)
    if link_badge_frame is None:
      link_badge_frame = Rect(2, 2, 16, 16)
    # initialize layer
    Layer.__init__(self, frame)
    self.copy_constants()
    _theme = themes.cur_theme()
    self.background = _theme.NODE_ICON_START_BG
    # set attributes
    self.relnode = relnode
    self.absnode = os.path.normpath(os.path.join(nfbdirs.DOCUMENTS, self.relnode))
    self.link_badge_frame = link_badge_frame
    self.resfactor = resfactor
    self.disp_layer = disp_layer
    
    self.pil_image = None
    self.do_load = not self.pil_image
    self.do_refresh = False
    self.refresh_ext()
    
    
  def __getstate__(self):
    return self.frame, self.relnode, self.link_badge_frame, self.resfactor, self.disp_layer, self.pil_image
  
  
  def __setstate__(self, state):
    Layer.__init__(self)
    self.frame, self.relnode, self.link_badge_frame, self.resfactor, self.disp_layer, self.pil_image = state
    self.copy_constants()
    _theme = themes.cur_theme()
    if self.pil_image is not None:
      self.background = _theme.NODE_ICON_TARGET_BG
    else:
      self.background = _theme.NODE_ICON_START_BG
    self.do_refresh = bool(self.pil_image)
    self.do_load = not self.pil_image
    self.absnode = os.path.normpath(os.path.join(nfbdirs.DOCUMENTS, self.relnode))
    self.refresh_ext()
  
  
  def copy_constants(self):
    _theme = themes.cur_theme()
    self.ignores_touches = True
    self.stroke = _theme.NODE_ICON_STROKE_COLOR
    self.stroke_weight = _theme.NODE_ICON_STROKE_WEIGHT
    
    
  def update(self, dt):
    Layer.update(self, dt)
    if self.do_load:
      if self.has_image_ext():
        fsz = os.path.getsize(self.absnode)
        d = 0.03125 * (fsz >> 10)
        if d > 8:
          d = 8
        _theme = themes.cur_theme()
        self.animate('background', _theme.NODE_ICON_TARGET_BG, d, completion=self.load)
      else:
        _theme = themes.cur_theme()
        self.background = _theme.NODE_ICON_TARGET_BG
        self.load()
      self.do_load = False
    if self.do_refresh:
      self.refresh_pil_image()
      self.do_refresh = False
  
  
  def skip_load_delay(self, pil_img=None):
    if pil_img is not None:
      if self.load_img_thumb():
        if self.disp_layer is not None:
          self.disp_layer.new_icon = True
        self.disp_layer = None
        self.do_load = False
      else:
        pil_img = None
    if pil_img is None and self.animations:
      self.remove_all_animations()
      _theme = themes.cur_theme()
      self.background = _theme.NODE_ICON_TARGET_BG
      self.load()
      self.do_load = False
    
    
  def load(self):
    _theme = themes.cur_theme()
    absnode = self.absnode
    # no-access icon
    if not os.access(absnode, os.R_OK):
      self.image = _theme.NOACCESS_ICON
      #self.scale_y = 1.183
    # directory icon
    elif os.path.isdir(absnode):
      self.image = _theme.FOLDER_ICON
    # attempt to open as image and generate thumbnail
    else:
      if not self.load_img_thumb():
        # default file icon
        self.image = _theme.PYFILE_ICON if self.ext == '.py' else _theme.FILE_ICON
      elif self.disp_layer is not None:
        self.disp_layer.new_icon = True
    # symbolic link badge
    if os.path.islink(absnode):
      link_badge_layer = Layer(self.link_badge_frame)
      link_badge_layer.image = _theme.SYMLINK_BADGE
      self.add_layer(link_badge_layer)
    self.disp_layer = None
  
  
  def refresh_ext(self):
    basename = os.path.basename(self.absnode)
    extdoti = basename.rfind('.')
    self.ext = None if extdoti == -1 else basename[extdoti:]
  
  
  def has_image_ext(self):
    return self.ext in Image.EXTENSION
  
  
  def load_img_thumb(self, pil_img=None):
    absnode = self.absnode
    if not self.has_image_ext():
      return False
    try:
      trf = self.resfactor
      sz = int(trf * self.frame.w), int(trf * self.frame.h)
      if pil_img is None:
        thumb = Image.open(absnode)
      else:
        thumb = pil_img.copy()
      npx = thumb.size[0] * thumb.size[1]
      if npx > 65536:
        thumb.thumbnail((256, 256), Image.NEAREST)
      thumb.thumbnail(sz, Image.ANTIALIAS)
      square = Image.new('RGBA', sz)
      #print os.path.basename(absnode), max(thumb.size) / (trf * 34)
      square.paste(thumb, ((sz[0] - thumb.size[0]) // 2, (sz[1] - thumb.size[1]) // 2))
      img = load_pil_image(square)
      self.image = img
      filename = nfbdirs.to_treepath(absnode) + '.jpg'
      if not absnode.startswith(nfbdirs.DYN):
        square.save(filename)
      self.pil_image = os.path.relpath(filename, nfbdirs.TREE_CACHE)
      return True
    except IOError:
      img = load_image_file(absnode)
      if img:
        self.image = img
        self.pil_image = os.path.relpath(absnode, nfbdirs.TREE_CACHE)
        return True
    finally:
      if self.pil_image is not None:
        self.alpha = 0
        self.animate('alpha', 1, 1, 0.5)
    return False
    
    
  def refresh_pil_image(self):
    if self.pil_image is not None:
      imgfile = os.path.normpath(os.path.join(nfbdirs.TREE_CACHE, self.pil_image))
      self.image = load_image_file(imgfile)
      if not self.image:
        print 'error loading ' + repr(imgfile)
  
  
  def __del__(self):
    # release icon resources if it is a generated thumbnail
    if self.pil_image is not None and self.image is not None:
      unload_image(self.image)
    try:
      Layer.__del__(self)
    except AttributeError:
      pass
    

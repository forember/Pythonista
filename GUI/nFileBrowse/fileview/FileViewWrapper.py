from scene import *
from .. import themes

_INTERN_ROOT = intern('root')

class FileViewLayer (Layer):
  def __init__(self, NTP, frame, *args, **kwargs):
    Layer.__init__(self, frame)
    self.root = FileViewRootLayer(NTP, frame, *args, **kwargs)
    self.add_layer(self.root)
    _theme = themes.cur_theme()
    self.animate('background', _theme.NTPL_BG_COLOR)
    
  def update(self, dt):
    sl = self.superlayer
    if self.frame != sl.frame:
      self.frame = sl.frame
      self.remove_layer()
      sl.add_layer(self)
    Layer.update(self, dt)
    
  def touch_began(self, touch):
    if hasattr(self, _INTERN_ROOT):
      self.root.touch_began(touch)
  
  def stop(self):
    if hasattr(self, _INTERN_ROOT):
      self.root.ntp.stop()

class FileViewRootLayer (Layer):
  def __init__(self, NTP, frame, *args, **kwargs):
    Layer.__init__(self, frame)
    
    # create and add arrow layer
    arrow_w = frame.w / 16
    arrow = Layer(Rect(0, (frame.h - arrow_w) / 2, arrow_w, arrow_w))
    arrow.ignores_touches = True
    _theme = themes.cur_theme()
    arrow.image = _theme.NTPL_ARROW_IMG
    arrow.tint = _theme.NTPL_ARROW_TINT
    self.arrow_layer = arrow
    self.add_layer(arrow)
    
    self.ntp = NTP(Rect(frame.w / 16, 0, 0.9375 * frame.w, frame.h), *args, **kwargs)
    self.add_layer(self.ntp)
    
    self.moving = True
    self.frame = Rect(*frame)
    self.frame.x += frame.w
    def completion():
      self.moving = False
      self.ntp.start()
    self.animate('frame', frame, completion=completion)
    
  def update(self, dt):
    Layer.update(self, dt)
    if not self.moving and self.frame != self.superlayer.frame:
      sl = self.superlayer
      frame = self.frame = sl.frame
      arrow_w = frame.w / 16
      self.arrow_layer.frame = Rect(0, (frame.h - arrow_w) / 2, arrow_w, arrow_w)
      self.ntp.set_frame(Rect(frame.w / 16, 0, 0.9375 * frame.w, frame.h))
      self.remove_layer()
      sl.add_layer(self)
    
  def touch_began(self, touch):
    # if the scene does not intercept a touch, close the layer
    self.close_view()
  
  def close_view(self):
    self.moving = True
    target = Rect(*self.frame)
    duration = 1 - target.x / target.w
    duration *= 0.5
    target.x = target.w
    self.ntp.stop(duration=duration)
    def completion():
      self.ntp.stop()
      sl = self.superlayer
      sl.remove_layer()
      sl.remove_layer(self)
      del sl.root
    self.animate('frame', target, duration, completion=completion)
    _theme = themes.cur_theme()
    bg_target = _theme.NTPL_FADE_TARGET
    self.superlayer.animate('background', bg_target, duration, completion=completion)

def close_view(ntp):
  sl = ntp.superlayer
  if hasattr(sl, 'close_view') and callable(sl.close_view):
    sl.close_view()
    return True
  return False

class GenericNTP (Layer):
  def __init__(self, frame):
    Layer.__init__(self, frame)
    _theme = themes.cur_theme()
    self.background = _theme.GENERIC_NTP_BG
  
  def set_frame(self, frame, **kwargs):
    self.frame = frame
  
  def start(self, **kwargs):
    pass
  
  def stop(self, **kwargs):
    pass
    
  def close_view(self):
    return close_view(self)

INTERN_FRAME = intern('frame')



class InstallError (Exception):
  
  pass



class TouchInfo (object):
  
  def __init__(self, touch, scene_t):
    self.touch = touch
    self.start_t = scene_t
    self.start_loc = touch.location
    self.exited_layer_enabled = False
    self.exited_layer = False
    self.exited_boxes = {}
  
  
  def update_exited_boxes(self):
    loc = self.touch.location
    for name, (box, e) in self.exited_boxes.iteritems():
      if e:
        continue
      if loc not in box:
        self.exited_boxes[name] = (box, True)
  
  
  def add_exit_box(self, box, name=None):
    if name is None:
      name = id(box)
    self.exited_boxes[name] = (box, False)



class TouchTracker (object):
  
  scene = None
  
  
  def __init__(self):
    self.touches = {}
  
  
  def install(self, scen):
    if self.scene is not None:
      raise InstallError
    self.scene = scen
    self._touch_began = scen.touch_began
    self._touch_moved = scen.touch_moved
    self._touch_ended = scen.touch_ended
    scen.touch_began = self.touch_began
    scen.touch_moved = self.touch_moved
    scen.touch_ended = self.touch_ended
  
  
  def uninstall(self):
    scen = self.scene
    self.scene = None
    scen.touch_began = self._touch_began
    scen.touch_moved = self._touch_moved
    scen.touch_ended = self._touch_ended
    self._touch_began = lambda: None
    self._touch_moved = lambda: None
    self._touch_ended = lambda: None
    
    
  def touch_began(self, touch):
    tinfo = TouchInfo(touch, self.scene.t)
    self.touches[touch.touch_id] = tinfo
    self._touch_began(touch)
  
  
  def touch_moved(self, touch):
    tinfo = self.touches[touch.touch_id]
    tinfo.touch = touch
    if tinfo.exited_layer_enabled:
      layer = touch.layer
      loc2 = layer.superlayer.convert_from_screen(touch.location)
      if hasattr(layer, INTERN_FRAME) and loc2 not in layer.frame:
        tinfo.exited_layer = True
    tinfo.update_exited_boxes()
    self._touch_moved(touch)
  
  
  def touch_ended(self, touch):
    tinfo = self.touches[touch.touch_id]
    tinfo.touch = touch
    tinfo.update_exited_boxes()
    self._touch_ended(touch)
    del self.touches[touch.touch_id]

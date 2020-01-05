# -*- coding: utf-8 -*-

from scene import Layer

class SceneLayer (Layer):
  '''Wraps a scene in a layer.'''
  
  def __init__(self, scene, frame):
    Layer.__init__(self, frame)
    self.dt = 0
    scene._setup_scene(*frame.size())
    self.scene = scene
    
  def update(self, dt):
    self.dt += dt
    sz = self.frame.size()
    if self.scene.size != sz:
      self.scene._set_size(*sz)
    
  def draw(self, a=1):
    dt = self.dt
    self.dt = 0
    return self.scene._draw(dt)
    
  def touch_began(self, touch):
    x, y = touch.location
    return self.scene._touch_began(x, y, touch.touch_id)
    
  def touch_moved(self, touch):
    x, y = touch.location
    prev_x, prev_y = touch.prev_location
    return self.scene._touch_moved(x, y, prev_x, prev_y, touch.touch_id)
    
  def touch_ended(self, touch):
    x, y = touch.location
    return self.scene._touch_ended(x, y, touch.touch_id)
    
  def should_rotate(self, orientation):
    return self.scene.should_rotate(orientation)
    
  def pause(self):
    return self.scene.pause()
    
  def resume(self):
    return self.scene.resume()
    
  def stop(self):
    return self.scene._stop()


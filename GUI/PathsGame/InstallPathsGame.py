from __future__ import division

from scene import *
import console
import os
import collections
import math

_ABSOLUTE = False

_REALFILE = os.path.realpath(__file__)
_PARDIR = os.path.dirname(_REALFILE)
_HOME = os.path.expanduser('~')
if _ABSOLUTE:
  DOCSDIR = os.path.join(_HOME, 'Documents')
else:
  DOCSDIR = os.path.dirname(_PARDIR)
PATHSDIR = os.path.join(DOCSDIR, 'PathsGame')
VERFILE = os.path.join(PATHSDIR, 'version')


_VERFIELDS = ('stage_letter', 'major', 'minor', 'patch', 'release_level', 'release_letter', 'year', 'month', 'day', 'hour', 'minute', 'second')

Version = collections.namedtuple('Version', _VERFIELDS)

def parse_version(s):
  import re
  m = re.match(r'([a-z])(\d+)\.(\d+)\.(\d+)-(d[er][cv]|rev)([a-z])-(\d{6})t(\d{6})$', s, re.IGNORECASE)
  if not m:
    raise ValueError, 'invalid version string'
  g = m.groups()
  return Version(g[0].upper(), int(g[1]), int(g[2]), int(g[3]), g[4].upper(), g[5].upper(), int(g[6][:2])+2000, int(g[6][2:4]), int(g[6][4:]), int(g[7][:2]), int(g[7][2:4]), int(g[7][4:]))

def repr_version(v):
  v4 = v[4].lower()
  if v4[:2] == 'dr':
    v4 = 'dr' + v4[2].upper()
  return '{}{:d}.{:d}.{:03d}-{}{}-{:02d}{:02d}{:02d}t{:02d}{:02d}{:02d}'.format(v[0].lower(), v[1], v[2], v[3], v4, v[5].upper(), v[6]-2000, *v[7:])

def str_version(v):
  v0 = v[0]
  if v0 == 'A':
    v0 = 'Alpha'
  elif v0 == 'B':
    v0 = 'Beta'
  v4 = v[4]
  v4s = ''
  if v4[0] == 'D':
    v4s = 'Dev '
  if v4[1] == 'R':
    v4s += 'Release '
  if v4[2] == 'C':
    v4s += 'Candidate'
  elif v4[2] == 'V':
    v4s += 'Revision'
  return '{} {:d}.{:d}.{:d} {} {}\n[{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}Z]'.format(v0, v[1], v[2], v[3], v4s, v[5].upper(), *v[6:])

def load_version(verfile=VERFILE):
  if not os.path.exists(verfile):
    return
  with open(verfile) as f:
    vstr = f.read()
  vstr = vstr.strip()
  return parse_version(vstr)



class SceneLayer (Layer):
  def __init__(self, parent_scene):
    Layer.__init__(self, parent_scene.bounds)
    self._scene = parent_scene
    self.init_t = parent_scene.t
    self.layer_compat()
    self.setup()

  def layer_compat(self):
    self.bounds = self.frame
    self.dt = self._scene.dt
    self.size = self._scene.size
    self.t = self._scene.t - self.init_t
    if hasattr(self._scene, 'scene_layer'):
      self.touches = self._scene.touches if self == self._scene.scene_layer else dict()

  def setup(self):
    pass


class ExampleSceneLayer (SceneLayer):
  def __init__(self, parent_scene):
    SceneLayer.__init__(self, parent_scene)

  def setup(self):
    pass

  def draw(self, a=1):
    self.layer_compat()
    Layer.draw(self, a)


class Button (Layer):
  def __init__(self, frame=Rect(), label=''):
    Layer.__init__(self, frame)
    self.action = None
    self.label = label
    self.background = Color(1, 1, 1, 0.5)
    self.prev_active_touches = []

  def draw(self, a=1):
    c = self.superlayer.convert_to_screen(self.frame.center())
    touches = self.superlayer.touches
    active_touches = []
    for touch in touches.iteritems():
      if touch[1].location in self.frame:
        active_touches.append(touch[0])
    if len(self.prev_active_touches) > 0 and len(active_touches) == 0:
      if not (frozenset(self.prev_active_touches) <= frozenset(touches.iterkeys())):
        if callable(self.action):
          self.action()
    if len(active_touches) > 0:
      self.background = Color(0.9, 0.7, 0.1, 0.9)
    else:
      self.background = Color(1, 1, 1, 0.5)
    self.prev_active_touches = active_touches
    Layer.draw(self, a)
    tint(0, 0, 0, self.alpha)
    text(self.label, 'GillSans', self.frame.h / 1.5, c.x, c.y)




def draw_logo(x, y, s=8):
  push_matrix()
  translate(x, y)
  scale(s)
  no_stroke()
  fill(0.8, 1, 0.9, 0.7)
  rect(0, 0, 1, 5)
  rect(1, 2, 1, 1)
  rect(1, 4, 1, 1)
  rect(2, 2, 1, 3)
  translate(4, 0)
  rect(0, 0, 1, 5)
  rect(1, 2, 1, 1)
  rect(1, 4, 1, 1)
  rect(2, 0, 1, 5)
  translate(4, 0)
  rect(0, 4, 1, 1)
  rect(1, 0, 1, 5)
  rect(2, 4, 1, 1)
  translate(4, 0)
  rect(0, 0, 1, 5)
  rect(1, 2, 1, 1)
  rect(2, 0, 1, 5)
  translate(4, 0)
  rect(0, 0, 3, 1)
  rect(0, 2, 3, 1)
  rect(0, 4, 2, 1)
  rect(0, 3, 1, 1)
  rect(2, 1, 1, 1)
  fill(0.9, 0.7, 0.1, 0.9)
  rect(2, 4, 1, 1)
  pop_matrix()



class StartLayer (SceneLayer):
  
  def __init__(self, parent_scene, back=None):
    self.back = back
    SceneLayer.__init__(self, parent_scene)
  
  
  def setup(self):
    global VERSION
    VERSION = load_version()
    if VERSION is None:
      self.verstr = 'Not Installed'
      self.vertstr = ''
    else:
      vstr = str_version(VERSION)
      self.verstr, self.vertstr = vstr.splitlines()
    self.state = 0
    self.ver_url = 'http://ntd5-mbpro.local/cgi-bin/pathsgame/version.py'
    if VERSION is not None:
      import urllib
      vrepr = repr_version(VERSION)
      self.ver_url += '?v=' + urllib.quote_plus(vrepr)
    self.wait = 3
    self.request_ctd = 1
    self.connection = None
    self.response = None
    self.new_version = None
    self.new_verstr = ''
    self.new_vertstr = ''
    cx, cy = self.bounds.center()
    self.installbtn = Button(Rect(cx-96, cy-120, 192, 32), 'Download & Install')
    self.backbtn = Button(Rect(cx-96, cy-82, 192, 32), 'Quit')
    if self.back is None:
      import sys
      self.backbtn.action = sys.exit
    else:
      self.backbtn.action = lambda: self._scene.set_layer(self.back(self._scene))
    

  def draw(self, a=1):
    self.layer_compat()
    Layer.draw(self, a)
    b = self.bounds
    cx, cy = b.center()
    hy = 0.86*b.h
    draw_logo(cx-76, hy)
    no_tint()
    text('INSTALLER', 'AvenirNextCondensed-UltraLight', 48, cx, hy+13, 2)
    
    tint(0.4, 0.6, 0.5)
    text('CURRENT  VERSION', 'GillSans', 16, cx, cy+56, 8)
    text(self.vertstr, 'GillSans', 16, cx, cy+35, 2)
    text(self.new_vertstr, 'GillSans', 16, cx, cy-59, 2)
    tint(1, 0.8, 0)
    text(self.verstr, 'GillSans', 18, cx, cy+34, 8)
    text(self.new_verstr, 'GillSans', 18, cx, cy-60, 8)
    
    state = self.state
    
    if state == 0:
      statestr = '. . . CONNECTING . . .'
      ts = self.t * 4
      tr = (math.sin(ts) + 1) / 2
      tg = (math.cos(ts) + 1) / 2
    elif state == 1:
      if VERSION is None:
        statestr = 'READY  TO  DOWNLOAD'
      else:
        statestr = 'UPDATES  AVAILABLE'
      ts = self.t
      tr = 1
      tg = (math.cos(ts) + 4) / 5
    elif state == -1:
      statestr = 'UP  TO  DATE'
      ts = self.t
      tr = (math.sin(ts) + 2) / 5
      tg = 1
    else:
      statestr = 'CONNECTION  FAILED'
      ts = self.t
      tr = 1
      tg = (math.cos(ts) + 2) / 6
    tb = 0.3
    tint(tr, tg, tb)
    text(statestr, 'GillSans', 22, cx, cy-38, 8)
    
    if self.state:
      pass
    elif self.wait:
      self.wait -= 1
    elif self.connection:
      self.response = rsp = self.connection.read()
      rsp = rsp.strip()
      self.state = -1 if rsp == '!' else 1
      self.add_layer(self.backbtn)
      if self.state == 1:
        self.backbtn.frame.y = cy-152
        try:
          self.new_version = parse_version(rsp)
          nvstr = str_version(self.new_version)
          self.new_verstr, self.new_vertstr = nvstr.splitlines()
        except ValueError:
          pass
    elif self.request_ctd:
      self.request_ctd -= 1
      import urllib2
      try:
        self.connection = urllib2.urlopen(self.ver_url, timeout=5)
      except urllib2.URLError:
        self.wait = 0
    else:
      self.state = -2
      self.add_layer(self.backbtn)
    
    


class ParticleScene (Scene):
  def __init__(self, mk_scene_layer=StartLayer):
    Scene.__init__(self)
    self.mk_scene_layer = mk_scene_layer
  
  def setup(self):
    self.root_layer = Layer(self.bounds)
    self.scene_layer = self.mk_scene_layer(self)
    self.root_layer.add_layer(self.scene_layer)

  def draw(self):
    background(0, 0, 0)
    self.root_layer.update(self.dt)
    self.root_layer.draw()

  def set_layer(self, layer, clear=True, gcollect=False):
    if clear:
      self.scene_layer.remove_layer()
      for sublayer in self.root_layer.sublayers:
        sublayer.remove_layer()
        del sublayer
      del self.scene_layer
    self.scene_layer = layer
    if gcollect:
      import gc
      gc.collect()
    self.root_layer.add_layer(layer)


def main():
  run(ParticleScene(), PORTRAIT)

if __name__ == '__main__':
  main()

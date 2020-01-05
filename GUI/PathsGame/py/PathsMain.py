from scene import *
import math
import random
import console
import sys
import sound
import gc
import os

from . import InstallPathsGame
ParticleScene = InstallPathsGame.ParticleScene
SceneLayer = InstallPathsGame.SceneLayer
Button = InstallPathsGame.Button

_VERBOSE = False

_REALFILE = os.path.realpath(__file__)
_PYDIR = os.path.dirname(_REALFILE)
PATHSDIR = os.path.dirname(_PYDIR)
DYNDIR = os.path.join(PATHSDIR, 'dyn')
if not os.path.exists(DYNDIR):
  os.mkdir(DYNDIR)

def _init_options():
  global defaults, options
  defaults = \
  {'sensitivity': 1.7,
   'time_sec': 120,
   'player_sprite': None,
   'allow_god_mode': 0}
  options = defaults.copy()
  try:
    options.update(load_options())
  except IOError:
    pass
    
    

class GameLayer (SceneLayer):
  def __init__(self, parent_scene, options):
    SceneLayer.__init__(self, parent_scene)
    self.options = options

  def setup(self):
    c = self.bounds.center()
    self.view_center = Point(0, 0)
    self.particle = Particle(16)
    self.gold_x = random.randint(-4, 4) * 32 + c.x - c.x % 32
    self.gold_y = random.randint(-4, 4) * 32 + c.y - c.y % 32
    self.score = 0
    self.path = gen_path(Point(c.x - c.x % 32, c.y - c.y % 32), Point(self.gold_x, self.gold_y))
    self.grav_cal = Vector3()
    #opt = self.options
    # options
    self.sensitivity = options['sensitivity']
    self.time_sec = options['time_sec']
    self.countdown = 3
    self.friction_val = 1.025
    self.player_sprite = options['player_sprite']
    self.allow_god_mode = options['allow_god_mode']
    # configurable in-game
    self.follow = True
    self.god_mode = self.allow_god_mode == 2
    # ^ configurable in-game
    # special wall rules
    self.lose_hit = True
    self.bounce = False
    self.dull_hit = False
    self.slow = False
    self.slow_val = 2.0
    self.clock_drain_on = False
    self.clock_drain = 4
    self.score_drain_on = False
    self.score_drain = 0.01
    # ^ special wall rules
    # ^ options
    self.sec = self.time_sec + self.countdown
    self.current_pt = (c.x - c.x % 32, c.y - c.y % 32)
    self.exiting_x = self.exiting_y = 0
    self.frozen = False
    self.frozen_manual = False
    if _VERBOSE:
      console.set_color(0.2, 0, 0.4)
      print 'START'
      print 'sensitivity:', self.sensitivity
      print 'time:', self.time_sec, 's'
      print 'friction:', self.friction_val
      console.set_color(0.2, 0.4, 0.4)
      if self.lose_hit:
        print '! lose_hit is ON'
      console.set_color(0.6, 0.2, 0)
      if self.allow_god_mode:
        print '! god mode is ALLOWED'
      if self.bounce:
        print '! bounce BETA is ON'
      if self.dull_hit:
        print '! dull_hit BETA is ON'
      if self.slow:
        print '! slow BETA is ON and set to ' + str(self.slow_val)
      if self.clock_drain_on:
        print '! clock_drain BETA is ON and set to ' + str(self.clock_drain)
      if self.score_drain_on:
        print '! score_drain BETA is ON and set to ' + str(self.score_drain)
      console.set_color(0.2, 0, 0.4)
      print '...'

  def draw(self, a=1):
    Layer.draw(self, a)
    if not self.frozen:
      self.layer_compat()
    prtcl = self.particle
    if self.follow:
      self.view_center = Point(prtcl.x, prtcl.y)
    c = self.bounds.center()
    vc = self.view_center
    bgx = 0.9*vc.x % 62
    bgy = 0.9*vc.y % 62
    fill(0.1, 0.1, 0.125)
    no_stroke()
    no_tint()
    background(0, 0, 0)
    for i in xrange(9):
      for j in xrange(9):
        if True:
          for k in (0, 1):
            rect(31 * (2 * i + k) - bgx, 31 * (2 * j + k) - bgy, 31, 31)
        else:
          image('_mc_dirt_64', 64 * i - bgx, 64 * j - bgy, 64, 64)
    fill(0.8, 1, 0.9, 0.7)
    in_path = False
    bounces = (False, False)
    for pt in self.path:
      rect(pt[0] - vc.x, pt[1] - vc.y, 32, 32)
      pt_dx = prtcl.x + c.x - pt[0]
      pt_dy = prtcl.y + c.y - pt[1]
      in_pt_x = 0 <= pt_dx <= 32
      in_pt_y = 0 <= pt_dy <= 32
      in_pt = in_pt_x and in_pt_y
      if self.bounce and self.current_pt == (pt[0], pt[1]):
        bounces = (not in_pt_x, not in_pt_y)
      in_path = in_path or in_pt
    if not (in_path or self.god_mode or self.frozen):
      if self.bounce:
        sound.play_effect('Boing_1')
        if bounces[0] and self.exiting_x != 0:
          prtcl.vx *= -1
          prtcl.x += prtcl.vx
        if bounces[1] and self.exiting_y != 0:
          prtcl.vy *= -1
          prtcl.y += prtcl.vy
      if self.dull_hit:
        self.exiting_x *= 2
        self.exiting_y *= 2
        prtcl.x -= self.exiting_x
        prtcl.y -= self.exiting_y
        if self.exiting_x != 0:
          prtcl.vx = -self.exiting_x
        if self.exiting_y != 0:
          prtcl.vy = -self.exiting_y
      if self.lose_hit:
        sound.play_effect('Explosion_4')
        self.end('FELL OFF\n@ %d:%02d' % (self.sec / 60, self.sec % 60))
    elif not self.frozen:
      pxbc = prtcl.x + c.x
      pybc = prtcl.y + c.y
      self.current_pt = (pxbc - pxbc % 32, pybc - pybc % 32)
    fill(0.9, 0.7, 0.1, 0.9)
    rect(self.gold_x - vc.x, self.gold_y - vc.y, 32, 32)
    if self.sec > self.time_sec:
      tint(1, 0, 0)
      text(str(int(self.sec + 0.9 - self.time_sec)), 'GillSans', 240, c.x, c.y)
      self.grav_cal = gravity()
    elif not self.frozen:
      grav = gravity()
      grav.x -= self.grav_cal.x
      grav.y -= self.grav_cal.y
      if grav.x != 0:
        prtcl.vx += grav.x * self.sensitivity
      if grav.y != 0:
        prtcl.vy += grav.y * self.sensitivity
      prtcl.vx /= self.friction_val
      prtcl.vy /= self.friction_val
      self.exiting_x = self.exiting_y = 0
      if in_path:
        upxbc = prtcl.x + c.x + prtcl.vx - self.current_pt[0]
        upybc = prtcl.y + c.y + prtcl.vy - self.current_pt[1]
        if upxbc < 0:
          self.exiting_x = upxbc
        elif upxbc > 32:
          self.exiting_x = upxbc - 32
        if upybc < 0:
          self.exiting_y = upybc
        elif upybc > 32:
          self.exiting_y = upybc - 32
      else:
        divisor = 1.0
        if self.god_mode:
          divisor = 1.0
        elif self.slow:
          divisor = self.slow_val
        elif self.bounce:
          divisor = 1.025
        elif self.dull_hit:
          divisor = 1000.0
        prtcl.vx /= divisor
        prtcl.vy /= divisor
      prtcl.tick()
    if self.player_sprite is None:
      fill(1, 0, 0)
      ellipse(prtcl.x - 4 + c.x - vc.x, prtcl.y - 4 + c.y - vc.y, 8, 8)
    else:
      no_tint()
      image(self.player_sprite, prtcl.x - 8 + c.x - vc.x, prtcl.y - 8 + c.y - vc.y, 16, 16)
    #tint(1, 0, 0)
    #text('(%d, %d)' % (vc.x, vc.y), 'GillSans', y=self.bounds.h - 16, alignment=3)
    if not self.frozen:
      if in_path:
        self.sec -= self.dt
      else:
        self.sec -= (self.clock_drain if self.clock_drain_on else 1) * self.dt
        if self.score_drain_on and self.score > 0:
          self.score -= self.score_drain
      if self.sec <= 0:
        self.sec = 0
        if self.score > 2 and self.lose_hit:
          self.score += 2
        sound.play_effect('Clock_2')
        self.end('TIME UP')
    fill(0, 0, 0, 0.8)
    rect(0, 0, self.bounds.w, 32)
    if self.frozen_manual:
      rect(*self.bounds)
      tint(1, 1, 1, 0.8)
      text('Paused', 'AvenirNextCondensed-UltraLight', 64, c.x, c.y, 8)
      text('touch to resume', 'GillSans', 18, c.x, c.y, 2)
      
      tint(1, 0, 0)
      image('Typicons48_Feed', self.bounds.w - 32, 32, 32, 32)
      tint(1, 0.8, 0.8, 0.8)
      text('Quit', 'GillSans', 20, self.bounds.w - 32, 36, 7)
      tint(0, 0, 1, 0.8)
    else:
      tint(0.9, 0.7, 0.1, 0.8)
    image('Typicons48_Time', self.bounds.w - 32, 0, 32, 32)
    if self.frozen:
      tint(0.8, 0.8, 1, 0.8)
    else:
      tint(1, 1, 0.8, 0.8)
    text('%d:%02d' % (self.sec / 60, self.sec % 60), 'GillSans', 20, self.bounds.w - 32, 4, 7)
    if self.follow:
      tint(0, 0, 1, 0.8)
    else:
      tint(0.3, 0.4, 0.5, 0.7)
    image('Typicons48_Relocate', 0, 0, 32, 32)
    if self.god_mode:
      tint(0, 0, 1, 0.8)
    elif self.allow_god_mode:
      tint(0.2, 0.4, 0.5, 0.7)
    else:
      tint(0.7, 0.5, 0.4, 0.2)
    image('Typicons48_Escape', 32, 0, 32, 32)
    tint(*score_color(self.score))
    text('SCORE', 'GillSans', 10, c.x, 12, 2)
    text('%d' % math.ceil(self.score), 'GillSans', 18, c.x, 12, 8)
    if 0 < prtcl.x + c.x - self.gold_x < 32 and 0 < prtcl.y + c.y - self.gold_y < 32:
      sound.play_effect('Ding_3')
      self.score += 1
      grid_pt = Point(prtcl.x + c.x, prtcl.y + c.y)
      grid_pt.x -= grid_pt.x % 32
      grid_pt.y -= grid_pt.y % 32
      self.gold_x = random.randint(-40, 40) * 32 + grid_pt.x
      self.gold_y = random.randint(-40, 40) * 32 + grid_pt.y
      path = gen_path(grid_pt, Point(self.gold_x, self.gold_y))
      ln = len(self.path)
      #self.path[ln:ln+len(path)] = path
      self.path = path

  def touch_began(self, touch):
    pass

  def touch_moved(self, touch):
    if self.frozen:
      return
    loc = touch.location
    ploc = touch.prev_location
    dx = ploc.x - loc.x
    dy = ploc.y - loc.y
    vc = self.view_center
    self.view_center = Point(vc.x + dx, vc.y + dy)

  def touch_ended(self, touch):
    if self.frozen and not self.frozen_manual:
      return
    x, y = touch.location
    w = self.bounds.w
    if y < 32:
      if x < 32:
        self.follow = not self.follow
      elif x < 64:
        self.god_mode = self.allow_god_mode and not self.god_mode
      elif x > w-32:
        self.frozen = not self.frozen
        self.frozen_manual = self.frozen
    elif y < 64:
      if x > w-32:
        mml = MainMenuLayer(self._scene)
        self._scene.set_layer(mml)
    elif self.frozen_manual:
      self.frozen = self.frozen_manual = False

  def end(self, why, good_score=6):
    gs = float(good_score)
    if _VERBOSE:
      console.set_color(0.6, 0.2, 0)
      print 'GAME OVER'
      console.set_color(0.2, 0, 0.4)
      print why
      sc = score_color(self.score)
      console.set_color(*sc)
      print 'score:', int(math.ceil(self.score))
    self.frozen = True
    self._scene.set_layer(GameOverLayer(self._scene, self), False)

class MainMenuLayer (SceneLayer):
  def __init__(self, parent_scene):
    SceneLayer.__init__(self, parent_scene)

  def setup(self):
    c = self.bounds.center()
    start_btn = Button(Rect(c.x - 128, c.y + 64, 256, 32), 'Start Game')
    start_btn.action = lambda: self._scene.set_layer(GameLayer(self._scene, None), gcollect=True)
    self.add_layer(start_btn)
    opt_btn = Button(Rect(c.x - 128, c.y + 32, 256, 32), 'Options...')
    opt_btn.action = lambda: self._scene.set_layer(OptionsLayer(self._scene), False)
    self.add_layer(opt_btn)
    update_btn = Button(Rect(c.x - 128, c.y - 16, 256, 32), 'Check for Updates')
    update_btn.action = lambda: self._scene.set_layer(InstallPathsGame.StartLayer(self._scene, MainMenuLayer))
    self.add_layer(update_btn)
    quit_btn = Button(Rect(c.x - 128, c.y - 48, 256, 32), 'Quit Game')
    quit_btn.action = sys.exit
    self.add_layer(quit_btn)
    path = []
    for x in (0,4,6,9,12,14,16,18):
      for y in xrange(5):
        path.append((32 * x,  32 * y))
    for x in (1,2,5,8,10,13,17):
      for y in (2,4):
        path.append((32 * x,  32 * y))
    for x, y in ((2,3),(17,0)):
      path.append((32 * x,  32 * y))
    for x, y in ((8,2),(10,2),(13,4),(16,1),(18,3)):
      path.remove((32 * x,  32 * y))
    self.path = path
    self.gold = Point(32 * 18, 32 * 4)

  def draw(self, a=1):
    self.layer_compat()
    background(0, 0, 0)
    vc = Point(160 * math.sin(self.t / 1.0 - math.pi / 2.0) + 128, 32 * math.cos(self.t / 1.0 - math.pi / 2.0) - 176)
    #vc = Point(128, -176)
    bgx = 0.9*vc.x % 62
    bgy = 0.9*vc.y % 62
    fill(0.1, 0.1, 0.125)
    no_stroke()
    no_tint()
    for i in xrange(9):
      for j in xrange(9):
        for k in (0, 1):
          rect(31 * (2 * i + k) - bgx, 31 * (2 * j + k) - bgy, 31, 31)
    fill(0.8, 1, 0.9, 0.7)
    for pt in self.path:
      rect(pt[0] - vc.x, pt[1] - vc.y, 32, 32)
    fill(0.9, 0.7, 0.1, 0.9)
    rect(self.gold.x - vc.x, self.gold.y - vc.y, 32, 32)
    Layer.draw(self, a)

def load_options(opt_filename=None):
  if opt_filename is None:
    opt_filename = os.path.join(DYNDIR, 'Options.json')
  import json
  with open(opt_filename) as fp:
    return json.load(fp)

def save_options(opts=None, opt_filename=None):
  if opts is None:
    opts = options
  if opt_filename is None:
    opt_filename = os.path.join(DYNDIR, 'Options.json')
  import json
  with open(opt_filename, 'w') as fp:
    json.dump(opts, fp, indent=2, separators=(',', ': '))

class OptionsLayer (SceneLayer):
  def __init__(self, parent_scene):
    SceneLayer.__init__(self, parent_scene)

  def setup(self):
    cx, cy = self.bounds.center()
    
    dark = Layer(self.bounds)
    dark.background = Color(0, 0, 0, 0.5)
    self.add_layer(dark)
    dark2 = Layer(Rect(cx-160, cy-170, 320, 340))
    dark2.background = Color(0.08, 0.1, 0.09, 0.8)
    self.add_layer(dark2)
    
    self.sliders = {}
    self.draw_funcs = []
    
    def add_slider(dcy, start, stop, step, opt_key, disp_name, val_disp_func):
      slider = Slider(Rect(cx-144, cy+dcy, 288, 32), start, stop, step, options[opt_key])
      self.sliders[opt_key] = slider
      self.add_layer(slider)
      
      default_btn = Button(Rect(cx-36, cy+dcy+26, 36, 16), 'Default')
      revert_btn = Button(Rect(cx, cy+dcy+26, 36, 16), 'Revert')
      default_btn.alpha = 0
      revert_btn.alpha = 0
      def set_value(value):
        slider.value = value
      default_btn.action = lambda: set_value(defaults[opt_key])
      revert_btn.action = lambda: set_value(options[opt_key])
      self.add_layer(default_btn)
      self.add_layer(revert_btn)
      
      def draw_func():
        tint(1, 1, 0.9)
        text(disp_name, 'GillSans', 18, cx-136, cy+dcy+22, 9)
        text(val_disp_func(slider.value), 'GillSans', 16, cx+136, cy+dcy+22, 7)
        default_btn.alpha = 0 if slider.value == defaults[opt_key] else 1
        revert_btn.alpha = 0 if slider.value == options[opt_key] else 1
      self.draw_funcs.append(draw_func)
    
    add_slider(120, 0, 3, 0.1, 'sensitivity', 'Sensitivity', lambda t: '%1.1f' % t)
    add_slider(70, 0, 600, 15, 'time_sec', 'Time', lambda t: '%d:%02d' % (t / 60, t % 60))
    
    godm_labels = ('DISABLED', 'ALLOWED', 'ON')
    godm_state = options['allow_god_mode']
    godm_btn = Button(Rect(cx-128, cy+20, 256, 32), 'God Mode: ' + godm_labels[godm_state])
    godm_btn.value = godm_state
    self.sliders['allow_god_mode'] = godm_btn
    def godm_action():
      godm_btn.value = state = (godm_btn.value + 1) % 3
      godm_btn.label = 'God Mode: ' + godm_labels[state]
    godm_btn.action = godm_action
    self.add_layer(godm_btn)
    
    cancel_btn = Button(Rect(cx-128, cy-160, 128, 32), 'Cancel')
    cancel_btn.action = lambda: self.return_to_menu(False)
    self.add_layer(cancel_btn)
    done_btn = Button(Rect(cx, cy-160, 128, 32), 'Done')
    done_btn.action = lambda: self.return_to_menu(True)
    self.add_layer(done_btn)

  def draw(self, a=1):
    self.layer_compat()
    Layer.draw(self, a)
    for draw_func in self.draw_funcs:
      draw_func()
  
  def return_to_menu(self, save):
    if save:
      for opt_key, slider in self.sliders.iteritems():
        options[opt_key] = slider.value
      save_options()
    self._scene.set_layer(self._scene.root_layer.sublayers[-2])

def score_color(score, gs=9.0):
  r = g = b = 0
  if score < 0:
    pass
  elif score <= gs:
    r = 1 - score / gs
    g = score / gs
  elif score <= 2 * gs:
    g = 2 - score / gs
    b = score / gs - 1
  else:
    b = 1
  return r, g, b

class GameOverLayer (SceneLayer):
  def __init__(self, parent_scene, frozen_game):
    self.game = frozen_game
    SceneLayer.__init__(self, parent_scene)

  def setup(self):
    c = self.bounds.center()
    dark = Layer(self.bounds)
    dark.background = Color(0, 0, 0, 0.8)
    self.add_layer(dark)
    btn = Button(Rect(c.x - 128, c.y - 80, 256, 32), 'Main Menu')
    btn.action = lambda: self._scene.set_layer(MainMenuLayer(self._scene))
    self.add_layer(btn)
    self.score_tint = Color(*score_color(self.game.score))

  def draw(self, a=1):
    self.layer_compat()
    Layer.draw(self, a)
    c = self.bounds.center()
    tint(1, 1, 1, 0.8)
    text('GAME OVER!', 'AvenirNextCondensed-UltraLight', 64, c.x, c.y, 8)
    st = self.score_tint
    tint(st.r, st.g, st.b, 0.8)
    text('score: %d' % math.ceil(self.game.score), 'GillSans', 40, c.x, c.y, 2)



class Slider (Layer):
  def __init__(self, frame, start, stop, step=1, value=None):
    Layer.__init__(self, frame)
    self.start = start
    self.stop = stop
    self.step = step
    if value is None:
      value = start
    self.value = value
    self.touchct = 0
  
  def draw(self, a=1):
    Layer.draw(self, a)
    f = self.frame
    sl = self.superlayer
    x, y = sl.convert_to_screen(f.origin())
    touchct = self.touchct
    no_stroke()
    if touchct:
      fill(1, 1, 0.9, 0.7)
    else:
      fill(1, 1, 1, 0.4)
    rect(x, y + 0.5*f.h - 8, f.w, 16)
    if touchct:
      fill(0.9, 0.7, 0.1, 0.8)
    else:
      fill(1, 1, 0.8, 0.5)
    start = self.start
    stop = self.stop
    hdlx = ((f.w - 16) * (self.value - start) / (stop - start)) + x
    rect(hdlx, y + 0.5*f.h - 8, 16, 16)
  
  def set_value(self, tx):
    f = self.frame
    start = self.start
    stop = self.stop
    value = ((tx - f.x) * (stop - start) / (f.w - 16)) + start
    step = self.step
    value = (value // step) * step
    if value < start:
      value = start
    elif value > stop:
      value = stop
    self.value = value
  
  def touch_began(self, touch):
    self.touchct += 1
    self.set_value(touch.location.x)
  
  def touch_moved(self, touch):
    self.set_value(touch.location.x)
  
  def touch_ended(self, touch):
    self.touchct -= 1

def in_frame(layer, pt):
  return layer.superlayer.convert_from_screen(pt) in layer.frame



def gen_path(src, dst, width=2, start_platform=True):
  x = src.x
  y = src.y
  path = []
  if start_platform:
    for i in xrange(-32 * width, 1 + 32 * width, 32):
      for j in xrange(-32 * width, 1 + 32 * width, 32):
        path.append((x + i, y + j))
  else:
    path.append((x, y))
  endvar = 32 * (width - 1)
  while abs(x - dst.x) > endvar or abs(y - dst.y) > endvar:
    dx = (dst.x - x) * random.random()
    dy = (dst.y - y) * random.random()
    if abs(dx) > abs(dy):
      if dx != 0:
        x += 32 * (width + 1) * dx / abs(dx)
    else:
      if dy != 0:
        y += 32 * (width + 1) * dy / abs(dy)
    for i in (-32, 0, 32):
      for j in (-32, 0, 32):
        path.append((x + i, y + j))
  return path

class Particle (object):
  def __init__(self, x=0, y=0, vx=0, vy=0, m=1):
    super(Particle, self).__init__()
    self.x = x
    self.y = y
    self.vx = vx
    self.vy = vy
    self.m = m

  def tick(self):
    self.x += self.vx
    self.y += self.vy

def main():
  if _VERBOSE:
    console.clear()
    console.set_color(0.2, 0, 0.4)
    print 'running scene'
  run(ParticleScene(MainMenuLayer), PORTRAIT)

_init_options()

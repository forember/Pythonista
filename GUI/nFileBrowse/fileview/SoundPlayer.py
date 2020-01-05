from __future__ import division

from scene import *
from .FileViewWrapper import GenericNTP
from .. import themes

def polyline(*points, **kwargs):
  joint_weight = kwargs['joint_weight']
  joffs = joint_weight / 2
  if len(points) == 1:
    points = points[0]
  it = iter(points)
  try:
    first = tuple(it.next())
  except StopIteration:
    return
  prev = first
  def fill_joint():
    if joint_weight:
      ellipse(prev[0]-joffs, prev[1]-joffs, joint_weight, joint_weight)
  for pt in it:
    pt = tuple(pt)
    if len(pt) == 0:
      pt = first
    line(*prev + pt)
    fill_joint()
    prev = pt
  fill_joint()

class SoundPlayerPane (GenericNTP):
  def __init__(self, frame, player, title='', name=None):
    GenericNTP.__init__(self, frame)
    _theme = themes.cur_theme()
    self.background = _theme.SOUND_BG
    self.player = player
    player.number_of_loops = 0
    self.title = title
    self.name = name
    self.curtime = player.current_time
    self.playing = False
    self.was_playing = False
    self.touch_starts = {}
    self.playpause_down = False
    self.volume = self.player.volume
    self.volume_write = False
  
  def start(self, **kwargs):
    self.sound_play()
    
  def stop(self, duration=0, **kwargs):
    if duration:
      self.volume_write = True
      self.animate('volume', 0, duration, completion=self.sound_stop)
    else:
      self.sound_stop()
    
  def sound_play(self):
    self.player.play()
    self.playing = True
  
  def sound_pause(self):
    self.player.pause()
    self.playing = False
  
  def sound_stop(self):
    self.player.stop()
    self.playing = False
  
  def update(self, dt):
    GenericNTP.update(self, dt)
    
    if self.volume_write:
      self.player.volume = self.volume
    else:
      self.volume = self.player.volume
    
    ncurtime = self.player.current_time
    if self.playing and not self.was_playing and not self.player.number_of_loops and ncurtime + 0.02 < self.curtime and ncurtime >= 0:
      self.sound_stop()
    self.curtime = ncurtime
    
    if self.playing and self.was_playing:
      self.was_playing = False
  
  def draw(self, a=1):
    GenericNTP.draw(self, a)
    
    origin = self.convert_to_screen(Point(0, 0))
    push_matrix()
    translate(origin.x, origin.y)
    
    _theme = themes.cur_theme()
    w, h = self.frame.size()
    cx, cy = w/2, h/2
    curtm = self.player.current_time
    duration = self.player.duration
    volume = self.player.volume
    
    # background
    tint(*_theme.SOUND_IMG_TINT)
    image(_theme.SOUND_IMG, cx-96, cy-64, 192, 192)
    
    # play/pause button
    stroke(*_theme.SOUND_BTN_STROKE)
    btnstrkw = _theme.SOUND_BTN_STROKEW
    stroke_weight(btnstrkw)
    if self.playpause_down:
      fill(*_theme.SOUND_BTN_BG_DOWN)
    else:
      fill(*_theme.SOUND_BTN_BG)
    ellipse(cx-32, 16, 64, 64)
    if self.playing:
      _color = _theme.SOUND_BTN_PLAY_COLOR
      no_stroke()
      fill(*_color)
      rect(cx-16, 32, 12, 32)
      rect(cx+4, 32, 12, 32)
    else:
      _color = _theme.SOUND_BTN_PLAY_COLOR
      _weight = _theme.SOUND_BTN_PLAY_WEIGHT
      stroke(*_color)
      stroke_weight(_weight)
      fill(*_color)
      polyline((cx-8, 32), (cx-8, 64), (cx+16, 48), (), joint_weight=_weight)
    
    # slider theme
    _sld_bg = _theme.SOUND_SLIDER_BG, _theme.SOUND_SLIDER_BG_STROKE, _theme.SOUND_SLIDER_BG_STROKEW
    _sld_fl = _theme.SOUND_SLIDER_FILL, _theme.SOUND_SLIDER_FILL_STROKE, _theme.SOUND_SLIDER_FILL_STROKEW
    _sld_hdl = _theme.SOUND_SLIDER_HANDLE_BG, _theme.SOUND_SLIDER_HANDLE_STROKE, _theme.SOUND_SLIDER_HANDLE_STROKEW
    def _sld(_t):
      fill(*_t[0])
      stroke(*_t[1])
      stroke_weight(_t[2])
    
    # time slider
    _sld(_sld_bg)
    rect(0.1*w, 105, 0.8*w, 8)
    _sld(_sld_fl)
    rect(0.1*w, 105, 0.8*w * curtm / duration, 8)
    _sld(_sld_hdl)
    ellipse((0.1*w - 9) + (0.8*w) * curtm / duration, 100, 18, 18)
    
    # time text
    _tmfnt = _theme.SOUND_TIME_FONT
    tint(*_theme.SOUND_ETIME_TINT)
    text(' {:02d}:{:02d}'.format(int(curtm // 60), int(curtm % 60)), *_tmfnt, x=0, y=95, alignment=3)
    tint(*_theme.SOUND_RTIME_TINT)
    text('-{:02d}:{:02d} '.format(int((duration - curtm) // 60), int((duration - curtm) % 60)), *_tmfnt, x=w, y=95, alignment=1)
    
    # volume slider
    _sld(_sld_bg)
    rect(0.1*w, h - 65, 0.8*w, 8)
    _sld(_sld_fl)
    rect(0.1*w, h - 65, 0.8*w * volume, 8)
    _sld(_sld_hdl)
    ellipse((0.1*w - 9) + (0.8*w) * volume, h - 70, 18, 18)
    
    # volume label
    tint(*_theme.SOUND_VOLUME_TINT)
    text(_theme.SOUND_VOLUME_TEXT, *_theme.SOUND_VOLUME_FONT, x=cx, y=h - 75, alignment=2)
    
    # title
    tint(*_theme.SOUND_TITLE_TINT)
    text(self.title, *_theme.SOUND_TITLE_FONT, x=cx, y=h - 35, alignment=5)
    
    pop_matrix()
    
  def touch_began(self, touch):
    self.touch_starts[touch.touch_id] = touch.location.as_tuple()
    tsx, tsy = touch.location
    tx, ty = tsx, tsy
    w, h = self.frame.size()
    if tsy < 90:
      self.playpause_down = True
    elif tsy < 125:
      self.was_playing = self.playing
      self.sound_pause()
      duration = self.player.duration
      self.player.current_time = (tx - (0.2*w - 9)) * duration / (0.8*w)
    elif tsy > h - 40:
      pass
    elif tsy > h - 90:
      volume = (tx - (0.2*w - 9)) / (0.8*w)
      self.player.volume = max(0, min(1, volume))
    
  def touch_moved(self, touch):
    tsx, tsy = self.touch_starts[touch.touch_id]
    tx, ty = touch.location
    w, h = self.frame.size()
    if tsy < 90:
      self.playpause_down = ty < 95
    elif tsy < 125:
      w = self.frame.w
      duration = self.player.duration
      self.player.current_time = (tx - 0.2*w) * duration / (0.8*w)
    elif tsy > h - 40:
      pass
    elif tsy > h - 90:
      volume = (tx - (0.2*w - 9)) / (0.8*w)
      self.player.volume = max(0, min(1, volume))
    
  def touch_ended(self, touch):
    tsx, tsy = self.touch_starts[touch.touch_id]
    tx, ty = touch.location
    w, h = self.frame.size()
    if tsy < 90:
      self.playpause_down = False
      if ty < 95:
        if self.playing:
          self.sound_pause()
        else:
          self.sound_play()
    elif tsy < 125:
      if self.was_playing:
        self.sound_play()

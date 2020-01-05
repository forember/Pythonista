# -*- coding: utf-8 -*-

from __future__ import division

import math
from scene import *
from .FileViewWrapper import close_view
from ..scenefont import Font, get_charsize_map
from .. import themes

def gen_displns(frame, iterlines, chrszmap, do_indent=False, tabsize=8):
  from UnicodeBreakAfter import OP, QU, PR
  nbrcls = '\\w'+OP+QU+PR
  import re
  break_re = re.compile(u'([^{0}]+)[{0}]*$'.format(nbrcls), re.UNICODE)
  
  if do_indent:
    ln_cont_chr = u'\u25E3' if chrszmap.font.name == 'DejaVuSansMono' else u'\u25FA'
  indent = ''
  
  from unicodedata import normalize
  for ln in iterlines:
    ln = normalize('NFKC', unicode(ln.expandtabs(tabsize))).rstrip()
    if not ln:
      yield ''
      continue 
    if do_indent:
      indent = ' ' * (len(ln) - len(ln.lstrip())) + ln_cont_chr
    i = 0
    w = 0
    while i < len(ln):
      c = ln[i]
      cw = chrszmap[c][0]
      if math.isnan(cw):
        cw = 0
      w += cw
      if w > frame.w:
        m = break_re.search(ln[:i])
        if m:
          bri = m.end(1)
        else:
          bri = i
        displn = ln[:bri].rstrip()
        if m and not displn:
          bri = i
          displn = ln[:bri].rstrip()
        yield displn
        ln = indent + ln[bri:].lstrip()
        i = -1
        w = 0
      i += 1
    if ln != indent:
      yield ln
      
class DisplayLines (object):
  __slots__ = 'iter_displns', 'displns', 'loading'
  
  def __init__(self, iter_displns):
    self.iter_displns = iter_displns
    self.displns = []
    self.loading = True
    
  def update(self, n=16):
    if self.loading:
      for x in xrange(n):
        try:
          ln = self.iter_displns.next()
          self.displns.append(ln)
        except StopIteration:
          self.loading = False
          break
        
  def __getitem__(self, key):
    it = self.iter_displns
    nlns = len(self.displns)
    from itertools import islice
    if isinstance(key, slice):
      if key.stop < 0:
        self.displns.extend(it)
      elif key.stop > nlns:
        self.displns.extend(islice(it, key.stop - nlns))
    else:
      if key < 0:
        self.displns.extend(it)
      elif key >= nlns:
        self.displns.extend(islice(it, 1 + key - nlns))
    return self.displns[key]
    
  def __len__(self):
    return len(self.displns)

class PageTextPane (Layer):
  def __init__(self, frame, iterlines, font=Font('Helvetica', 16), color=None, do_indent=False, tabsize=8):
    Layer.__init__(self, frame)
    _theme = themes.cur_theme()
    self.background = _theme.TEXTPANE_BG
    if color is None:
      color = _theme.TEXTPANE_TINT
    self.tint = color
    
    chrszmap = get_charsize_map(font)
    self.font = chrszmap.font
    self.lineh = chrszmap[' '][1]
    self.lnsppg = int(frame.h // self.lineh) - 1
    disp_frame = Rect(*frame)
    disp_frame.w -= 4 + 1.25 * _theme.TEXTPANE_TEXT_X
    self.displns = DisplayLines(gen_displns(disp_frame, iterlines, chrszmap, do_indent, tabsize))
    
    self.npages = int(math.ceil(len(self.displns) / self.lnsppg))
    
    self.page_n = 1
    self.update_page()
    
    self.waiting = True
    
  def set_frame(self, frame, **kwargs):
    oldsz = self.frame.size()
    newsz = frame.size()
    self.frame = frame
    font = (self.font.name, self.font.size * (newsz.w / oldsz.w))
    
    chrszmap = get_charsize_map(font)
    self.font = chrszmap.font
    self.lineh = chrszmap[' '][1]
    self.lnsppg = int(frame.h // self.lineh) - 1
    
    old_npages = self.npages
    self.npages = int(math.ceil(len(self.displns) / self.lnsppg))
    
    self.page_n = int(self.page_n * (self.npages / old_npages))
    if self.page_n < 1:
      self.page_n = 1
    elif self.page_n > self.npages:
      self.page_n = self.npages
    self.update_page()
    
  def start(self, **kwargs):
    self.waiting = False
    
  def stop(self, **kwargs):
    self.waiting = True
    
  def update(self, dt):
    if self.waiting:
      return
    Layer.update(self, dt)
    loading = self.displns.loading
    self.displns.update()
    if loading:
      self.npages = int(math.ceil(len(self.displns) / self.lnsppg)) + self.displns.loading
    
  def draw(self, a=1):
    Layer.draw(self, a)
    f = self.frame
    push_matrix()
    translate(*self.superlayer.convert_to_screen(f.origin()))
    tint(*self.tint)
    _theme = themes.cur_theme()
    text(self.page, *self.font, x=_theme.TEXTPANE_TEXT_X, y=f.h, alignment=3)
    if self.displns.loading:
      _theme = themes.cur_theme()
      tint(*_theme.TEXTPANE_PAGED_LOAD)
    text('{:d} / {:d}'.format(self.page_n, self.npages), *self.font, x=f.w / 2, alignment=8)
    pop_matrix()
    
  def update_page(self):
    endi = self.page_n * self.lnsppg
    self.page = '\n'.join(self.displns[endi - self.lnsppg:endi])
    
  def touch_ended(self, touch):
    x, y = self.superlayer.convert_from_screen(touch.location)
    x -= self.frame.x
    y -= self.frame.y
    w, h = self.frame.size()
    old_page_n = self.page_n
    
    if x < 0.3 * w or y > 0.7 * h:
      self.page_n -= 1
    if x > 0.6 * w or y < 0.3 * h:
      self.page_n += 1
    
    if self.page_n < 1:
      self.page_n = 1
    elif self.page_n > self.npages:
      self.page_n = self.npages
    
    if self.page_n != old_page_n:
      self.update_page()
  
  def close_view(self):
    close_view(self)

class ScrollTextPane (Layer):
  def __init__(self, frame, iterlines, font=Font('Helvetica', 16), color=None, do_indent=False, tabsize=8):
    Layer.__init__(self, frame)
    _theme = themes.cur_theme()
    self.background = _theme.TEXTPANE_BG
    if color is None:
      color = _theme.TEXTPANE_TINT
    self.tint = color
    
    chrszmap = get_charsize_map(font)
    self.font = chrszmap.font
    self.lineh = chrszmap[' '][1]
    self.lnsppg = int(frame.h // self.lineh) - 1
    disp_frame = Rect(*frame)
    disp_frame.w -= 4 + 1.25 * _theme.TEXTPANE_TEXT_X
    self.displns = DisplayLines(gen_displns(disp_frame, iterlines, chrszmap, do_indent, tabsize))
    
    self.pageh = self.lineh * self.lnsppg
    
    self.view_y = -1
    self.touch_dy = 0
    self.velocity = 0
    self.consective_swipes = 0
    
    self.waiting = True
    
  def set_frame(self, frame):
    oldsz = self.frame.size()
    newsz = frame.size()
    self.frame = frame
    font = (self.font.name, self.font.size * (newsz.w / oldsz.w))
    
    chrszmap = get_charsize_map(font)
    self.font = chrszmap.font
    old_lineh = self.lineh
    self.lineh = chrszmap[' '][1]
    self.lnsppg = int(frame.h // self.lineh) - 1
    
    self.pageh = self.lineh * self.lnsppg
    
    self.view_y *= self.lineh / old_lineh
    self.touch_dy = 0
    self.velocity = 0
    self.consective_swipes = 0
    
  def start(self, **kwargs):
    self.waiting = False
    
  def stop(self, **kwargs):
    self.waiting = True
    
  def update(self, dt):
    if self.waiting:
      return
    Layer.update(self, dt)
    self.displns.update()
    
    if self.touch_dy:
      self.view_y += self.touch_dy
      self.velocity = 0.5 * (self.velocity + (self.touch_dy / dt))
      self.touch_dy = 0
    elif abs(self.velocity) < 4:
      self.velocity = 0
    else:
      if abs(self.velocity) > 100:
        self.velocity *= 0.93
      else:
        self.velocity *= 0.62
      self.view_y += self.velocity * dt
      if abs(self.velocity) < 1000:
        self.consective_swipes = 0
      elif self.consective_swipes == 0:
        self.consective_swipes = 1
    
    btmy = 1 + self.frame.h - self.lineh*len(self.displns)
    if self.view_y > -1:
      self.view_y = -1
    elif self.view_y < btmy:
      self.view_y = btmy
    if self.view_y > -1:
      self.view_y = -1
    
  def draw(self, a=1):
    _theme = themes.cur_theme()
    Layer.draw(self, a)
    lns = self.displns
    font = self.font
    f = self.frame
    lnh = self.lineh
    pgh = self.pageh
    topi = int(-self.view_y // lnh)
    txti = topi + 1
    btmi = txti + self.lnsppg
    topspc = self.view_y + txti*lnh
    txt = '\n'.join(lns[txti:btmi])
    btmspc = f.h - (topspc + pgh)
    ox, oy = self.superlayer.convert_to_screen(f.origin())
    push_matrix()
    translate(ox, oy + f.h)
    tint(*self.tint)
    if topspc > 2:
      try:
        text(lns[topi], font.name, font.size * topspc / lnh, _theme.TEXTPANE_TEXT_X, 0, 3)
      except IndexError:
        pass
    text(txt, font.name, font.size, _theme.TEXTPANE_TEXT_X, -topspc, 3)
    if btmspc > 2:
      btmscale = (btmspc / lnh) if btmspc < lnh else 1
      try:
        text(lns[btmi], font.name, font.size * btmscale, _theme.TEXTPANE_TEXT_X, btmspc-f.h, 3)
      except IndexError:
        pass
    if self.displns:
      # draw scrollbar
      if self.displns.loading:
        fill(*_theme.TEXTPANE_SCROLL_LOAD)
      else:
        fill(*_theme.TEXTPANE_SCROLL_NORM)
      _stroke = _theme.TEXTPANE_SCROLL_STROKE
      stroke(*_stroke)
      _strokew = _theme.TEXTPANE_SCROLL_STROKEW
      stroke_weight(_strokew)
      sbf = f.h / (lnh * len(self.displns))
      rect(f.w - 3, self.view_y * sbf, 2.5, -pgh * sbf)
    pop_matrix()
    
  def touch_began(self, touch):
    if abs(self.velocity) >= 1000:
      self.consective_swipes += 1
    
  def touch_moved(self, touch):
    dy = touch.prev_location.y - touch.location.y
    if self.consective_swipes >= 3:
      dy *= 3
    self.touch_dy += dy
  
  def close_view(self):
    close_view(self)

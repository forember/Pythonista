from scene import render_text
from collections import namedtuple
from weakref import WeakValueDictionary

Font = namedtuple('Font', 'name size')

def get_charsize(font, char):
  return get_charsize_map(font)[char]
  
def get_charsize_map(font):
  return _chrsz_maps[font]

def truncate_text(text, font, max_width, ellipsis=u'\u2026'):
  chrszmap = get_charsize_map(font)
  tmw = max_width - chrszmap[ellipsis][0]
  w = 0
  tei = None
  for i, c in enumerate(text):
    w += chrszmap[c][0]
    if tei is None and w > tmw:
      tei = i
    if w > max_width:
      break
  else:
    return text
  return text[:tei] + ellipsis
  
class _CharSizeMaps (WeakValueDictionary):
  __slots__ = ()
  
  def __getitem__(self, key):
    if key not in self:
      self[key] = chrszmap = _CharSizeMap(key)
      return chrszmap
    return WeakValueDictionary.__getitem__(self, key)
    
  def __setitem__(self, key, value):
    return WeakValueDictionary.__setitem__(self, Font._make(key), value)
    
_chrsz_maps = _CharSizeMaps()
  
class _CharSizeMap (dict):
  __slots__ = '__weakref__', 'font'
  
  def __init__(self, font):
    dict.__init__(self)
    self.font = Font._make(font)
    
  def __getitem__(self, key):
    if key not in self:
      self[key] = render_text(key, *self.font)[1]
    return dict.__getitem__(self, key)

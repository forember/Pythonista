import re

class Error (Exception):
  filename = '<string>'

class SyntaxError (Error):
  def __init__(self, s, index, msg='invalid syntax'):
    Error.__init__(self, msg)
    self.s = s
    self.index = index
    self.msg = msg
  
  def __str__(self):
    s = self.s
    index = self.index
    lnstart = s.rfind('\n', 0, index) + 1
    lnend = s.find('\n', index)
    line = s[lnstart:lnend]
    offs = index - lnstart
    lineno = s.count('\n', 0, index) + 1
    return '{msg}\n\nFile "{fnm}", line {lineno}\n    {line}\n    {offs}^'.format(msg=self.msg, fnm=self.filename, lineno=lineno, line=line, offs=' '*offs)

_version = 0

magic_ver_re = re.compile(
    r'\?dsmap\s+(?P<VERSION>\d+)\?')

def dsmap_eval(s, filename='<string>', raise_errors=False):
  try:
    match = magic_ver_re.match(s)
    if match:
      version = int(match.group('VERSION'))
      if version > _version:
        raise Error, 'version'
      index = match.end()
    else:
      version = None
      index = 0
    return _dsmap_eval(s, index)[0]
  except Error as e:
    e.filename = filename
    if raise_errors:
      raise e
    else:
      import traceback
      traceback.print_exc()
      return {}
  
_space_re = re.compile(r'\s*')

def _dsmap_eval(s, index):
  space_match = _space_re.match(s, index)
  index = space_match.end()
  for datt in _datatypes:
    if datt[0].match(s, index):
      return datt[1](s, index)
  else:
    raise SyntaxError, (s, index)


# === Datatypes ===

_datatypes = []

def _add_datatype(magic_re, func):
  _datatypes.append((re.compile(magic_re), func))

# DATATYPE: comment

_datt_comment_re = re.compile(r'#.*$', re.MULTILINE)

def _datt_comment(s, index):
  match = _datt_comment_re.match(s, index)
  if not match:
    raise SyntaxError, (s, index)
  index = match.end()
  return _dsmap_eval(s, index)

_add_datatype(r'#', _datt_comment)

# DATATYPE: int

_datt_int_re = re.compile(r'[-+]?\d+')

def _datt_int(s, index):
  try:
    match = _datt_int_re.match(s, index)
    if not match:
      raise SyntaxError, (s, index, 'invalid integer')
    value = int(match.group())
    index = match.end()
    return value, index
  except ValueError as e:
    raise SyntaxError, (s, index, 'invalid integer')

_add_datatype(r'[-+]?\d', _datt_int)

# DATATYPE: str

_datt_str_re = re.compile(
    r'"(([^"]|\\")*)"')

def _datt_str(s, index):
  try:
    match = _datt_str_re.match(s, index)
    if not match:
      raise SyntaxError, (s, index, 'invalid string')
    enc = 'unicode_escape'
    value = match.group(1).decode(enc)
    index = match.end()
    return value, index
  except UnicodeDecodeError as e:
    raise SyntaxError, (s, index, 'invalid string: ' + str(e))

_add_datatype(r'"', _datt_str)

# DATATYPE: dict

_datt_dict_end_re = re.compile(r'\s*}')
_datt_dict_kvsep_re = re.compile(r'\s*:')
_datt_dict_isep_re = re.compile(r'\s*;')

def _datt_dict(s, index):
  try:
    end_re = _datt_dict_end_re
    kvsep_re = _datt_dict_kvsep_re
    isep_re = _datt_dict_isep_re
    if s[index] != '{':
      raise SyntaxError, (s, index, 'invalid dict: expected "{"')
    index += 1
    value = dict()
    while index < len(s):
      end_match = end_re.match(s, index)
      if end_match:
        index = end_match.end()
        break
      k, index = _dsmap_eval(s, index)
      kvsepm = kvsep_re.match(s, index)
      if not kvsepm:
        raise SyntaxError, (s, index, 'invalid dict: expected ":"')
      index = kvsepm.end()
      v, index = _dsmap_eval(s, index)
      isepm = isep_re.match(s, index)
      if not isepm:
        raise SyntaxError, (s, index, 'invalid dict: expected ";"')
      index = isepm.end()
      value[k] = v
    else:
      raise IndexError
    return value, index
  except IndexError as e:
    raise SyntaxError, (s, index, 'invalid dict: ' + str(e))

_add_datatype(r'{', _datt_dict)

# =================

from ..autoview import args


AUTOTYPE_PRIORITY = 0x7fffffff


def AUTOTYPE_FUNC(browser, file_path, fileobj=None, ext='', **kwargs):
  if fileobj is None:
    fileobj = open(file_path)
  import os
  filename = os.path.basename(file_path)
  ds = browser.dsmap.get(filename, {})
  paged = ds.get('PAGED', 0)
  read = ds.get('READ', 0)
  is_py_code = ds.get('IS_PY', ext == '.py')
  from .. import TextPane
  if paged:
    NTP = TextPane.PageTextPane
  else:
    NTP = TextPane.ScrollTextPane
  from ... import themes
  _theme = themes.cur_theme()
  if read:
    font = _theme.FILE_READ_FONT
  elif is_py_code:
    font = _theme.FILE_PY_FONT
  else:
    font = _theme.FILE_TEXT_FONT
  do_indent = is_py_code
  tabsize = 2 if is_py_code else 8
  def iterlines():
    import sys
    encoding = sys.getfilesystemencoding()
    ln = fileobj.readline()
    try:
      ln = ln.decode(encoding)
    except UnicodeDecodeError:
      encoding = 'latin_1'
      ln = ln.decode(encoding)
    yield ln.replace('\0', '')
    for ln in fileobj:
      yield ln.decode(encoding, 'replace').replace('\0', '')
  return NTP, args(iterlines(), font, None, do_indent, tabsize), 4

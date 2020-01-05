import os

from .. import themes


def args(*args, **kwargs):
  return args, kwargs


def view_file(browser, file_path, fileobj=None):
  '''Attempt to open the file for viewing.
  
  Display an error message if the file could not successfully be opened for viewing.'''
  try:
    return _view_file(browser, file_path, fileobj)
  except IOError, why:
    errstr = '=!!= ERROR =!!=\n\nThe file could not be opened: ' + str(why)
  except Exception, why:
    errstr = '=!!= ERROR =!!=\n\nThe file viewer encoutered a problem: ' + str(why)
  import traceback
  traceback.print_exc()
  from . import TextPane
  _theme = themes.cur_theme()
  return TextPane.PageTextPane, args(errstr.splitlines(), _theme.FILE_ERROR_FONT, _theme.FILE_ERROR_TINT), 2
  
  
def _view_file(browser, file_path, fileobj=None):
  filename = os.path.basename(file_path)
  title, ext = os.path.splitext(filename)
  import autotypes
  for autotype in autotypes.autotypes.itervalues():
    r = autotype.AUTOTYPE_FUNC(browser, file_path, fileobj=fileobj, filename=filename, title=title, ext=ext)
    if r is not None:
      return r

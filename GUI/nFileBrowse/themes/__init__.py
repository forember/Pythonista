def load_theme():
  global _theme
  from .. import FileBrowseOpts as _opts
  from importlib import import_module
  module_name = '.' + _opts.theme_name
  _theme = import_module(module_name, __package__)

load_theme()

def cur_theme():
  return _theme

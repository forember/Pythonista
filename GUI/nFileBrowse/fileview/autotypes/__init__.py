def _load_modules(path, package=None):
  import pkgutil
  modules = {}
  prefix = '' if package is None else package + '.'
  for importer, name, ispkg in pkgutil.iter_modules(path, prefix):
    loader = importer.find_module(name)
    modules[name] = loader.load_module(name)
  return modules


def _sorted_autotypes(modules):
  from collections import Mapping, OrderedDict
  if isinstance(modules, Mapping):
    iteritems = modules.iteritems()
  else:
    iteritems = ((module.__name__, module) for module in modules)
  isautotype = lambda t: hasattr(t[1], 'AUTOTYPE_PRIORITY') and hasattr(t[1], 'AUTOTYPE_FUNC')
  autotype_items = filter(isautotype, iteritems)
  sortkey = lambda t: t[1].AUTOTYPE_PRIORITY
  autotypes = OrderedDict(sorted(autotype_items, key=sortkey))
  return autotypes


def _load_autotypes(path):
  return _sorted_autotypes(_load_modules(path, __package__))


def reload_autotypes():
  global builtin_autotypes, plugin_autotypes, autotypes
  from ...plugins import fileview_autotypes as plugin_pkg
  builtin_autotypes = _load_autotypes(__path__)
  plugin_autotypes = _load_autotypes(plugin_pkg.__path__)
  autotypes = builtin_autotypes.copy()
  autotypes.update(plugin_autotypes)
  autotypes = _sorted_autotypes(autotypes)


reload_autotypes()

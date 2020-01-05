from __future__ import division
import scene, math, os
from .. import nfbdirs

def wavg_color(*colors):
  wsum = math.fsum(zip(*colors)[0])
  return scene.Color(*[math.fsum(xs) / wsum for xs in zip(*[[w*x for x in c] for w, c in colors])])

def scale_if_retina(path, scale=None, check_exist=True):
  if scale is None:
    scale = scene.get_screen_scale()
  if scale > 1:
    spath, ext = os.path.splitext(path)
    spath += '@2x' + ext
    if not check_exist or os.path.exists(spath):
      return spath
  return path

def load_app_img(name, do_scale=True):
  path = os.path.join(nfbdirs.PYTHONISTA, name)
  if do_scale:
    path = scale_if_retina(path)
  return scene.load_image_file(path)

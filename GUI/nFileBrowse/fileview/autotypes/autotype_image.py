from ..autoview import args

from PIL import Image

Image.init()


AUTOTYPE_PRIORITY = 0x5fffffff


def AUTOTYPE_FUNC(browser, file_path, ext='', **kwargs):
  if ext not in Image.EXTENSION:
    return
    
  import scene
  from ... import nfbdirs
  
  icon_path = nfbdirs.to_treepath(file_path) + '.png'
  img = scene.load_image_file(icon_path)
  is_icon = bool(img)
  if not img:
    img = scene.load_image_file(file_path)
  if not img:
    return
    
  iconl = browser.cur_iconl
  browser.cur_iconl = None
  from ..ImageView import ImageViewPane
  return ImageViewPane, args(img, file_path, is_icon=is_icon, iconl=iconl), 3

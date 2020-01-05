import sys
sys.modules.pop('nFileBrowse.' 'FileBrowseLoad', None)
from . import FileBrowseLoad
FileBrowseLoad.clear_nfb_sys_modules()
from . import FileBrowseOpts as _opts

__all__ = FileBrowseLoad.NFB_MODULE_NAMES

def main():
  FileBrowseLoad.main()

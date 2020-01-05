def main():
  print '## nFileBrowse Backup Script ##'
  import os, shutil
  curdir = os.path.abspath('.')
  dirname, basename = os.path.split(curdir)
  if not basename or basename == '.':
    curdir = dirname
  basename = os.path.basename(curdir)
  docsdir = os.path.dirname(curdir)
  zolddir = os.path.join(docsdir, 'zOld')
  bksdir = os.path.join(zolddir, 'nFileBrowse_backups')
  bkdir = os.path.join(bksdir, '-tmp_nfb_bk.d')
  print 'creating temporary backup directory...'
  os.mkdir(bkdir)
  print '   done'
  nfbdir = os.path.join(bkdir, basename)
  
  def ignorefunc(path, names):
    relpath = os.path.relpath(path, curdir)
    print '  @ ' + relpath
    ignore = []
    for name in names:
      if name.startswith('--'):
        ignore.append(name)
      elif name.endswith('.pyc') and name[:-1] in names:
        ignore.append(name)
    return ignore
  
  print 'copying nFileBrowse package directory...'
  shutil.copytree(curdir, nfbdir, ignore=ignorefunc)
  print '   done'
  xpath = curdir + 'X.py'
  print 'copying launch script...'
  if os.path.exists(xpath):
    shutil.copy2(xpath, os.path.join(bkdir, os.path.basename(xpath)))
    print '   done'
  else:
    print '  ! launch script not found'
    print '  ! continuing w/o launch script'
  """dyndir = os.path.join(nfbdir, '-dyn')
  print 'removing dynamic data...'
  shutil.rmtree(dyndir)
  print '   done'
  print 'removing bytecode files (pyc)...'
  for dirpath, dirnames, filenames in os.walk(nfbdir):
    for name in filenames:
      if name.endswith('.pyc') and name[:-1] in filenames:
        pycfile = os.path.join(dirpath, name)
        print '  - ' + os.path.relpath(pycfile, nfbdir)
        os.remove(pycfile)
  print '   done'"""
  import time
  bkzipnm = time.strftime('nfb%Y-%m-%dT%H-%M-%S.zip')
  bkzip = os.path.join(bksdir, bkzipnm)
  print 'archiving to ' + bkzipnm
  shutil.make_archive(bkzip, 'zip', bkdir)
  print '   done'
  print 'deleting temporary backup directory...'
  shutil.rmtree(bkdir)
  print '   done'
  print 'ALL DONE'

if __name__ == '__main__':
  main()

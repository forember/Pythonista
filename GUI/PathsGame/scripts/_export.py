import sys, traceback
sys.excepthook = traceback.print_exception

print '## PathsGame Version Exporter ##'

import os
import collections
import time
import shutil


class Error (Exception):
  pass


_VERFIELDS = ('stage_letter', 'major', 'minor', 'patch', 'release_level', 'release_letter', 'year', 'month', 'day', 'hour', 'minute', 'second')

Version = collections.namedtuple('Version', _VERFIELDS)

_EV_FIELDMAP = dict(zip(_VERFIELDS, xrange(len(_VERFIELDS))))

class EditableVersion (list):
  __slots__ = ()
  
  def __getattr__(self, name):
    if name in _EV_FIELDMAP:
      return self[_EV_FIELDMAP[name]]
    else:
      return list.__getattr__(self, name)
  
  def __setattr__(self, name, value):
    if name in _EV_FIELDMAP:
      self[_EV_FIELDMAP[name]] = value
    else:
      return list.__setattr__(self, name, value)
  
  

def parse_version(s):
  import re
  m = re.match(r'([a-z])(\d+)\.(\d+)\.(\d+)-(d[er][cv]|rev)([a-z])-(\d{6})t(\d{6})$', s, re.IGNORECASE)
  if not m:
    raise ValueError, 'invalid version string'
  g = m.groups()
  return Version(g[0].upper(), int(g[1]), int(g[2]), int(g[3]), g[4].upper(), g[5].upper(), int(g[6][:2])+2000, int(g[6][2:4]), int(g[6][4:]), int(g[7][:2]), int(g[7][2:4]), int(g[7][4:]))

def repr_version(v):
  v4 = v[4].lower()
  if v4[:2] == 'dr':
    v4 = 'dr' + v4[2].upper()
  return '{}{:d}.{:d}.{:03d}-{}{}-{:02d}{:02d}{:02d}t{:02d}{:02d}{:02d}'.format(v[0].lower(), v[1], v[2], v[3], v4, v[5].upper(), v[6]-2000, *v[7:])


def input_options(options, default=0):
  for i, opt in enumerate(options):
    print '{:d}: {}{}'.format(i, opt, ' [default]' if i == default else '')
  while True:
    ri = raw_input('? ')
    if not ri:
      return default
    try:
      i = int(ri)
      if i not in xrange(len(options)):
        raise ValueError
      return i
    except ValueError:
      print '!! Invalid value !!'



_REALFILE = os.path.realpath(__file__)
SCPTDIR = os.path.dirname(_REALFILE)
PATHSDIR = os.path.dirname(SCPTDIR)
VERFILE = os.path.join(PATHSDIR, 'version')

with open(VERFILE) as f:
  VERSTR = f.read()
del f
VERSTR = VERSTR.strip()
VERSION = parse_version(VERSTR)

print '\nCurrent version:'
print '    ' + repr_version(VERSION)

decver = EditableVersion(VERSION)
gmt = time.gmtime()
decver[6:] = gmt[:6]

print '\nSelect an update type:'
update_types = ['Edit (dec)', 'Unstable Release (dev)', 'Release Candidate (drC)', 'Release (rev/drV)', 'QUIT']
utype = input_options(update_types)

is_dec = True
is_dev = False
is_drc = False
is_drv = False
is_rev = False


if utype == 0:
  pass
elif utype == 1:
  is_dev = True
  
  print '\nSelect an revision type:'
  revision_types = ['Revision', 'Patch', 'Minor', 'Major', 'Stage', 'QUIT']
  rtype = input_options(revision_types)
  
  if rtype == 0:
    nrlo = 1 + ord(decver.release_letter)
    if nrlo > ord('Z'):
      print '!! max release letter !!'
      raise SystemExit, 2
    decver.release_letter = chr(nrlo)
  elif rtype == 1:
    decver.patch += 1
  elif rtype == 2:
    decver.minor += 1
  elif rtype == 3:
    decver.major += 1
  elif rtype == 4:
    nslo = 1 + ord(decver.stage_letter)
    if nrlo > ord('Z'):
      print '!! max stage letter !!'
      raise SystemExit, 2
    decver.stage_letter = chr(nslo)
  else:
    raise SystemExit, 1
elif utype == 2:
  is_drc = True
elif utype == 3:
  is_drv = is_rev = True
else:
  raise SystemExit, 1
  
  
decversion = Version(*decver)

expversions = []
if is_dec:
  expversions.append(decversion)
if is_dev:
  decver.release_level = 'DEV'
  expversions.append(Version(*decver))
if is_drc:
  decver.release_level = 'DRC'
  expversions.append(Version(*decver))
if is_drv:
  decver.release_level = 'DRV'
  expversions.append(Version(*decver))
if is_rev:
  decver.release_level = 'REV'
  expversions.append(Version(*decver))

print '\nNew dec version:'
print '    ' + repr_version(decversion)
print '''\
Are you sure you would like to update the
dec to this version and also export the
following versions?'''
for v in expversions:
  print '    ' + repr_version(v)
sure = input_options(['No', 'Yes'])
if not sure:
  raise SystemExit, 1

print '\nUpdating version file...'
with open(VERFILE, 'w') as f:
  f.write(repr_version(decversion))
  
  
print 'Creating directories...'

DOCSDIR = os.path.dirname(PATHSDIR)
ZOLDDIR = os.path.join(DOCSDIR, 'zOld')
VERSDIR = os.path.join(ZOLDDIR, 'PathsGame_versions')
DECDIR = os.path.join(VERSDIR, '-edit')
DEVDIR = os.path.join(VERSDIR, 'dev')
REVDIR = os.path.join(VERSDIR, 'release')
TMPDIR = os.path.join(VERSDIR, 'tmp')
TPATHSDIR = os.path.join(TMPDIR, 'PathsGame')
PATHSX = os.path.join(DOCSDIR, 'PathsGameX.py')
TPATHSX = os.path.join(TMPDIR, 'PathsGameX.py')
TVERFILE = os.path.join(TPATHSDIR, 'version')

try: os.makedirs(VERSDIR)
except OSError: pass
try: os.mkdir(DECDIR)
except OSError: pass
try: os.mkdir(DEVDIR)
except OSError: pass
try: os.mkdir(REVDIR)
except OSError: pass
shutil.rmtree(TMPDIR, True)


def export(v):
  if not os.path.exists(TMPDIR):
    try: os.mkdir(TMPDIR)
    except OSError: pass
    shutil.copytree(PATHSDIR, TPATHSDIR)
    shutil.copy2(PATHSX, TPATHSX)
  vstr = repr_version(v)
  with open(TVERFILE, 'w') as f:
    f.write(vstr)
  dec = v.release_level == 'DEC'
  rev = v.release_level == 'REV'
  catdir = DECDIR if dec else DEVDIR
  if rev:
    catdir = REVDIR
    tdyndir = os.path.join(TPATHSDIR, 'dyn')
    tscptdir = os.path.join(TPATHSDIR, 'scripts')
    tpydir = os.path.join(TPATHSDIR, 'py')
    tpyzip = os.path.join(TPATHSDIR, 'py.zip')
    import zipfile
    zf = zipfile.PyZipFile(tpyzip, 'w', zipfile.ZIP_DEFLATED)
    zf.writepy(tpydir)
    shutil.rmtree(tdyndir)
    shutil.rmtree(tscptdir)
    shutil.rmtree(tpydir)
  arname = os.path.join(catdir, vstr)
  shutil.make_archive(arname, 'zip', TMPDIR)
  if rev:
    shutil.rmtree(TMPDIR)


print '\nExporting:'
for v in expversions:
  print '    ' + repr_version(v)
  export(v)
  
print '\nCleaning up...'
shutil.rmtree(TMPDIR, True)

print '\nDone\n'

# Copyright 2010 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Creates a debian package assuming the following:

  ./debian/  contains correct debian configuration files
  ./dist/<package>-<ver>-tar.gz has a built source package.

If a there's a ./tmp directory it'll blow it away and create a new one.

Outputs the final package to ./debian-<debversion>/ (ex. ./debian-squeeze/sid)

On any error it exit's.

calling git-import-orig does that
call push pushes tag etc to git.
"""

import os
import shutil
import subprocess
import textwrap
import util

class DebianException(Exception):
  pass

def _copy_dir(from_dir, to_dir):
  """Recursively copy all the files from `from_dir` and below to `to_dir`."""
  print 'Copying from %r to %r' % (from_dir, to_dir)
  os.makedirs(to_dir)
  for fname in os.listdir(from_dir):
    from_name = os.path.join(from_dir, fname)
    if os.path.isdir(from_name):
      _copy_dir(from_name, os.path.join(to_dir, fname))
    else:
      shutil.copy2(from_name, to_dir)


def _copy_deb_file_to_dist(from_dir):
  """Copy the only .deb file to dist."""
  dest_dir = 'dist'
  for fname in os.listdir(from_dir):
    from_name = os.path.join(from_dir, fname)
    if os.path.isfile(from_name) and from_name.endswith('.deb'):
      shutil.copy(from_name, dest_dir)
      print 'Copied %r to %r' % (fname, dest_dir)
      return


def _move_top_files_to_dir(from_dir, to_dir):
  """Copy top level files (only) in `from_dir` to `to_dir`."""
  os.makedirs(to_dir)
  for fname in os.listdir(from_dir):
    from_name = os.path.join(from_dir, fname)
    if os.path.isfile(from_name):
      shutil.move(from_name, to_dir)
  print 'Moved files to %r' % to_dir


def _run_or_die(args, output=True):
  """Run the `args` (a list) or dies."""
  if output:
    print ' '.join(args)
  ret = subprocess.call(args)
  if ret:
    raise DebianException('Error running: %r' % ' '.join(args))

def _get_deb_dir():
  # Move
  if os.path.exists('/etc/debian_version'):
    deb_ver = open('/etc/debian_version').read().rstrip()
  else:
    deb_ver = 'UNKNOWN'
  return 'debian-%s' % deb_ver

def build_deb(setup):
  tmpdir = 'tmp'
  shutil.rmtree(tmpdir, True)
  dest_dir = '%s-%s' % (setup.NAME, setup.VER)
  src_tar = '%s-%s' % (setup.NAME, setup.VER)
  dest_tar = '%s_%s' % (setup.NAME, setup.VER)
  _copy_dir('debian', os.path.join(tmpdir, dest_dir, 'debian'))

  src_tarname = src_tar + '.tar.gz'
  dest_tarname = dest_tar + '.tar.gz'
  print 'Linking dist/%r to tmp/%r' % (src_tarname, dest_tarname)
  os.symlink(os.path.abspath(os.path.join('dist', src_tarname)),
             os.path.abspath(os.path.join(tmpdir, dest_tarname)))

  dest_tarname = dest_tar + '.orig.tar.gz'
  print 'Linking dist/%r to tmp/%r' % (src_tarname, dest_tarname)
  os.symlink(os.path.abspath(os.path.join('dist', src_tarname)),
             os.path.abspath(os.path.join(tmpdir, dest_tarname)))

  args = ['tar', '-zx', '--directory', tmpdir, '-f',
          os.path.join('dist', dest_dir + '.tar.gz')]
  _run_or_die(args)
  old_cwd = os.getcwd()
  os.chdir(os.path.join(tmpdir, dest_dir))
  args = ['debuild',
      '--lintian-opts', '--info', '--display-info', '--display-experimental',
      '--color', 'always',
      #'--pedantic'
      #'--fail-on-warnings',
      ]
  _run_or_die(args)
  os.chdir(old_cwd)
  debdir = _get_deb_dir()

  # Example removes ./debian-squeeze/sid/ on down.
  shutil.rmtree(debdir, True)
  _copy_deb_file_to_dist(tmpdir)
  _move_top_files_to_dir(tmpdir, debdir)

  # Cleanup tmpdir
  shutil.rmtree(tmpdir, True)

def control_file(setup):
  """Create a simple debian/control file.
  Args:
    setup: setup file.
  Returns:
    list of lines
  """
  lines = []

  lines.append('Source: %s' % setup.NAME)
  lines.append('Section: python')
  lines.append('Priority: optional')
  lines.append('Maintainer: %s <%s>' % (setup.SETUP['author'], setup.SETUP['author_email']))
  lines.append('Build-Depends: cdbs, debhelper (>= 7), python (>= 2.4), python-support')
  lines.append('Standards-Version: 3.8.4')
  lines.append('Homepage: %s' % setup.SETUP['url'])
  vcs = setup.VCS
  if vcs.endswith('/hg/'):
    lines.append('Vcs-Hg: %s' % vcs)
    lines.append('Vcs-Browser: %s' % vcs)
  lines.append('')
  lines.append('Package: %s' % setup.DEB_NAME)
  lines.append('Architecture: all')
  lines.append('Depends: ${shlibs:Depends}, ${misc:Depends},${python:Depends},')
  lines.append(' %s' % ','.join(setup.DEPENDS))
  lines.append('Description: %s' % setup.SETUP['description'])
  long_desc = textwrap.wrap(setup.SETUP['long_description'])
  for line in long_desc:
    if line.strip():
      lines.append(' %s' % line)
    else:
      lines.append(' .')
  lines.append('# -- generated by %s' % util.MAGIC_NAME)
  return lines

def git_import_orig(setup):
  """Run git_import_orig in the directory."""
  old_cwd = os.getcwd()
  os.chdir(os.path.join(_get_deb_dir(), '..', setup.NAME))
  args = ['git-import-orig',
    '../../%s/%s_%s.orig.tar.gz' % (_get_deb_dir(), setup.NAME, setup.VER),
    ]
  _run_or_die(args)

  args = ['git', 'push', 'origin', 'master']
  _run_or_die(args)

  args = ['git', 'push' '--tags']
  _run_or_die(args)

  os.chdir(old_cwd)

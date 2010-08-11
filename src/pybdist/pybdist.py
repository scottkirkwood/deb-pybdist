#!/usr/bin/python
# -*- coding: utf-8 -*-
#
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
"""

You'll need:
sudo apt-get install help2man fakeroot python-twitter python-simplejson

You'll also need ~/.netrc ~/.ssh/<fname>
"""

__author__ = 'Scott Kirkwood (scott+pybdist@forusers.com)'
__version__ = '0.3.1'

import codecs
import getpass
import glob
import httplib
import netrc
import os
import re
import release
import shutil
import simplejson
import subprocess
import twitter

import debian
import documents
import googlecode_update
import i18n
import mailinglist
import mercurial
import pypi_list
import rst_check
import spell_check
import update_file

class PyBdistException(Exception):
  pass


def fixup_setup(setup):
  """Fill in any missing pieces from setup."""
  if not hasattr(setup, 'PY_NAME'):
    setup.PY_NAME = setup.NAME
  if not hasattr(setup, 'PY_SRC'):
    setup.PY_SRC = '%s.py' % setup.PY_NAME
  if not hasattr(setup, 'DEB_NAME'):
    setup.DEB_NAME = setup.NAME
  if not hasattr(setup, 'AUTHOR_NAME'):
    setup.AUTHOR_NAME = setup.SETUP['author']
  if not hasattr(setup, 'GOOGLE_CODE_EMAIL'):
    setup.GOOGLE_CODE_EMAIL = setup.SETUP['author_email']
  return setup

def _run_or_die(args, err_mess=None, output=True):
  """Run the `args` (a list) or die.
  Args:
    args: list of arguments to pass to call
    err_mess: Extra hint what went wrong.
    output: output the command before running
  """
  if output:
    print ' '.join(args)
  try:
    ret = subprocess.call(args)
  except OSError, oserr:
    mess = 'Error running: %r: %r' % (' '.join(args), oserr)
    if err_mess:
      mess += '\n' + err_mess
    raise PyBdistException(err_mess)
  if ret:
    raise PyBdistException('Error running: code %r\n%r' % (ret, ' '.join(args)))


def _get_py_source_version(setup):
  fname = os.path.join(setup.DIR, setup.PY_SRC)
  re_py_ver = re.compile(r'__version__\s*=\s*[\'"](.*)[\'"]')
  grps = re_py_ver.search(open(fname).read())
  if not grps:
    raise PyBdistException('Unable to find __version__ in %r' % fname)
  source_ver = grps.group(1)
  return source_ver


def get_and_verify_versions(setup):
  """Get the version and make sure all versions are synched."""
  setup_ver = setup.VER
  source_ver = _get_py_source_version(setup)

  rel_ver, _, _ = _parse_last_release(setup)

  changelog_ver, _, _ = release.parse_deb_changelog(
      'debian/changelog')

  if (setup_ver != source_ver or setup_ver != rel_ver
      or setup_ver != changelog_ver):
    print '** Local setup versions don\'t agree'
    print '** setup.py = %r' % setup_ver
    print '** %s/%s = %r' % (setup.DIR, setup.PY_SRC, source_ver)
    print '** %s = %r' % (setup.RELEASE_FILE, rel_ver)
    print '** %s = %r' % ('debian/changelog', changelog_ver)
    raise PyBdistException('Setup versions don\'t agree')
  print '   Local setup versions agree'
  return setup_ver

def verify_remote_versions(setup):
  """Examine the remote versions."""
  setup_ver = setup.VER
  gc_ver, _, _ = release.get_last_google_code_version(setup.NAME)
  pypi_ver, _, _ = pypi_list.get_latest_version(setup.NAME)
  if gc_ver and gc_ver == setup_ver:
    print '   code.google.com version is up-to-date'
  else:
    print '** Note: code.google.com version is at %r and needs to be uploaded' % gc_ver

  if pypi_ver and pypi_ver == setup_ver:
    print '   pypi version is up-to-date'
  else:
    print '** Note: pypi.python.org version is at %r and needs to be uploaded' % pypi_ver


def _parse_last_release(setup):
  """Parse the release file from setup information.
  Returns:
    rel_ver, relase_date, rel_lines
  """
  release_regex = _get_var(setup, 'RELEASE_FORMAT')
  return release.parse_last_release(
      setup.RELEASE_FILE, release_regex)


def parse_last_release(setup):
  _, rel_date, rel_lines = _parse_last_release(setup)
  return rel_date, rel_lines


def build_zip_tar(unused_setup):
  args = [
    'python', 'setup.py', 'sdist', '--formats=gztar,zip']
  _run_or_die(args, 'Error building sdist')
  print 'Built zip and tar'


def upload_to_pypi(unused_setup):
  args = [
    'python', 'setup.py', 'sdist', '--formats=zip', 'upload',]
  _run_or_die(args, '\n'.join([
      'Error uploading to pypi',
      'If it\'s the first time, run "python setup.py register"']))
  print 'Upload to pypi'


def build_man(setup):
  if not hasattr(setup, 'MAN_FILE') or not setup.MAN_FILE:
    return

  dest_dir = os.path.dirname(setup.MAN_FILE)
  if not os.path.isdir(dest_dir):
    print 'Making directory %r' % dest_dir
    os.makedirs(dest_dir)
  langs = ['']
  if hasattr(setup, 'LANGS'):
    langs += setup.LANGS
  for lang in langs:
    if not lang:
      lang_dot = ''
    else:
      lang_dot = '%s.' % lang
    cur_manfile = setup.MAN_FILE.replace('.1', '.%s1' % lang_dot)
    include_file = cur_manfile.replace('.1', '.include')
    if not lang:
      locale = 'C'
    else:
      locale = lang
    args = [
      'help2man',
      '%s/%s' % (setup.DIR, setup.PY_SRC),
      #'%s' % setup.NAME,
      '--locale', locale,
      '-N', # no pointer to TextInfo
      '-i', include_file,
      '-o', cur_manfile]
    _run_or_die(args, '\n'.join([
        'Failed to build manfile',
        'You may need to install help2man']))

  print 'Built %s.1' % setup.NAME


def _get_var(setup, var):
  if hasattr(setup, var):
    return getattr(setup, var)
  return None


def build_deb(setup):
  debian.build_deb(setup)

def get_deb_filenames(setup):
  """Returns the list of debian files found in dist/ folder.

  Args:
    setup: information used to filter only some versions.
  Returns:
    list of fnames without the folder name.
  """
  debs = 'dist/%s_%s*all.deb' % (setup.DEB_NAME, setup.VER)
  ret = []
  for deb in glob.glob(debs):
    ret.append(deb.replace('dist/', ''))
  return ret


def clean_config(setup):
  config_file = os.path.expanduser('~/.config/%s/config' % setup.NAME)
  if os.path.exists(config_file):
    os.unlink(config_file)


def _clean_doc(setup):
  if not setup.NAME:
    raise PyBdistException('Missing setup.NAME')
  docs = '/usr/share/doc/%s' % setup.NAME
  if os.path.exists(docs) and os.path.isdir(docs):
    print 'rm -r %s' % docs
    shutil.rmtree(docs)


def _clean_man(setup):
  if not setup.NAME:
    raise PyBdistException('Missing setup.NAME')
  man = '/usr/share/man/man1/%s.1.gz' % setup.NAME
  if os.path.exists(man):
    print 'rm %s' % man


def _clean_scripts(setup):
  if 'scripts' not in setup.SETUP:
    return
  for script in setup.SETUP['scripts']:
    if not script.strip():
      raise PyBdistException('Missing setup.SETUP.scripts')
    bin_script = '/usr/local/bin/%s' % os.path.basename(script)
    if os.path.exists(bin_script):
      print 'rm %s' % bin_script
      os.unlink(bin_script)


def _clean_packages(setup):
  dist_dirs = ['/usr/share/pyshared',
      '/usr/local/lib/python2.4/dist-packages',
      '/usr/local/lib/python2.5/dist-packages',
      '/usr/local/lib/python2.6/dist-packages']
  base_dir = os.path.basename(setup.DIR)
  if not base_dir.strip():
    raise PyBdistException('%r is not a good name' % setup.DIR)

  for dist_dir in dist_dirs:
    if not os.path.exists(dist_dir):
      continue
    dist_packages = '%s/%s' % (dist_dir, base_dir)
    if os.path.exists(dist_packages):
      print 'rm -r %s' % dist_packages
      shutil.rmtree(dist_packages)
    _clean_eggs(dist_dir, setup)


def _clean_eggs(dist_dir, setup):
  dist_egg = '%s/%s-*.egg-info' % (dist_dir, setup.PY_NAME)
  for fname in glob.glob(dist_egg):
    if os.path.exists(fname):
      if os.path.isdir(fname):
        print 'rm -r %s' % fname
        shutil.rmtree(fname)
      else:
        print 'rm %s' % fname
        os.unlink(fname)


def clean_all(setup):
  clean_config(setup)
  _clean_packages(setup)
  _clean_doc(setup)
  _clean_man(setup)
  _clean_scripts(setup)


def print_release_info(setup):
  rel_date, rel_lines = parse_last_release(setup)
  print 'Local version is %r, date %r' % (setup.VER, rel_date)
  print 'Release notes'
  print '-------------'
  print '\n'.join(rel_lines)
  print

def test_code(setup):
  """Run tests with nosetests."""
  dirs = [setup.DIR]
  for root, cur_dirs, unused_files in os.walk(setup.DIR):
    for dirname in cur_dirs:
      if dirname in ['.svn', '.hg', '.ropeproject']:
        continue
      dirs.append(os.path.join(root, dirname))
  fname = '.noserc'
  if os.path.exists(fname):
    noserc = os.path.abspath(fname)
  else:
    noserc = None
  args = ['nosetests']
  if noserc:
    args += ['--config', noserc]
  args += dirs
  _run_or_die(args, 'You may need to install python-nose')

def check_code(setup):
  """Check the source code for errors."""
  if os.path.exists('.pycheckrc'):
    pycheckrc = os.path.abspath('.pycheckrc')
  else:
    pycheckrc = None
  olddir = os.getcwd()
  os.chdir(setup.DIR)
  files = glob.glob('*.py') + glob.glob('*/*.py') + glob.glob('*/*/*.py')

  args = ['pychecker', '--quiet', '--limit', '30']
  if pycheckrc:
    args += ['--config', pycheckrc]
  args += files
  _run_or_die(args, 'You may need to install pychecker')
  print 'Passed pychecker'
  os.chdir(olddir)

def check_rst(setup):
  """Check the release reStructuredText for errors."""
  rst_check.check_file(setup.RELEASE_FILE)
  rst_check.check_text(setup.SETUP['long_description'])

def check_spelling(setup):
  """Check the release reStructuredText for errors."""
  dictionary = '.aspell.en.pws'
  spell_check.check_file(setup.RELEASE_FILE, dictionary)
  spell_check.check_code_file('setup.py', dictionary)

def _maybe_update_file(old_fname, old_ver, new_fname, new_ver, replace_text, regex, del_lines=0):
  print '%r has version %r and %r has version %r' % (old_fname, old_ver, new_fname, new_ver)
  prompt = 'Update %r?: ' % old_fname
  yn = raw_input(prompt)
  if yn.lower() == 'y':
    if regex:
      update_file.update_lines(old_fname, regex, replace_text)
    else:
      update_file.insert_before(old_fname, replace_text, del_lines)

def _ver_lines_different(lines1, lines2):
  if len(lines1) != len(lines2):
    return True
  for l1, l2 in zip(lines1, lines2):
    if l1.strip() != l2.strip():
      return True
  return False

def _fix_versions_notes(setup):
  ver, date, lines = _parse_last_release(setup)
  setup_ver = setup.VER
  source_file = os.path.join(setup.DIR, setup.PY_SRC)
  source_ver = _get_py_source_version(setup)
  setup_file = 'setup.py'
  release_file = setup.RELEASE_FILE
  changelog_file = 'debian/changelog'
  changelog_ver, _, cl_lines = release.parse_deb_changelog(changelog_file)

  STRING_GROUP = '["\']([^"\']+)["\']'
  EQ = '\s*=\s*'
  if ver != setup.VER:
    _maybe_update_file(setup_file, setup_ver, release_file, ver,
        ver, r'^VER' + EQ + STRING_GROUP)

  if ver != changelog_ver or _ver_lines_different(lines, cl_lines):
    setup.VER = ver
    if ver == changelog_ver:
      del_lines = len(cl_lines) + 5
    else:
      del_lines = 0
    new_text = '\n'.join(release.out_debian_changelog(setup, lines))
    _maybe_update_file(changelog_file, changelog_ver, release_file, ver,
        new_text, None, del_lines)

  if ver != source_ver:
    _maybe_update_file(source_file, source_ver, release_file, ver,
        ver, r'^\s*__version__' + EQ + STRING_GROUP)


def check_for_errors(setup):
  _fix_versions_notes(setup)
  check_code(setup)
  check_rst(setup)
  check_spelling(setup)
  if mercurial.needs_hg_commit(verbose=False):
    print '** Mercurial needs commit'
  elif mercurial.needs_hg_push(verbose=False):
    print '** Mercurial needs push'
  get_and_verify_versions(setup)
  if hasattr(setup, 'LANGS'):
    i18n.count_untranslated(_get_locale_dir(setup), setup.LANGS)

def get_pass_from(fname):
  """Retrieves the password from this file.
  Verifies that the password is not visible by others on the machine.
  Args:
    fname: ex. ~/.ssh/myuser
  Returns:
    None or the password.  May output stuff too.
  """
  fname = os.path.expanduser(fname)
  if os.path.exists(fname):
    mode = os.stat(fname).st_mode
    if mode & 0077:
      print 'Change permissions on file first, chmod 600 %r' % fname
      return None
    dirname = os.path.dirname(fname)
    mode = os.stat(dirname).st_mode
    if mode & 0077:
      print 'Change permission on directory first, chmod 700 %r' % dirname
      return None
    return file(fname).read().rstrip()
  else:
    print '%r not found' % fname
  return None


def upload_to_google_code(setup):
  print 'Using user %r' % setup.GOOGLE_CODE_EMAIL
  password = get_pass_from('~/.ssh/%s' % setup.GOOGLE_CODE_EMAIL)
  if not password:
    # Read password if not loaded from svn config, or on subsequent tries.
    print 'Please enter your googlecode.com password.'
    print '** Note that this is NOT your Gmail account password! **'
    print 'It is the password you use to access repositories,'
    print 'and can be found here: http://code.google.com/hosting/settings'
    password = getpass.getpass()
  username = setup.GOOGLE_CODE_EMAIL
  files = [
    '%s-%s.zip' % (setup.NAME, setup.VER),
    '%s-%s.tar.gz' % (setup.NAME, setup.VER),
  ] + get_deb_filenames(setup)
  # removes all 'Featured' downloads that aren't in my list of `files`
  googlecode_update.remove_featured_labels(
      setup.NAME, username, password, files)

  for fname in files:
    if fname.endswith('.zip') or fname.endswith('.tar.gz'):
      labels = ['Type-Source', 'OpSys-Linux', 'Featured']
    elif fname.endswith('.deb'):
      labels = ['Type-Package', 'OpSys-Linux', 'Featured']
    else:
      labels = None
    summary = fname
    googlecode_update.maybe_upload_file(
        setup.NAME, 'dist', fname, summary, labels, username, password)


def announce_on_freshmeat(setup):
  """Announce launch on freshmeat."""
  print 'Announcing on Freshmeat...'

  _, _, rel_lines = _parse_last_release(setup)
  rcinfo = netrc.netrc(os.path.expanduser('~/.netrc'))
  # Storing the auth_code as the account in the .netrc file
  # ex. chmod 600 ~/.netrc
  # machine freshmeat
  #     login myname
  #     account auth_code_given_by_freshmeat
  #     password mypassword
  auth_code = rcinfo.authenticators('freshmeat')[1]
  name = setup.NAME
  if hasattr(setup, 'FRESHMEAT'):
    name = setup.FRESHMEAT
  tag = 'Bug fixes'
  if setup.VER.endswith('.0'):
    tag = 'Feature enhancements'
  changelog = ['Changes: '] + rel_lines
  release_dict = dict(version=setup.VER, changelog='\n'.join(changelog), tag_list=tag)
  path = '/projects/%s/releases.json' % name
  body = codecs.encode(simplejson.dumps(dict(auth_code=auth_code, release=release_dict)))
  connection = httplib.HTTPConnection('freshmeat.net')
  connection.request('POST', path, body, {'Content-Type': 'application/json'})
  response = connection.getresponse()
  if response.status == 404:
    print 'Project %r not found, may have to add FRESHMEAT to setup.py' % name
    raise PyBdistException('Freshmeat project not found, please register.')
  elif  response.status != 201:
    print 'Request failed: %d %s' % (response.status, response.reason)
    raise PyBdistException('Freshmeat upload failed')
  print 'Done announcing on Freshmeat.'


def announce_on_twitter(setup):
  print 'Announcing on twitter...'
  rcinfo = netrc.netrc(os.path.expanduser('~/.netrc'))
  auth = rcinfo.authenticators('twitter')
  username = auth[0]
  password = auth[2]
  metadata = dict(version=setup.VER, name=setup.NAME, url=setup.SETUP['url'])
  api = twitter.Api(username=username, password=password)
  api.PostUpdate('Release %(version)s of %(name)s is available from %(url)s' % metadata)
  print 'Done announcing on twitter.'

def _get_pot_filename(setup):
  return os.path.join(_get_locale_dir(setup), '%s.pot' % setup.NAME)

def _get_locale_dir(setup):
  return '%s/locale' % setup.DIR

def build_get_text(setup):
  # TODO(scottkirkwood): sub-directories
  dirs = [ 'setup.py', os.path.join(setup.DIR, '*.py')]
  i18n.build_get_text(_get_pot_filename(setup), dirs)

def update_po_files(setup):
  missing = i18n.update_po_files(_get_pot_filename(setup), _get_locale_dir(setup), setup.LANGS)
  for lang, fname in missing:
    print 'Creating %r' % fname
    i18n.make_empty_po_file(fname, lang, setup)

def compile_po_files(setup):
  i18n.compile_po_files(_get_locale_dir(setup), setup.LANGS)

def handle_standard_options(options, setup):
  """Handle options added by add_standard_options().
  Args:
    options: OptParser set of options.
    setup: the setup file module.
  Returns:
    True if handled, false otherwise."""
  fixup_setup(setup)
  if options.doclean:
    clean_all(setup)
  elif options.check:
    check_for_errors(setup)
    print
    print_release_info(setup)
  elif options.check_remote:
    verify_remote_versions(setup)
  elif options.test:
    test_code(setup)
  elif options.git:
    debian.git_import_orig(setup)
  elif options.dist:
    build_man(setup)
    build_zip_tar(setup)
    build_deb(setup)
    print_release_info(setup)
  elif options.upload:
    print_release_info(setup)
    upload_to_google_code(setup)
  elif options.pypi:
    print_release_info(setup)
    upload_to_pypi(setup)
  elif options.mail:
    mailinglist.mail(setup)
  elif options.freshmeat:
    print_release_info(setup)
    announce_on_freshmeat(setup)
  elif options.twitter:
    print_release_info(setup)
    announce_on_twitter(setup)
  elif options.missing_docs:
    documents.out_license(setup)
    documents.out_readme(setup)
    documents.out_install(setup)
  elif options.gettext:
    build_get_text(setup)
    update_po_files(setup)
    compile_po_files(setup)
  else:
    return False
  return True

def add_standard_options(parser, setup=None):
  parser.add_option('--clean', dest='doclean', action='store_true',
                    help='Uninstall things')
  parser.add_option('--missing-docs', dest='missing_docs', action='store_true',
                    help='Create missing docs.')
  parser.add_option('--check', dest='check', action='store_true',
                    help='Check for errors.')
  parser.add_option('--check-remote', dest='check_remote', action='store_true',
                    help='Check remote versions.')
  parser.add_option('--test', dest='test', action='store_true',
                    help='Run nose tests.')
  parser.add_option('--git', dest='git', action='store_true',
                    help='Push to git using gimp-import-orig.')
  parser.add_option('--dist', dest='dist', action='store_true',
                    help='Only build distributions.')
  parser.add_option('--upload', dest='upload', action='store_true',
                    help='Only upload to google code.')
  parser.add_option('--pypi', dest='pypi', action='store_true',
                    help='Only upload to pypi')
  if setup and hasattr(setup, 'MAILING_LIST'):
    parser.add_option('--mail', dest='mail', action='store_true',
                      help='Announce to mailing list.')
  parser.add_option('--freshmeat', dest='freshmeat', action='store_true',
                    help='Announce on freshmeat')
  parser.add_option('--twitter', dest='twitter', action='store_true',
                    help='Announce on Twitter')
  if not parser.has_option('--gettext') and setup and hasattr(setup, 'LANGS'):
    parser.add_option('--gettext', dest='gettext', action='store_true',
                      help='Build gettext files.')

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

"""Output some standard documents.

Creates files based on your setup.py that requires a few variables set:
NAME ex. NAME = 'pybdist'
SETUP ex. SETUP = { 'name': 'pybdist, ... }

Optional:
LANGS ex. LANGS = ['pt_BR', 'fr']
DEPENDS ex. DEPENDS = ['python-twitter']
"""

__author__ = 'Scott Kirkwood (scott+pybdist@forusers.com)'

import codecs
import filecmp
import gettext
import logging
import os
import re
import tempfile
import time
import urllib2

MAGIC_NAME = '`pybdist`'

gettext.install('pybdist')
logging.basicConfig()
LOG = logging.getLogger('pybdist')

LICENSES = {
  'Apache': (
     'http://www.apache.org/licenses/LICENSE-2.0.txt',
     r'\[yyyy\]', r'\[name of copyright owner\]'),
  'Artistic': (
      'http://www.perlfoundation.org/attachment/legal/artistic-2_0.txt',
      '2000-2006', 'The Perl Foundation'),
  'GPL.*2': (
      'http://www.gnu.org/licenses/gpl-2.0.txt',
      'END OF TERMS.+', ''),
  'GPL.*3': (
      'http://www.gnu.org/licenses/gpl-3.0.txt',
      'END OF TERMS.+', ''),
  'LGPL': (
      'http://www.gnu.org/licenses/lgpl.txt',
      '', ''),
  'MIT': (
      'mit-license.txt',
      '<year>', '<copyright holders>'),
  'Mozilla': (
      'http://www.mozilla.org/MPL/MPL-1.1.txt',
      '', ''),
  'BSD': (
      'new-bsd-license.txt',
      '<YEAR>', '<OWNER>'),
}

class DocumentsException(Exception):
  pass

def _safe_overwrite(lines, fname):
  """Given the new text string overwrite fname.

  Leaves the old version in /tmp/pybdist/ folder, this is ok since you should
  be using a version control system anyway, right?

  Asks if you want to overwrite.
  Doesn't ask if the files are identical.
  Doesn't ask if the file exists has has MAGIC_NAME near the end.

  Args:
    text: lines, list of lines
    fname: filename to overwrite
  """

  can_overwrite = True
  if os.path.exists(fname):
    can_overwrite = False
    for line in open(fname):
      if MAGIC_NAME in line:
        can_overwrite = True
        break
  if not can_overwrite:
    LOG.info('%r not overwritten because it\'s missing magic string %r', fname, MAGIC_NAME)
    return
  tmpdir = os.path.join(tempfile.gettempdir(), 'pybdist')
  if not os.path.isdir(tmpdir):
    LOG.info('Makeing directory %r', tmpdir)
    os.makedirs(tmpdir)
  out_tempname = os.path.join(tmpdir, 'tmp.tmp')
  outf = codecs.open(out_tempname, encoding='utf-8', mode='w')
  outf.write(u'\n'.join(lines))
  outf.close()
  if os.path.exists(fname):
    if filecmp.cmp(out_tempname, fname):
      os.unlink(out_tempname)
      LOG.info('%r is the same', fname)
      return

    prompt = 'Update %r?: ' % fname
    yn = raw_input(prompt)
    if yn.lower() != 'y':
      os.unlink(out_tempname)
      LOG.info('User requested not to overwrite')
      return  # nope

  backup_name = os.path.join(tmpdir, os.path.basename(fname))
  if os.path.exists(fname):
    LOG.info('backup stored at %r', backup_name)
    os.rename(fname, backup_name)
  os.rename(out_tempname, fname)
  LOG.info('Wrote %r', fname)
  print 'Updated %r' % fname

def _find_license():
  """Return the name of the license file or an empty string."""
  re_licensefilename = re.compile('license', re.IGNORECASE)
  for fname in os.listdir('.'):
    if re_licensefilename.search(fname):
      return os.path.abspath(os.path.join('.', fname))

  return ''

def _underline(word, char='='):
  return [word, char * len(word)]

def _readme_lines(setup):
  lines = ['']
  lines += _underline(setup.NAME)
  lines.append('')
  lines.append(setup.SETUP['description'])
  lines.append('')
  lines.append(setup.SETUP['long_description'])
  lines += _underline(_('Home Page'))
  lines.append('')
  lines.append(_('You can find %s hosted at:') % setup.NAME)
  url = setup.SETUP['url']
  lines.append('  %s' % url)
  if 'code.google.com/' in url:
    LOG.info('Adding code.google.com links')
    lines.append('')
    lines.append(_('You can file bugs at:'))
    lines.append('  %s/issues/list' % url)
    lines.append('')
    lines.append(_('Latest downloads can be found at:'))
    lines.append('')
    lines.append('  %s/downloads/list' % url)

  if hasattr(setup, 'DEPENDS'):
    lines.append('')
    lines += _underline(_('Requirements'))
    lines.append(_('This program requires other libraries which you may or may not have installed.'))
    lines.append('')
    for req in setup.DEPENDS:
      lines.append(' * %s' % req)

  lines.append('')
  lines += _underline(_('License'))
  lines.append('')
  lines.append(setup.SETUP['license'])
  license_file = _find_license()
  if not license_file:
    license_file = 'LICENSE-2.0.txt'
  lines.append(_('You can find it in the %s file.') % license_file)
  lines.append('')
  lines.append(_('-- file generated by %s.') % MAGIC_NAME)
  return lines

def out_readme(setup):
  langs = ['']
  if hasattr(setup, 'LANGS'):
    langs += setup.LANGS
    LOG.info('Will output %d README language files.', len(langs))

  for lang in langs:
    if lang:
      dot_lang = '.%s' % lang
      locale = lang
    else:
      dot_lang = ''
      locale = ''
    locale_dir = os.path.join(setup.DIR, 'locale')
    locale_dir = os.path.abspath(locale_dir)
    if locale:
      lang = gettext.translation(setup.NAME, locale_dir, languages=[locale])
      lang.install(unicode=True)
    fname = 'README%s' % dot_lang
    _safe_overwrite(_readme_lines(setup), fname)

def out_license(setup):
  lic_text = setup.SETUP['license']
  to_fetch = None
  for regex, info in LICENSES.items():
    if re.search(regex, lic_text, re.IGNORECASE):
      to_fetch = info
      break
  if not to_fetch:
    raise DocumentsException('Unknown lic_text %r' % lic_text)

  license_fname = _find_license()
  if not license_fname:
    license_fname = 'LICENSE-2.0.txt'
    LOG.info('Creating license file %r' % license_fname)
  else:
    LOG.info('License file already exists as %r' % license_fname)
  url, y_regex, name_regex = to_fetch
  if url.startswith('http'):
    txt = urllib2.urlopen(url).read()
  else:
    txt = open(os.path.join(os.path.dirname(__file__), url)).read()
  year = time.strftime('%Y', time.localtime())
  re_yyyy = re.compile(y_regex, re.DOTALL)
  txt = re_yyyy.sub(year, txt)
  copyright_name = setup.SETUP['author']
  if hasattr(setup, 'COPYRIGHT_NAME'):
    copyright_name = setup.COPYRIGHT_NAME
  if name_regex:
    re_name = re.compile(name_regex, re.DOTALL)
    txt = re_name.sub(copyright_name, txt)
  else:
    txt += ' ' + copyright_name
  _safe_overwrite(txt.split('\n'), license_fname)

if __name__ == '__main__':
  import sys
  LOG.setLevel(logging.DEBUG)
  setup_dir = os.path.abspath(__file__ + '/../../..')
  print setup_dir
  sys.path.insert(0, setup_dir)
  import setup
  out_readme(setup)
  out_license(setup)

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

import os
try:
  import polib
except ImportError:
  raise ImportError('You need to install polib, try sudo "apt-get install python-polib"')
import subprocess
import time

class I18nException(Exception):
  pass

def _run_or_die(args, output=True):
  """Run the `args` (a list) or dies."""
  if output:
    print ' '.join(args)
  ret = subprocess.call(args)
  if ret:
    raise I18nException('Error running: %r' % ' '.join(args))

def build_get_text(out_pot, dirs):
  """Creates .pot file from source python files.
  Args:
    out_pot: name of output .pot file to create.
    dirs: list of globs ex, ['src/*.py']
  Throw:
    I18nException on error
  """
  args = [
      'pygettext',
      '--output', out_pot,
      ] + dirs
  _run_or_die(args)

def make_empty_po_file(fname, lang, setup):
  po = polib.POFile()
  curtime = time.strftime('%Y-%m-%d %H:%M+', time.localtime())
  curtime += time.tzname[0]
  po.metadata['Project-Id-Version'] = '%s' % setup.NAME
  po.metadata['Report-Msgid-Bugs-To'] = setup.SETUP['author_email']
  po.metadata['POT-Creation-Date'] = curtime
  po.metadata['PO-Revision-Date'] = curtime
  po.metadata['Last-Translator'] = 'you <you@example.com>'
  po.metadata['Language-Team'] = '%s team' % lang
  po.metadata['MIME-Version'] = '1.0'
  po.metadata['Content-Type'] = 'text/plain; charset=utf-8'
  po.metadata['Content-Transfer-Encoding'] = '8bit'
  po.save(fname)

def update_po_files(potfile, locale_dir, langs):
  """Merge an old translated .po with the new messages.pot into one.
  Creates loacaldir/lang/LC_MESSAGES/
  Args:
    potfile: source potfile to merge from.
    locale_dir: ex. src/app/locale
    langs: array of languages, ex. ['pt_BR', 'fr']
  Return:
    possibly list of problem file [ (lang, fname) ]
  """
  if not potfile.endswith('.pot'):
    raise I18nException('Your .pot file must end with .pot %r' % potfile)
  po_name = os.path.split(potfile)[1].replace('.pot', '.po')
  missing = []
  for lang in langs:
    curdir = os.path.join(locale_dir, lang, 'LC_MESSAGES')
    if not os.path.exists(curdir):
      os.makedirs(curdir)
    outfile = os.path.join(curdir, po_name)
    if not os.path.exists(outfile):
      missing.append((lang, outfile))
      continue
    args = [
        'msgmerge',
        outfile,
        potfile,
        '-o', outfile
        ]
    _run_or_die(args)
  return missing

def compile_po_files(locale_dir, langs):
  """Convert the .po files into binary .mo files.
  Args:
    locale_dir: location of the locale dir
    langs: list of languages, ex. ['pt_BR', 'fr']
  """
  for lang in langs:
    curdir = os.path.join(locale_dir, lang, 'LC_MESSAGES')
    if not os.path.exists(curdir):
      continue
    files = os.listdir(curdir)
    for fname in files:
      if fname.endswith('.po'):
        fname_mo = fname.replace('.po', '.mo')
        args = [
            'msgfmt',
            os.path.join(curdir, fname),
            '-o', os.path.join(curdir, fname_mo)
            ]
        _run_or_die(args)

def count_untranslated(locale_dir, langs):
  for lang in langs:
    curdir = os.path.join(locale_dir, lang, 'LC_MESSAGES')
    if not os.path.exists(curdir):
      continue
    files = os.listdir(curdir)
    for fname in files:
      if fname.endswith('.po'):
        pofilename = os.path.join(curdir, fname)
        po = polib.pofile(pofilename)
        un = po.untranslated_entries()
        if un:
          print '%r has %d untranslated entries' % (pofilename, len(un))

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

"""Utility routines used by pybdist."""

from __future__ import absolute_import
from __future__ import print_function
from six.moves import input
MAGIC_NAME = '`pybdist`'

__author__ = 'Scott Kirkwood (scott+pybdist@forusers.com)'

import codecs
import filecmp
import logging
import os
import tempfile

logging.basicConfig()
LOG = logging.getLogger('pybdist')

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
    yn = input(prompt)
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
  print('Updated %r' % fname)

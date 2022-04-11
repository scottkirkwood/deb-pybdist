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
"""Spell check a file or a piece of text.

Uses the aspell command which must be installed and on the path.
May open a spell check window.

Creates or uses a spell check file given.
"""
from __future__ import absolute_import
from __future__ import print_function
__author__ = 'Scott Kirkwood (scott+pybdist@forusers.com)'

import os
import subprocess
import tempfile

class SpellCheckException(Exception):
  pass

def _run_or_die(args, err_mess=None, output=True):
  """Run the `args` (a list) or die.
  Args:
    args: list of arguments to pass to call
    err_mess: Extra hint what went wrong.
    output: output the command before running
  """
  if output:
    print(' '.join(args))
  try:
    ret = subprocess.call(args)
  except OSError as oserr:
    mess = 'Error running: %r: %r' % (' '.join(args), oserr)
    if err_mess:
      mess += '\n' + err_mess
    raise SpellCheckException(err_mess)
  if ret:
    raise SpellCheckException('Error running: code %r\n%r' % (ret, ' '.join(args)))


def check_file(fname, dictionary):
  """Check the file given with and update the dictionary given."""
  if os.path.exists(fname):
    home_dir = os.path.dirname(os.path.abspath(dictionary))
  else:
    home_dir = dictionary
  args = ['aspell', '--lang', 'en']
  if home_dir:
    args += ['--home-dir', home_dir]
  args += ['-c', fname]
  _run_or_die(args, 'You may need to install aspell')

def check_code_file(fname, dictionary):
  """Check the file given with and update the dictionary given."""
  if os.path.exists(fname):
    home_dir = os.path.dirname(os.path.abspath(dictionary))
  else:
    home_dir = dictionary
  args = ['aspell', '--mode', 'perl', '--lang', 'en']
  if home_dir:
    args += ['--home-dir', home_dir]
  args += ['-c', fname]
  _run_or_die(args, 'You may need to install aspell')

def check_text(text, dictionary):
  t_out, fname_tmp = tempfile.mkstemp('txt')
  os.write(t_out, bytes(text, 'utf-8'))
  os.close(t_out)
  check_file(fname_tmp, dictionary)
  os.unlink(fname_tmp)

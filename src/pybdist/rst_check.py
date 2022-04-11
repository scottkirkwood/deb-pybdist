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

from __future__ import absolute_import
from __future__ import print_function
__author__ = 'Scott Kirkwood (scott+pybdist@forusers.com)'

import os
import subprocess
import tempfile

class RstCheckException(Exception):
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
    raise RstCheckException(err_mess)
  if ret:
    raise RstCheckException('Error running: code %r\n%r' % (ret, ' '.join(args)))


def check_file(fname):
  args = ['rst2html', '--strict', fname, '/dev/null']
  _run_or_die(args, 'You may need to run "sudo apt-get install python3-docutils')


def check_text(rst_text):
  t_out, fname_tmp = tempfile.mkstemp('rst')
  os.write(t_out, bytes(rst_text, 'utf-8'))
  os.close(t_out)
  args = ['rst2html', '--strict', fname_tmp, '/dev/null']
  _run_or_die(args, 'Note: left a tempfile at %r' % fname_tmp)
  os.unlink(fname_tmp)

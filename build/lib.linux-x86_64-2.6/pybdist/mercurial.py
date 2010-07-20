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

__author__ = 'Scott Kirkwood (scott+pybdist@forusers.com)'

import subprocess

def _run_ret(args, output=True):
  """Run the `args` (a list)

  Retcode -999 if unable to run.
  Args:
    args: list of arguments to pass to call
    output: output the command before running
  Returns:
    retcode, lines
  """
  lines = []
  if output:
    print ' '.join(args)
  try:
    p = subprocess.Popen(args, stdout=subprocess.PIPE)
    text = p.communicate()[0]
    lines = text.split('\n')
    ret = p.returncode
  except OSError, oserr:
    ret = -999
  return (ret, lines)

def needs_hg_push(verbose=True):
  """Checks if mercurial thinks we need to push."""
  args = ['hg', 'outgoing', '--noninteractive', '--quiet']
  ret, _ = _run_ret(args, verbose)
  if ret == -999:
    return False
  if ret == 1:
    if verbose:
      print 'Mercurial remote version up-to-date'
    return False
  if verbose:
    print 'Mercurial remote version needs push'
  return True

def needs_hg_commit(verbose=True):
  args = ['hg', 'status', '--noninteractive', '--quiet']
  ret, lines = _run_ret(args, verbose)
  if ret == -999:
    if verbose:
      print 'Mercurial not found'
      print '\n'.join(lines)
    return False
  # Strip blank lines
  lines = [l for l in lines if l]
  if not lines:
    if verbose:
      print 'Mercurial does not need a push', ret
    return False
  if verbose:
    print 'Mercurial needs commit, %d files out of date' % len(lines)
    print '\n'.join(lines)
  return True

if __name__ == '__main__':
  needs_hg_commit()
  needs_hg_push()

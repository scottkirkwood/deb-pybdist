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
"""This updates a files with a regular expression.
Works on linux only.
"""

__author__ = 'Scott Kirkwood (scott+pybdist@forusers.com)'

import re
import os
import tempfile

class UpdateFileException(Exception):
  pass

class OverwriteFile(object):
  """Class to use to overwrite a file."""

  def __init__(self):
    self.prefix = None
    self.postfix = None
    self.fin = None
    self.dirname = None
    self.fname = None
    self.t_out = None
    self.fname_tmp = None

  def open(self, fname):
    basename = os.path.basename(fname)
    name, ext = os.path.split(basename)
    self.prefix = name
    self.postfix = ext + '_bak'
    self.fname = fname
    if not os.path.exists(fname):
      raise UpdateFileException('File not found %r' % self.fname)
    self.fin = open(self.fname, 'r')
    if not self.fin:
      raise UpdateFileException('Unable to open file %r' % self.fname)
    self.dirname = os.path.dirname(self.fname)
    if not self.dirname:
      self.dirname = '.'
    self.t_out, self.fname_tmp = tempfile.mkstemp(self.postfix, self.prefix, dir=self.dirname)
    if not self.t_out:
      raise UpdateFileException('Unable to make temp file')

  def readlines(self):
    """Returns fin which can be iterated."""
    return self.fin

  def write(self, text):
    """Write to the temp file."""
    os.write(self.t_out, text)

  def close(self):
    """Closes the input and output and overwrite self.fname."""
    if not self.t_out:
      return
    os.close(self.t_out)
    self.fin.close()
    self.t_out = None
    self.fin = None

    # Note: This only works correctly on POSIX systems
    # i.e. it overwrites the destination
    os.rename(self.fname_tmp, self.fname)

  def __del__(self):
    self.close()

def insert_before(fname, text):
  """Inserts `text` at the start of the file."""
  update = OverwriteFile()
  update.open(fname)
  update.write(text)
  for line in update.readlines():
    update.write(line)
  update.close()

def update_lines(fname, regex, replace, max_replaces=1):
  """Looks for `regex` and replaces group(1) with `replace`.
  Note: regex is on a line basis, not multiline.

  Args:
    fname: name of the file, may be in a subfolder.
    regex: regular expression, must have 1 group.
    replace: The text to replace in group 1.
    max_replaces: Number of replaces expected, for speed and safety.
  """
  update = OverwriteFile()
  update.open(fname)
  re_f = re.compile(regex)
  num_replaces = 0
  for line in update.readlines():
    if max_replaces > 0:
      match = re_f.search(line)
      if max_replaces > 0 and match:
        if len(match.groups()) != 1:
          raise UpdateFileException('Your regex must have exactly 1 group %r' % regex)
        max_replaces -= 1
        num_replaces += 1
        update.write(line[:match.start(1)])
        update.write(re_f.sub(line, replace))
        update.write(line[match.end(1):])
      else:
        update.write(line)
    else:
      update.write(line)
  if num_replaces == 0:
    raise UpdateFileException('No replaces performed on %r' % fname)
  update.close()

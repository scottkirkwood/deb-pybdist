#!/usr/bin/python
# -*- coding: utf-8 -*-
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

"""Parses a release file and gets the latest release information.
Code assumes that the release has a date and a version.
And sections are separated by ======== or --------
"""

import googlecode_update
import re
import sys
import time

class ReleaseException(Exception):
  pass

def parse_last_release(fname, pattern=None):
  """Parse the last release in an RST release file.
  Args:
    fname: filename
    pattern: Regular expression or null, expects the <date> and <ver> groups.
  Returns:
    (version, date, lines)
  """
  # Example "Apr. 18th, 2009 v 0.16"
  if not pattern:
    pattern = r'(?P<date>.*) v (?P<ver>\d+.\d+(?:.\d+)?)$'

  re_version = re.compile(pattern)
  re_horz = re.compile(r'^[-=]+$')
  version = None
  lines = []
  for line in open(fname):
    line = line.rstrip()
    grps = re_version.match(line)
    if grps:
      if version:
        break
      date, version = grps.group('date'), grps.group('ver')
    elif re_horz.match(line):
      pass
    elif version:
      lines.append(line)

  if not lines:
    raise ReleaseException('No line with %r pattern found in %r' % (pattern, fname))

  if not lines[-1]:
    del lines[-1]

  return version, date, lines

def parse_deb_changelog(fname):
  re_ver = re.compile(r'^[\w-]+ \(([^)]+)\) ')
  re_date_exp = r'^ -- [\w ]+ \<[^>]+\>  (.*)'
  re_date = re.compile(re_date_exp)
  version = None
  date = None
  lines = []
  for line in file(fname):
    line = line.rstrip()
    grps = re_ver.search(line)
    if grps:
      if version:
        print 'Bad changelog, got two versions %r & %r' % (version, grps.group(1))
        print 'Probably means I couldn\'t find the date line "%s".' % re_date_exp
        raise ReleaseException('Bad debian/changelog')
      version = grps.group(1)
      continue
    grps = re_date.search(line)
    if grps:
      date = grps.group(1)
      break
    if version and line:
      lines.append(line)
  if version:
    index = version.rfind('-')
    if index != -1:
      version = version[:index]
  return version, date, lines

def out_debian_changelog(settings, lines):
  ret = []
  ret.append('%s (%s-1) unstable; urgency=low' % (settings.NAME, settings.VER))
  ret.append('')
  ret += ['  %s' % l for l in lines]
  ret.append('')
  datestr = time.strftime('%a, %d %b %Y %H:%M:%S', time.localtime())
  datestr += ' %+05d' % (time.timezone/36)
  ret.append(' -- %s <%s>  %s' % (settings.AUTHOR_NAME, settings.GOOGLE_CODE_EMAIL, datestr))
  ret.append('')
  ret.append('')
  return ret

def _get_last_versions(project_name):
  versions = []
  re_version = re.compile(r'%s-(.*).tar.gz' % project_name)
  for info in googlecode_update.get_download_list(project_name):
    grps = re_version.search(info['fname'])
    if grps:
      ver = grps.group(1)
      versions.append((info['updated'], ver, [info['summary']]))
  return versions


def get_last_google_code_version(project_name):
  versions = _get_last_versions(project_name)
  if not versions:
    return ('', '', '')
  versions.sort()
  last = versions[-1]
  return last[1], last[0], last[2]


if __name__ == '__main__':
  VER, DATE, LINES = parse_last_release('RELEASE.rst')
  print VER, DATE, LINES

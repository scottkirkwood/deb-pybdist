#!/usr/bin/env python
#
# Copyright 20l0 Google Inc. All Rights Reserved.
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
__author__ = 'scott@forusers.com (Scott Kirkwood)'

import re
import six.moves.urllib.request, six.moves.urllib.error, six.moves.urllib.parse

def get_latest_version(project_name):
  """Get the version, download fname, and md5 hash.

  If version is '' then the project was not found.
  fname and hash may be '' if not found.
  Args:
    project_name: Name of the pypi project.
  Returns:
    (version, download_fname, download md5 digest)
  """

  url = 'http://pypi.python.org/pypi/%s/' % project_name
  try:
    fin = six.moves.urllib.request.urlopen(url)
    text = fin.read()
    fin.close()
  except six.moves.urllib.error.URLError:
    text = ''
  # The following url should always exist.
  re_url = re.compile(r'<a href="[^"]*/pypi/%s/([^"]+)">' % project_name, re.DOTALL)

  # Sometimes the download url does not exist.
  re_download = re.compile(
      r'<a href="http://pypi.python.org/packages/source/m/%s/([^#]+)#md5=([^"]+)">' % project_name,
      re.DOTALL)
  grps = re_url.search(text)
  if grps:
    ver = grps.group(1)
  else:
    ver = ''
  grps = re_download.search(text)
  if grps:
    fname = grps.group(1)
    md5 = grps.group(2)
  else:
    fname = ''
    md5 = ''
  return (ver, fname, md5)

if __name__ == '__main__':
  print(get_latest_version('myzones'))

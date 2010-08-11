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

import gettext
import logging
import os
import netrc
import re
import smtplib

import release

gettext.install('pybdist')
logging.basicConfig()
LOG = logging.getLogger('pybdist')

DEFAULT_MESSAGE = _("""Hi,

I'm happy to announce release version %(version)s of %(name)s.

_Release Notes_
%(release_lines)s

What is "%(name)s"?

%(long_description)s

_Links_
%(urls)s

Thanks,
%(author)s
""")

def create_message(setup):
  if hasattr(setup, 'RELEASE_FORMAT'):
    release_regex = setup.RELEASE_FORMAT
  else:
    release_regex = None
  rel_ver, rel_date, rel_lines = release.parse_last_release(
      setup.RELEASE_FILE, release_regex)
  urls = [
    'Homepage: %s' % setup.SETUP['url'],
    ]

  if 'code.google.com' in setup.SETUP['url']:
    urls.append('Download: %s/downloads/list' % setup.SETUP['url'])
  else:
    urls.append('Download: %s' % setup.SETUP['download_url'])

  grps = re.match(r'([^@]+)@googlegroups.com', setup.MAILING_LIST)
  if grps:
    urls.append('Manage mailing list: '
                'http://groups.google.com/group/%s/subscribe' % grps.group(1))
  else:
    urls.append('Mailing list: %s' % setup.MAILING_LIST)

  return DEFAULT_MESSAGE % {
      'rel_date': rel_date,
      'release_lines': '\n'.join(rel_lines),
      'version': setup.SETUP['version'],
      'name': setup.NAME,
      'description': setup.SETUP['description'],
      'long_description': setup.SETUP['long_description'],
      'urls': '\n'.join(urls),
      'author': setup.SETUP['author']}

def create_subject(setup):
  return _('[ANN] Release %s of %s') % (setup.SETUP['version'], setup.NAME)

def send_email(to_email, subject, msg):
  rcinfo = netrc.netrc(os.path.expanduser('~/.netrc'))
  auth = rcinfo.authenticators('gmail')
  email = auth[0]
  name = auth[1].replace('+', ' ')  # put a + for space in the .netrc file
  password = auth[2]
  server = 'smtp.gmail.com'
  port = 587
  LOG.info('Connecting to %s:%s', server, port)
  server = smtplib.SMTP(server, port)
  server.ehlo()
  server.starttls()
  server.ehlo()
  LOG.info('Logging in using email %s', email)
  server.login(email, password)
  full_message = ['To: %s' % to_email,
      'From: %s <%s>' % (name, email),
      'Reply-To: %s' % to_email,
      'Subject: %s' % subject,
      '',
      msg]
  LOG.info('Full Message\n%s', '\n'.join(full_message))
  result = server.sendmail(email, to_email, '\n'.join(full_message))
  if result:
    errs = []
    for recip in result:
      errs.append(
          'Could not deliver mail to: %s\n'
          'Server said: %s\n%s' % (recip, result[recip][0], result[recip][1]))
    raise smtplib.SMTPException('\n'.join(errs))
  server.close()

def mail(setup):
  subject = create_subject(setup)
  message = create_message(setup)
  send_email(setup.MAILING_LIST, subject, message)
  print 'Sent mail to %s' % setup.MAILING_LIST

if __name__ == '__main__':
  import sys
  LOG.setLevel(logging.DEBUG)
  setup_dir = os.path.abspath(__file__ + '/../../..')
  sys.path.insert(0, setup_dir)
  import setup
  os.chdir('../..')
  subject = create_subject(setup)
  message = create_message(setup)
  if False:
    send_email(setup.MAILING_LIST, subject, message)
  else:
    print subject
    print message

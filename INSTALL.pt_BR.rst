==================
Instalando pybdist
==================

Downloading
-----------

Você vai achar a ultima versão no:

  http://code.google.com/p/pybdist/downloads/list

Se prefere, pode clonar o repositório::

  hg clone http://pybdist.code.google.com/hg pybdist

Instalação
----------

Para instalar utilizando ``pip``,::

  $ pip install pybdist

Para instalar utilizando ``easy_install``,::

  $ easy_install pybdist

Para instalar no pacote .deb::

  $ sudo dpkg -i pybdist*.deb

If you get errors like Package pybdist depends on XXX; however it is not installed.

  $ sudo apt-get -f install
Should install everything you need, then run:
  $ sudo dpkg -i pybdist*.deb # again

Dependências
------------

Este programa preciso::

* fakeroot          - Gives a fake root environment
* lintian           - Debian package checker
* help2man          - Automatic manpage generator
* build-essential   - Informational list of build-essential packages
* python-twitter    - Twitter API wrapper for Python
                      (http://code.google.com/p/python-twitter/)
* python-simplejson - Simple, fast, extensible JSON encoder/decoder for Python
                      (http://undefined.org/python/#simplejson)
* pychecker         - Finds common bugs in Python source code
* python-docutils   - utilities for the documentation of Python modules
                      (http://docutils.sourceforge.net/)
* python-nose       - test discovery and running for Python's unittest
                      (http://somethingaboutorange.com/mrl/projects/nose/)
* aspell            - GNU Aspell spell-checker
                      (http://aspell.net/)
* aspell-en         - English dictionary for GNU Aspell
* python-polib      - Python library to parse and manage gettext catalogs
                      (http://bitbucket.org/izi/polib/src/)
* python-apt        - Python interface to libapt-pkg

-- arquivo criado pelo `pybdist`.
Release Notes
=============

August 10th, 2010 v 0.3.1
-------------------------
* Rot13 files missing from debian distribution.

August 10th, 2010 v 0.3
-----------------------
* Added ability to an make an announcement to a mailing list.

August 4th, 2010 v 0.2.16
-------------------------
* Automated git-import and push with --git.

August 4th, 2010 v 0.2.15
-------------------------
* When updating changelog, I was off by 5 lines.

August 3rd, 2010 v 0.2.14
-------------------------
* Missing files in MANIFEST.in
* ROT13 the licenses so there will be no confusion which license this package
  is using.
* Support for updating the debian release notes.

August 2nd, 2010 v 0.2.13
-------------------------
* Fix update file so that it copies the file mode.

July 19th, 2010 v 0.2.12
------------------------
* Added ability to create INSTALL.rst file.
* Changed default from README to README.rst since it plays nice in github.

July 16th, 2010 v 0.2.11
------------------------
* Added --missing-docs parameter to create various files.
* Added --check-remote to check pypi and download pages as a separate check.
* Support for creating README docs in multiple languages.
* Broke out util.py functions.
* Support for internationalization of man pages.

July 15th, 2010 v 0.2.10
------------------------
* Added code for creating gettext internationalization.

July 14th, 2010 v 0.2.9
-----------------------
* Added pypi version check.
* Added mercurial commit and push checks.
* Check for rst errors in setup description.
* Spell check setup.py

July 14th, 2010 v 0.2.8
-----------------------
* Added nosetests.
* Added fixup_setup() method which can fill in missing variables as required.

July 14th, 2010 v 0.2.7
-----------------------
* Have freshmeat use alternate name 'FRESHMEAT' if found in setup.py.

July 13th, 2010 v 0.2.6
-----------------------
* Have pychecker do sub-directories.
* Have pychecker user a local .pycheckrc file, if it exists.
* Check for spell errors in release notes with aspell.
* Check for rst errors in release notes with rst2html.

July 12th, 2010 v 0.2.5
-----------------------
* Throwing exceptions instead of sys.exit()
* Better error when debian/changelog is empty.
* Works when offline.

July 8th, 2010 v 0.2.4
-----------------------
* Add auto_file to update version information automatically on --check.

July 7th, 2010 v 0.2.3
-----------------------
* Problem with the Google code upload.

July 4th, 2010 v 0.2.2
-----------------------
* Additional changes to make it work with key-mon

July 4th, 2010 v 0.2.1
-----------------------
* Bad manifest caused missing files.
* Changed the function names to use underscores, this will break old code!
  I've realized that Google's public Python style guide is a bit different
  than the internal style guide.
* Automatically removes 'Featured' flag for old files on code.google.com.
* Added pychecker test.
* Added .pylintrc.

July 3rd, 2010 v 0.2.0
-----------------------
* Debian build uses debian directory.
* Parse of the Debian changelog done to make sure versions are up-to-date.
* Download of the versions numbers from code.google.com for verification.

June 20th, 2010 v 0.1.5
-----------------------
* Upload of Debian file was incorrect.

June 20th, 2010 v 0.1.4
-----------------------
* Can have a release pattern for different changelog styles.
* Can announce on twitter.

June 20th, 2010 v 0.1.3
-----------------------
* Icons are copied.
* Menus can be install (why is that so damn hard to do?).

June 19th, 2010 v 0.1.2
-----------------------
* Minor bug fixes.
* Optional variables are optional.
* Made CleanConfig a global function.
* Made the Clean functions a little safer.

June 19th, 2010 v 0.1.1
-----------------------
* Initial release

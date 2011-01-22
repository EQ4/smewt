#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, re

if len(sys.argv) != 2:
    print 'Error: you need to specify a version number for the make_release script to work. Aborting...'
    sys.exit(1)


VERSION = sys.argv[1]


# write version number to file
sinit = open('smewt/__init__.py').read()
sinit = re.sub('__version__ =.*', '__version__ = \'%s\'' % VERSION, sinit)
sinit = re.sub('MAIN_LOGGING_LEVEL =.*', 'MAIN_LOGGING_LEVEL = logging.WARNING', sinit)

sinit = re.sub('APP_NAME = .*', 'APP_NAME = \'Smewt\'', sinit)
open('smewt/__init__.py', 'w').write(sinit)


# replace logging function call in smewg
smewg = open('bin/smewg').read()
logfunc = [ l for l in open('utils/slogging.py') if l[0] != '#' ]
smewg = smewg.replace('''from utils.slogging import setupLogging
setupLogging()''', ''.join(logfunc) + '\nsetupLogging()\n')
open('bin/smewg', 'w').write(smewg)



#os.system('git commit -a -m "Tagged %s release"' % VERSION)
#os.system('git tag ' + VERSION)


# generate and upload package to PyPI
# TODO: generate win packages
#os.system('python setup.py sdist upload')

print 'Successfully made release ' + VERSION
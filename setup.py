#!/usr/bin/env python
from __future__ import absolute_import
from __future__ import print_function
from distutils.core import setup
import re


modcontents = open('bottle_pydal.py').read()
version = re.search(r"__version__ = '([^']*)'",modcontents).group(1)
del modcontents

setup(
        name = 'bottle-pydal',
        version = version,
        description = 'PyDAL for bottle.',
        author = 'James P Burke',
        author_email = 'james.burke1203@gmail.com',
        license = 'Artistic',
        py_modules = [ 'bottle_pydal' ],
        url = 'https://bitbucket.org/devries/bottle-session',
        install_requires = [
            'bottle >=0.9',
            'pydal'
            ],
        classifiers = [
            'Development Status :: 4 - Beta',
            'Framework :: Bottle',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Artistic License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Internet :: WWW/HTTP :: WSGI :: Application'
            ]
        )
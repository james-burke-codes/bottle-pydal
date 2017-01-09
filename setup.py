#!/usr/bin/env python3
from __future__ import absolute_import
from __future__ import print_function
from setuptools import setup
import re


modcontents = open('bottle_pydal.py').read()
version = re.search(r"__version__ = '([^']*)'",modcontents).group(1)
del modcontents

setup(
        name = 'bottle-pydal',
        version = version,
        description = 'PyDAL for bottle - See Github for more info',
        author = 'James P Burke',
        author_email = 'james.burke1203@gmail.com',
        license = 'LGPL v3.0',
        py_modules = [ 'bottle_pydal' ],
        url = 'https://github.com/peregrinius/bottle-pydal',
        install_requires = [
            'bottle >=0.9',
            'pydal'
            ],
        classifiers = [
            'Development Status :: 4 - Beta',
            'Framework :: Bottle',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Internet :: WWW/HTTP :: WSGI :: Application'
            ]
        )
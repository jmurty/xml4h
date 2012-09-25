#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import xml4h

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# Custom commands
# TODO Worth making proper custom commands, per gist.github.com/2366194 ?
if sys.argv[-1] == 'test-docs':
    os.system(r'nosetests --verbose --nocapture'
              r' --include=docs --ignore-files=\.py'
              r' --with-doctest --doctest-extension=.rst')
    sys.exit()
elif sys.argv[-1] == 'test-coverage':
    os.system(r'nosetests --nocapture'
              r' --with-coverage --cover-package=xml4h')
    sys.exit()


setup(
    name='xml4h',
    version=xml4h.__version__,
    description='Python XML for Humans.',
    long_description=open('README.rst').read(),
    author='James Murty',
    author_email='james@murty.co',
    url='TODO',
    packages=[
        'xml4h',
        'xml4h.impls',
    ],
    package_data={'': ['LICENSE']},
    include_package_data=True,
    install_requires=None,
    license=open('LICENSE').read(),
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Text Processing :: Markup :: XML',
        'Natural Language :: English',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 3.0',
        # 'Programming Language :: Python :: 3.1',
        # 'Programming Language :: Python :: 3.2',
    ),
)


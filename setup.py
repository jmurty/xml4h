#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import xml4h

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


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


#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml4h

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name=xml4h.__title__,
    version=xml4h.__version__,
    description='XML for Humans in Python',
    long_description=open('README.rst').read(),
    long_description_content_type='text/x-rst',
    author='James Murty',
    author_email='james@murty.co',
    url='https://github.com/jmurty/xml4h',
    packages=[
        'xml4h',
        'xml4h.impls',
    ],
    package_dir={'xml4h': 'xml4h'},
    package_data={'': ['README.rst', 'LICENSE']},
    include_package_data=True,
    install_requires=[
        'six',
    ],
    license='MIT License',
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Text Processing :: Markup :: XML',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    test_suite='tests',
)

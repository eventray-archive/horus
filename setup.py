#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import os
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


def content_of(*files):
    import codecs
    here = os.path.abspath(os.path.dirname(__file__))
    content = []
    for f in files:
        with codecs.open(os.path.join(here, f), encoding='utf-8') as stream:
            content.append(stream.read())
    return '\n'.join(content)


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # Import here, because outside the eggs aren't loaded
        import pytest
        result = pytest.main(self.test_args)
        sys.exit(result)

requires = [
    'sqlalchemy',
    'zope.sqlalchemy',
    'transaction',
    'cryptacular',
    'deform',
    'pystache',
    'hem',
    'beaker',
    'pyramid',
    'pyramid_mailer',
    'pyramid_beaker',
    'pyramid_deform',
    'pyramid_mako',
]

setup(
    name='horus',
    version='0.9.14dev',
    description='Generic user registration for pyramid',
    long_description=content_of('README.rst'),
    classifiers=[  # http://pypi.python.org/pypi?:action=list_classifiers
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        'License :: OSI Approved :: BSD License',
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    author='John Anderson',
    author_email='sontek@gmail.com',
    url='https://github.com/eventray/horus',
    keywords=['pyramid', 'authentication', 'user registration'],
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    entry_points="""\
    [console_scripts]
    horus_scaffold = horus.scripts.scaffold:main
    """,
    tests_require=requires + ['pytest', 'mock', 'webtest', 'pytest-cov',
        'psycopg2'],
    cmdclass={'test': PyTest},
    test_suite='horus',
)

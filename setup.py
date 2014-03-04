#!/usr/bin/env python
#
# Copyright (c) 2011-2013 Ivan Zakrevsky
# Licensed under the terms of the BSD License (see LICENSE.txt)
import os.path
from setuptools import setup, find_packages

app_name = os.path.basename(os.path.dirname(os.path.abspath(__file__)))

setup(
    name = app_name,
    version = '0.7.4.1',

    packages = find_packages(),
    include_package_data=True,

    author = "Ivan Zakrevsky",
    author_email = "ivzak@yandex.ru",
    description = "Django-versioning allows you to version the data stored in django models, and stores only diff, not content copy.",
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    license = "BSD License",
    keywords = "versioning revision model django changeset reversion",
    tests_require = [
        'Django>=1.3',
    ],
    test_suite = 'runtests.main',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    url = "https://bitbucket.org/emacsway/{0}".format(app_name),
)

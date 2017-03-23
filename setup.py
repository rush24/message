#!/usr/bin/env python
# coding: utf-8

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from os import path


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'requirements.txt')) as f:
    all_reqs = f.read().split('\n')

install_requires = [x.strip() for x in all_reqs if 'git+' not in x]

setup(
    name='message',
    version='0.1.0',
    license='private',
    description='message',
    author='xiaotan2424@gmail.com',
    packages=['test'],
    install_requires=install_requires,
    entry_points='''
    [console_scripts]
    message=message.app:main
    ''',
)


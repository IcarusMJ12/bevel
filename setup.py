#!/usr/bin/env python

from setuptools import setup

setup(name = 'bevel',
        version = '0.1.2',
        description = 'a selection of tools for viewing and editing bencoded entities',
        author = 'Igor Kaplounenko',
        author_email = 'igor@bittorrent.com',
        license = 'BSD',
        keywords = 'bevel bencode bittorrent utorrent',
        provides = ['bevel'],
        requires = ['bencode (>=1.0)'],
        py_modules = ['bevel'],
        scripts = ['bcat', 'bgrep', 'bsed'],
        long_description = open('README').read()
)

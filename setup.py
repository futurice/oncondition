#!/usr/bin/env python
from setuptools import setup, find_packages, Command
from setuptools.command.test import test

import os, sys, subprocess

class TestCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        raise SystemExit(
            subprocess.call([sys.executable,
                             'app_test_runner.py',
                             'test']))

install_requires = ['celery>=3', 'django-dirtyfield>=0.9',]
base_dir = os.path.dirname(os.path.abspath(__file__))

setup(
    name = "oncondition",
    version = "0.8",
    description = "Event classes that fire actions on conditions. Supports Django.",
    url = "http://github.com/futurice/oncondition",
    author = "Jussi Vaihia",
    author_email = "jussi.vaihia@futurice.com",
    packages = ["oncondition"],
    include_package_data = True,
    keywords = 'django event condition transparency',
    license = 'BSD',
    install_requires = install_requires,
    cmdclass = {
        'test': TestCommand,
    },
)

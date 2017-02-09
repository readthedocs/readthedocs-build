# -*- coding: utf-8 -*-
import codecs
from setuptools import find_packages
from setuptools import setup


setup(
    name='readthedocs-build',
    version='2.0.6',
    author='Eric Holscher',
    author_email='eric@ericholscher.com',
    url='https://readthedocs.org',
    license='MIT',
    description='Build infrastructure for Read the Docs',
    packages=find_packages(),
    include_package_data=True,
    long_description=codecs.open("README.rst", "r", "utf-8").read(),
    install_requires=[
        "PyYAML>=3.0",
        "Sphinx>=1.3",
        "Docutils",
        "readthedocs-sphinx-ext",
        "recommonmark",
        "click>=4.0",
        "virtualenv",
    ],
    entry_points={
        'console_scripts': [
            'rtd-build=readthedocs_build.cli:main',
        ]
    },
    zip_safe=True,
)

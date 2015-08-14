# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup


setup(
    name='my_python_package',
    version='0.1.0',
    author='Eric Holscher',
    author_email='eric@ericholscher.com',
    url='https://readthedocs.org',
    license='MIT',
    description='For testing',
    packages=find_packages(),
    include_package_data=True,
    long_description='',
    zip_safe=True,
)

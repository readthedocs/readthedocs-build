import codecs
try:
    from setuptools import setup, find_packages
    extra_setup = dict(
        zip_safe=True,
        install_requires=[
            "PyYAML>=3.0"
        ],
    )
except ImportError:
    from distutils.core import setup
    extra_setup = {}

setup(
    name='readthedocs-build',
    version='1.0.0',
    author='Eric Holscher',
    author_email='eric@ericholscher.com',
    url='https://readthedocs.org',
    license='MIT',
    description='Build infrastructure for Read the Docs',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    long_description=codecs.open("README.rst", "r", "utf-8").read(),
    entry_points={
        'console_scripts': [
            'readthedocs-build=cli:run_main',
            'rtd-build=cli:run_main',
            'rtfd-build=cli:run_main',
        ]
    },
    **extra_setup
)

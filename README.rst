Read the Docs Builder
=====================

This module is the main building interface to Read the Docs.
It has no explicit dependency on RTD code itself,
and can be used outside of RTD to test your builds.

.. warning::
    This code is still under active development and isn't considered
    stable. Please report bugs you find and contribute back if you are so
    inclined.

Install
-------

Install with pip::

    pip install readthedocs-build

CLI Use
-------

Running a build is simple::

    rtd-build

This will search for all ``readthedocs.yml`` (or ``.readthedocs.yml``) files
below your current directory and will build your documentation.

You can set a specific a directory where the built documentation should be
stored::

    rtd-build --outdir=out_dir

The documentation will then be placed in `out_dir/<name>/html/`. Where `<name>`
is the name configured in your `readthedocs.yml`. The default for ``--outdir``
is `_readthedocs_build`.

Run `rtd-build --help` for more information.

The Build
---------

Here is a list of steps that `rtd-build` performs to built your documentation.
All these steps are performed for each individual section in your
``readthedocs.yml`` configs.

- it creates a new virtual environment with ``virtualenv``
- it installs the builder's dependencies into the virtualenv, for example
  ``Sphinx``
- it runs the build command (e.g. ``sphinx-build``) on your documentation and
  puts the output into the directory specified with ``--outdir``.
- it removes the virtualenv

Library Use
-----------

An example use of this library is:

.. code-block:: python

    import os
    from readthedocs_build.build import build

    build([{
        'output_base': os.path.abspath('outdir'),
        'name': 'docs',
        'type': 'sphinx',
        'base': os.path.dirname(os.path.abspath(__file__)),
    }])

Development
-----------

Just run::

    pip install -e .

This will install the project into your environment, and have it pick up
changes as you edit them in the code.

To run the tests::

    tox

Build Process
-------------

Read the Docs creates a full environment for your build. In your local
environment, you can choose what portions of this environment to re-create.
You can either use your existing environment with our builder code installed,
or allow our builder to create a fully isolated environment for itself. A fully
isolated environment is much closer to our production build environment for
testing purposes.

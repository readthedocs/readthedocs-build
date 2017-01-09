Specification
=============

``rtd-build`` is a tool that can build Sphinx documentation. It is used
internally by readthedocs.org to build all Sphinx based documentation.

Creating a build works like this:

- change into the root of the project that you want to build the documentation
  for
- run ``rtd-build``

``rtd-build`` will then perform the following actions:

- it searches for all ``readthedocs.yml`` files below the current directory
  and merges all found files into a list of configurations
- it iterates over all configurations (order is not garuanteed) and performs
  the following actions for each:

  - create a fresh virtualenv
  - ``cd`` into the base directory of the documentation
  - ``pip install ...`` whatever is configured in the config
  - ``python setup.py install`` if configured (from the path specified in
    ``python.setup_path``.
  - run ``sphinx-build``

``readthedocs.yml`` spec
------------------------

A ``readthedocs.yml`` file must be in YAML format. If the top level is a block
sequence (i.e. a list), then the file describes multiple configurations. If
the top level is mapping, then the file describes a single configuration.

A few complete examples:

- config file living at the root of the repository, configuring only one
  documentation:

  .. code-block:: yaml

    # in /readthedocs.yml
    base: docs/
    type: sphinx
    formats:
        html: true
        pdf: true
    python:
        setup_install: true

- A project with multiple documentations. The on in ``docs/`` is the english
  one and considered the main documentation. ``docs-de/`` contains a second
  documentation which is the german translation of ``docs/``.

  .. code-block:: yaml

    # in /docs/readthedocs.yml
    type: sphinx
    language: en
    python:
        requirements:
            - "-r../requirements.txt"
        setup_install: true

    # in /docs-de/readthedocs.yml
    extend: docs/readthedocs.yml
    language: de

- The same as the previous example but with everything configured in one
  ``readthedocs.yml`` in the root of the project:

  .. code-block:: yaml

    - name: en
      type: sphinx
      language: en
      base: docs/
      python:
        requirements:
            - "-rrequirements.txt"
        setup_install: true

    - name: de
      extend: en
      language: de
      base: docs-de/


Following mapping keys are supported (all but the marked once are optional):

``extend``
    References the name of another configuration. All mapping keys are
    inherited, except for ``name`` and ``base``.

``name``
    An identifier of the documentation that this config is about. It might
    simply be ``docs``, or ``docs-de``. It's arbitrary, but must be unique
    with in all readthedocs configs in one project. It can be used to refer to
    a different configuration.

    It defaults to the path of the file relative to the project root. E.g. the
    config in ``api-docs/readthedocs.yml`` will get the name
    ``api-docs/readthedocs.yml`` by default. Since the ``name`` must be
    unique, it's an error to have two configurations without a name in the
    same file.

``base``
    The path to the root directory of the documentation that this config is
    about. That is usually the path that contains the ``conf.py`` file. It
    defaults to the directory that the ``readthedocs.yml`` file lives in. All
    commands for building the documentation will have the ``base`` set as
    working directory.

``type``, *required*
    The documentation framework that this documentation is written in. Allowed
    values are:

    - ``sphinx``
    - ``mkdocs``

``formats``
    A mapping of format types to shall be built. The following formats are
    supported:

    - ``html``, default: ``true``
    - ``pdf``, default: ``false``
    - ``epub``, default: ``false``

``python``
    Python specific configuration. All builds are executed inside a
    virtualenv. This config can customize the virtualenv before running the
    build. The following subkeys are allowed:

    ``pip_requirements``
        A list of arguments that will be passed down to a ``pip install``
        call. You can specify requirements files with ``-r
        path/to/requirements.txt``. Accepts version modifiers like
        ``setuptools>=18.0``.

    ``extra_requirements``
        A list of `extra requirements`_ sections to install, additionnaly to
        the `package default dependencies`_. Ignored if the ``setup_install``
        option below is ``true``.

    ``setup_install``
        If ``true``, then ``python setup.py install`` will be executed before
        building the docs.

    ``setup_path``
        The path in which ``python setup.py install`` will be executed.
        Defaults to the repository root.

    ``version``
        The Python interpreter version to use for all build calls. This value
        should be a float or integer value.

        Supported versions can be configured on config instantiation by passing
        in the following to the `env_config`::

            {
                'python': {
                    'supported_versions': [2, 2.7, 3, 3.5],
                }
            }

``language``
    The language the doc is written in. Defaults to empty string.


.. _extra requirements: http://setuptools.readthedocs.io/en/latest/setuptools.html#declaring-extras-optional-features-with-their-own-dependencies
.. _package default dependencies: http://setuptools.readthedocs.io/en/latest/setuptools.html#declaring-dependencies

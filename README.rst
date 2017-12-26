Read the Docs Builder
=====================

.. warning::
   This repo is only used as a configuration parser for readthedocs.org builds,
   and it's unsupported for other uses.

Install
-------

Install with pip::

    pip install readthedocs-build

Library Use
-----------

Example uses of this library is:

* https://github.com/rtfd/readthedocs.org/blob/master/readthedocs/doc_builder/config.py#L8-L9
* https://github.com/rtfd/readthedocs.org/blob/master/readthedocs/projects/tasks.py#L27


Development
-----------

Just run::

    pip install -e .

This will install the project into your environment, and have it pick up
changes as you edit them in the code.

To run the tests::

    tox

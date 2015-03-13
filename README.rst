Read the Docs Builder
=====================

This module is the main building interface to Read the Docs.
It has no explicit dependency on RTD code itself,
and can be used outside of RTD to test your builds.

An example use of this library is:


.. code-block:: python

	import os

	from doc_builder.loader import loading
	from doc_builder.state import BuildState

	docs_dir = os.getcwd()

	state = BuildState(root=docs_dir)
	BuilderClass = loading.get('sphinx')
	builder = BuilderClass(state=state)
	builder.build()

This will run the same code as RTD,
so you should be able to debug the build more easily.

Development
-----------

Just run::

    pip install -e .

This will install the project into your environment, and have it pick up changes as you edit them in the code.

To run the tests::

    ./runtests.sh

Build Process
-------------

Read the Docs creates a full environment for your build.
In your local environment,
you can choose what portions of this environment to re-create.
You can either use your existing environment with our builder code installed,
or allow our builder to create a fully isolated environment for itself.
A fully isolated environment is much closer to our production build environment for testing purposes.

Using
~~~~~

Running a build is simple::

	rtd-build 

You can set a specific output directory::

	rtd-build --output=html_dir

Run a fully isolated build::

	rtd-build --full --output=html_dir

Read the Docs Builder
=====================

This module is the main building interface to Read the Docs.
It has no explicit dependency on RTD code itself,
and can be used outside of RTD to test your builds.

An example use of this library is:


.. code-block::

	>>> from readthedocs.build import loading
	>>> from readthedocs.build import state

	>>> build_state = state.load('.readthedocs.yml')
	>>> BuilderClass = loading.get(build_state.documentation_type)
	>>> builder = BuilderClass(build_state)
	>>> builder.append_conf()
	>>> builder.build()

This will run the same code as RTD,
so you should be able to debug the build more easily.

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

	rtd-build -o site

You can also 

Steps
~~~~~

Configuration
~~~~~~~~~~~~~



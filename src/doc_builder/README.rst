Read the Docs Builder
=====================

This module is the main building interface to Read the Docs.
It has no explicit dependency on RTD code itself,
and can be used outside of RTD to test your builds.

An example use of this library is:


.. doctest::

	>>> from readthedocs.doc_builder import loading
	>>> from readthedocs.doc_builder import state

	>>> build_state = state.load('.readthedocs.yml')
	>>> BuilderClass = loading.get(build_state.documentation_type)
	>>> builder = BuilderClass(build_state)
	>>> builder.append_conf()
	>>> builder.build()

This will run the same code as RTD,
so you should be able to debug the build more easily.
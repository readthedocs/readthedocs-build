import os
import subprocess
import tempfile
import shutil

from unittest import TestCase

from doc_builder.loader import loading
from doc_builder.state import BuildState


def run():
    docs_dir = os.getcwd()

    state = BuildState(root=docs_dir)
    BuilderClass = loading.get('sphinx')
    builder = BuilderClass(state=state)

    builder.append_conf()
    builder.build()

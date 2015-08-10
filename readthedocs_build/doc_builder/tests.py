import os
import subprocess
import tempfile
import shutil

from unittest import TestCase

from readthedocs_build.doc_builder.loader import loading
from readthedocs_build.doc_builder.state import BuildState


class TestState(TestCase):

    def test_local_build(self):

        test_dir = os.path.dirname(os.path.realpath(__file__))
        docs_dir = os.path.normpath(os.path.join(test_dir, os.pardir, os.pardir, 'docs'))

        state = BuildState(root=docs_dir)
        BuilderClass = loading.get('sphinx')
        builder = BuilderClass(state=state)

        builder.append_conf()
        builder.build()
        self.assertIn('index.html', os.listdir(state.output_path))
        shutil.rmtree(state.output_path)

    def test_total_build(self):

        self.root = tempfile.mkdtemp()

        repo_url = 'file://' + subprocess.check_output('git rev-parse --show-toplevel', shell=True).strip()
        state = BuildState(root=self.root, repo=repo_url)
        BuilderClass = loading.get('sphinx')
        builder = BuilderClass(state=state)

        builder.checkout_code()
        builder.setup_environment()
        builder.append_conf()
        builder.build()
        self.assertIn('index.html', os.listdir(state.output_path))

        shutil.rmtree(self.root)

import os
import subprocess
import tempfile
import shutil

from unittest import TestCase

from doc_builder.loader import loading
from doc_builder.state import BuildState


class TestState(TestCase):

    def test_local_build(self):

        test_dir = os.path.dirname(os.path.realpath(__file__))
        docs_dir = os.path.normpath(os.path.join(test_dir, os.pardir, os.pardir, 'docs'))

        state = BuildState(root=docs_dir)
        BuilderClass = loading.get('sphinx')
        builder = BuilderClass(state=state)

        builder.build()
        build_dir = os.path.join(docs_dir, '_readthedocs_build', 'html')
        self.assertIn('index.html', os.listdir(build_dir))

        shutil.rmtree(os.path.join(docs_dir, '_readthedocs_build'))

    def test_total_build(self):

        self.root = tempfile.mkdtemp()

        repo_url = 'file://' + subprocess.check_output('git rev-parse --show-toplevel', shell=True).strip()
        state = BuildState(root=self.root, repo=repo_url)
        BuilderClass = loading.get('sphinx')
        builder = BuilderClass(state=state)

        builder.checkout_code()
        builder.setup_environment()
        # print builder.append_conf()
        builder.build()
        build_dir = os.path.join(self.root, '_readthedocs_build', 'html')
        self.assertIn('index.html', os.listdir(build_dir))

        shutil.rmtree(self.root)

import os
import shutil
import tempfile

from .utils import run


class VirtualEnv(object):
    """
    Light abstraction of a virtualenv.
    """

    def __init__(self):
        self.base_path = tempfile.mkdtemp()
        self.setup()

    def setup(self):
        exit_code = run([
            'virtualenv',
            '--python=/usr/bin/python2.7',
            self.base_path,
        ])
        assert exit_code == 0, 'virtualenv setup failed'

    def cleanup(self):
        if os.path.exists(self.base_path):
            shutil.rmtree(self.base_path)

    def __del__(self):
        self.cleanup()

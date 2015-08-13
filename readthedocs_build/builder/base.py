import shutil
import subprocess
import tempfile


def run(args):
    popen = subprocess.Popen(args)
    return popen.wait()


class BaseBuilder(object):
    def __init__(self, build_config):
        self.build_config = build_config

    def setup(self):
        self.setup_virtualenv()

    def setup_virtualenv(self):
        self.virtualenv_path = tempfile.mkdtemp()
        run([
            'virtualenv',
            '--interpreter=/usr/bin/python2.7',
            self.virtualenv_path,
        ])

    def build(self):
        """
        Initializes the build.
        """
        self.setup()
        self.build_html()
        self.cleanup()

    def build_html(self):
        # Must be overriden by subclass.
        pass

    def cleanup(self):
        shutil.rmtree(self.virtualenv_path)

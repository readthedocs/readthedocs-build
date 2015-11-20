import os
import shutil
import tempfile

from .utils import run


class VirtualEnv(object):
    """
    Light abstraction of a virtualenv.
    """

    def __init__(self, system_site_packages=False):
        self.base_path = tempfile.mkdtemp()
        self.system_site_packages = system_site_packages
        self.setup()

    def python_run(self, command_bin, args):
        """
        Execute a script from the virtualenv by using the bin/python from the
        virtualenv. That prevents an issue with too long shbangs. See
        https://github.com/rtfd/readthedocs.org/issues/994 for details.

        ``command_bin`` can be the name of an executable installed in the
        virtualenv or an absolute path to a python script.
        """
        python_bin = os.path.join(self.base_path, 'bin', 'python')
        command_bin = os.path.join(self.base_path, 'bin', command_bin)
        return run([
            python_bin,
            command_bin,
        ] + list(args))

    def setup(self):
        params = [
            'virtualenv',
            self.base_path,
            '--python=/usr/bin/python2.7',
        ]
        if self.system_site_packages:
            params.append('--system-site-packages')

        exit_code = run(params)
        assert exit_code == 0, 'virtualenv setup failed'

    def cleanup(self):
        if os.path.exists(self.base_path):
            shutil.rmtree(self.base_path)

    def __del__(self):
        self.cleanup()

    def install(self, package):
        exit_code = self.python_run('pip', ['install', package])
        assert exit_code == 0

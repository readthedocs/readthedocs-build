import os
import subprocess

from readthedocs_build.utils import cd


def test_minimal_project(tmpdir):
    base_path = os.path.dirname(os.path.abspath(__file__))
    with cd(base_path):
        process = subprocess.Popen([
            'rtd-build',
            'minimal_project',
            '--outdir={}'.format(tmpdir)
        ])
        process.wait()
        assert process.returncode == 0

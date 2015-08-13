import re
import os
import subprocess

from readthedocs_build.utils import cd


def test_minimal_project(tmpdir):
    base_path = os.path.dirname(os.path.abspath(__file__))
    out_dir = tmpdir.join('out')
    with cd(base_path):
        process = subprocess.Popen([
            'rtd-build',
            'minimal_project',
            '--outdir={}'.format(out_dir)
        ])
        process.wait()
        assert process.returncode == 0

    # Assert that the index was built.
    index_html = out_dir.join('docs', 'html', 'index.html')
    assert index_html.exists()
    assert re.search(
        '<title>Welcome to minimal_project.*</title>',
        index_html.read())

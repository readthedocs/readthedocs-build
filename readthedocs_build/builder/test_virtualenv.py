from mock import patch

from .virtualenv import VirtualEnv


def test_creates_virtualenv():
    with patch('readthedocs_build.builder.virtualenv.run') as run:
        run.return_value = 0

        venv = VirtualEnv()
        run.assert_called_with([
            'virtualenv',
            '--interpreter=/usr/bin/python2.7',
            venv.base_path,
        ])


def test_cleanup_deletes_virtualenv(tmpdir):
    venv_dir = str(tmpdir.mkdir('venv'))
    with patch.object(VirtualEnv, '__init__') as __init__:
        __init__.return_value = None
        venv = VirtualEnv()
        venv.base_path = venv_dir
        venv.cleanup()
        assert not tmpdir.join('venv').exists()

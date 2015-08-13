from mock import patch
import os

from .virtualenv import VirtualEnv


def test_creates_virtualenv():
    with patch('readthedocs_build.builder.virtualenv.run') as run:
        run.return_value = 0

        venv = VirtualEnv()
        run.assert_called_with([
            'virtualenv',
            '--python=/usr/bin/python2.7',
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


def test_python_run(tmpdir):
    with patch('readthedocs_build.builder.virtualenv.run') as run:
        with patch.object(VirtualEnv, 'setup'):
            venv = VirtualEnv()
            venv.python_run('pip', args=['freeze'])
            run.assert_called_with([
                os.path.join(venv.base_path, 'bin', 'python'),
                os.path.join(venv.base_path, 'bin', 'pip'),
                'freeze',
            ])


def test_install(tmpdir):
    with patch.object(VirtualEnv, 'setup'):
        with patch.object(VirtualEnv, 'python_run') as python_run:
            python_run.return_value = 0
            venv = VirtualEnv()
            venv.install('FooBar')
            python_run.assert_called_with('pip', ['install', 'FooBar'])

            venv.install('FooBar>=1.2')
            python_run.assert_called_with('pip', ['install', 'FooBar>=1.2'])

            venv.install('-rrequirements.txt')
            python_run.assert_called_with(
                'pip', ['install', '-rrequirements.txt'])

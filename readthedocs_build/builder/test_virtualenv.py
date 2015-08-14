from mock import patch
import os

from .virtualenv import VirtualEnv


def test_creates_default_virtualenv():
    with patch('readthedocs_build.builder.virtualenv.run') as run:
        run.return_value = 0

        venv = VirtualEnv()
        assert not venv.system_site_packages
        run.assert_called_with([
            'virtualenv',
            venv.base_path,
            '--python=/usr/bin/python2.7',
        ])


def test_it_respects_system_site_packages_flag():
    with patch('readthedocs_build.builder.virtualenv.run') as run:
        run.return_value = 0

        venv = VirtualEnv(system_site_packages=True)
        assert venv.system_site_packages
        run.assert_called_with([
            'virtualenv',
            venv.base_path,
            '--python=/usr/bin/python2.7',
            '--system-site-packages',
        ])


def test_cleanup_deletes_virtualenv(tmpdir):
    venv_dir = str(tmpdir.mkdir('venv'))
    with patch.object(VirtualEnv, '__init__') as __init__:
        __init__.return_value = None
        venv = VirtualEnv()
        venv.base_path = venv_dir
        venv.cleanup()
        assert not tmpdir.join('venv').exists()


def describe_python_run():
    def it_takes_relative_executable():
        with patch('readthedocs_build.builder.virtualenv.run') as run:
            with patch.object(VirtualEnv, 'setup'):
                venv = VirtualEnv()
                venv.python_run('pip', args=['freeze'])
                run.assert_called_with([
                    os.path.join(venv.base_path, 'bin', 'python'),
                    os.path.join(venv.base_path, 'bin', 'pip'),
                    'freeze',
                ])

    def it_takes_absolute_path_to_script(tmpdir):
        with patch('readthedocs_build.builder.virtualenv.run') as run:
            with patch.object(VirtualEnv, 'setup'):
                setup_py = str(tmpdir.join('setup.py'))
                venv = VirtualEnv()
                venv.python_run(setup_py, [])
                run.assert_called_with([
                    os.path.join(venv.base_path, 'bin', 'python'),
                    setup_py,
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

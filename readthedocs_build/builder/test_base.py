from mock import patch

from .base import BaseBuilder


def get_config(extra=None):
    defaults = {
        'name': 'docs',
        'type': 'sphinx',
        'python': {
            'use_system_site_packages': False,
            'setup_py_install': False,
            'setup_py_path': '',
        },
        'output_base': '/tmp',
    }
    if extra is not None:
        defaults.update(extra)
    return defaults


def test_build_calls_setup():
    build_config = get_config()
    with patch.object(BaseBuilder, 'setup') as setup:
         with patch.object(BaseBuilder, 'cleanup'):
            builder = BaseBuilder(build_config=build_config)
            builder.build()
            setup.assert_called_with()


def test_build_calls_cleanup():
    build_config = get_config()
    with patch('readthedocs_build.builder.base.VirtualEnv'):
        with patch.object(BaseBuilder, 'cleanup') as cleanup:
            builder = BaseBuilder(build_config=build_config)
            builder.build()
            cleanup.assert_called_with()
        # Do real cleanup.
        builder.cleanup()


def test_build_calls_build_html():
    build_config = get_config()
    with patch('readthedocs_build.builder.base.VirtualEnv'):
        with patch.object(BaseBuilder, 'build_html') as build_html:
            builder = BaseBuilder(build_config=build_config)
            builder.build()
            build_html.assert_called_with()


def test_build_calls_build_search_data():
    build_config = get_config()
    mock_venv = patch('readthedocs_build.builder.base.VirtualEnv')
    mock_build_html = patch.object(BaseBuilder, 'build_html')
    mock_build_search_data = patch.object(BaseBuilder, 'build_search_data')
    with mock_venv, mock_build_html:
        with mock_build_search_data as build_search_data:
            builder = BaseBuilder(build_config=build_config)
            builder.build()
            build_search_data.assert_called_with()


def test_setup_creates_virtualenv():
    build_config = get_config()
    builder = BaseBuilder(build_config=build_config)
    with patch('readthedocs_build.builder.base.VirtualEnv') as VirtualEnv:
        builder.setup()
        assert VirtualEnv.call_count == 1


def describe_setup_virtualenv():
    def it_respects_use_system_site_packages_config():
        build_config = get_config()
        build_config['python'].update({
            'use_system_site_packages': False
        })
        with patch('readthedocs_build.builder.base.VirtualEnv') as VirtualEnv:
            builder = BaseBuilder(build_config=build_config)
            builder.setup_virtualenv()
            VirtualEnv.assert_called_with(system_site_packages=False)

        build_config = get_config()
        build_config['python'].update({
            'use_system_site_packages': True
        })
        with patch('readthedocs_build.builder.base.VirtualEnv') as VirtualEnv:
            builder = BaseBuilder(build_config=build_config)
            builder.setup_virtualenv()
            VirtualEnv.assert_called_with(system_site_packages=True)

    def it_executes_setup_py_install(tmpdir):
        setup_py = str(tmpdir.join('setup.py'))
        build_config = get_config()
        build_config['python'].update({
            'setup_py_install': True,
            'setup_py_path': setup_py,
        })
        with patch('readthedocs_build.builder.base.VirtualEnv') as VirtualEnv:
            VirtualEnv.return_value = VirtualEnv
            builder = BaseBuilder(build_config=build_config)
            builder.setup_virtualenv()
            VirtualEnv.python_run.assert_called_with(
                setup_py,
                ['install'])


def test_cleanup_removes_virtualenv(tmpdir):
    build_config = get_config()
    builder = BaseBuilder(build_config=build_config)
    with patch('readthedocs_build.builder.base.VirtualEnv'):
        builder.setup()
        builder.cleanup()
        builder.venv.cleanup.assert_called_with()

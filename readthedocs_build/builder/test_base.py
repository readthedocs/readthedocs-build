from mock import patch

from .base import BaseBuilder


def test_build_calls_setup():
    build_config = {'name': 'docs', 'type': 'sphinx'}
    with patch.object(BaseBuilder, 'setup') as setup:
         with patch.object(BaseBuilder, 'cleanup'):
            builder = BaseBuilder(build_config=build_config)
            builder.build()
            setup.assert_called_with()


def test_build_calls_cleanup():
    build_config = {'name': 'docs', 'type': 'sphinx'}
    with patch('readthedocs_build.builder.base.VirtualEnv'):
        with patch.object(BaseBuilder, 'cleanup') as cleanup:
            builder = BaseBuilder(build_config=build_config)
            builder.build()
            cleanup.assert_called_with()
        # Do real cleanup.
        builder.cleanup()


def test_build_calls_build_html():
    build_config = {'name': 'docs', 'type': 'sphinx'}
    with patch('readthedocs_build.builder.base.VirtualEnv'):
        with patch.object(BaseBuilder, 'build_html') as build_html:
            builder = BaseBuilder(build_config=build_config)
            builder.build()
            build_html.assert_called_with()


def test_setup_creates_virtualenv():
    build_config = {'name': 'docs', 'type': 'sphinx'}
    builder = BaseBuilder(build_config=build_config)
    with patch('readthedocs_build.builder.base.VirtualEnv') as VirtualEnv:
        builder.setup()
        VirtualEnv.assert_called_with()


def test_cleanup_removes_virtualenv(tmpdir):
    build_config = {'name': 'docs', 'type': 'sphinx'}
    builder = BaseBuilder(build_config=build_config)
    with patch('readthedocs_build.builder.base.VirtualEnv'):
        builder.setup()
        builder.cleanup()
        builder.venv.cleanup.assert_called_with()

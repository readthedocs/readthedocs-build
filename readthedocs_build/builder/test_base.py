from mock import patch
import os

from ..testing.config import get_project_config
from .base import BaseBuilder


def test_build_calls_setup():
    build_config = get_project_config({
        'type': 'sphinx'
    })
    with patch.object(BaseBuilder, 'setup') as setup:
         with patch.object(BaseBuilder, 'cleanup'):
            builder = BaseBuilder(build_config=build_config)
            builder.build()
            setup.assert_called_with()


def test_build_calls_cleanup():
    build_config = get_project_config({
        'type': 'sphinx'
    })
    with patch('readthedocs_build.builder.base.run'):
        with patch.object(BaseBuilder, 'cleanup') as cleanup:
            builder = BaseBuilder(build_config=build_config)
            builder.build()
            cleanup.assert_called_with()
        # Do real cleanup.
        builder.cleanup()


def test_build_calls_build_html():
    build_config = get_project_config({
        'type': 'sphinx'
    })
    with patch('readthedocs_build.builder.base.run'):
        with patch.object(BaseBuilder, 'build_html') as build_html:
            builder = BaseBuilder(build_config=build_config)
            builder.build()
            build_html.assert_called_with()


def test_setup_creates_virtualenv():
    build_config = get_project_config({'type': 'sphinx'})
    builder = BaseBuilder(build_config=build_config)
    with patch('readthedocs_build.builder.base.run') as run:
        builder.setup()
        run.assert_called_with([
            'virtualenv',
            '--interpreter=/usr/bin/python2.7',
            builder.virtualenv_path,
        ])
        assert os.path.exists(builder.virtualenv_path)
    # Do real cleanup.
    builder.cleanup()


def test_cleanup_removes_virtualenv(tmpdir):
    venv = tmpdir.mkdir('venv')
    build_config = get_project_config({'type': 'sphinx'})
    builder = BaseBuilder(build_config=build_config)
    with patch.object(BaseBuilder, 'setup_virtualenv'):
        builder.setup()
        builder.virtualenv_path = str(venv)
        builder.cleanup()
        assert not venv.exists()

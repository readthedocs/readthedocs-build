from mock import patch

from ..testing.config import get_project_config
from .base import BaseBuilder


def test_build_calls_setup():
    build_config = get_project_config({
        'type': 'sphinx'
    })
    with patch.object(BaseBuilder, 'setup') as setup:
        builder = BaseBuilder(build_config=build_config)
        builder.build()
        setup.assert_called_with()


def test_build_calls_cleanup():
    build_config = get_project_config({
        'type': 'sphinx'
    })
    with patch.object(BaseBuilder, 'cleanup') as cleanup:
        builder = BaseBuilder(build_config=build_config)
        builder.build()
        cleanup.assert_called_with()


def test_build_calls_build_html():
    build_config = get_project_config({
        'type': 'sphinx'
    })
    with patch.object(BaseBuilder, 'build_html') as build_html:
        builder = BaseBuilder(build_config=build_config)
        builder.build()
        build_html.assert_called_with()

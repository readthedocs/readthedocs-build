from mock import patch

from ..testing.config import get_project_config
from .sphinx import SphinxBuilder


def test_setup_installs_sphinx():
    build_config = get_project_config({'type': 'sphinx'})
    builder = SphinxBuilder(build_config=build_config)
    with patch('readthedocs_build.builder.base.VirtualEnv'):
        builder.setup()
        assert any([
            args[0].startswith('Sphinx')
            for args, kwargs in builder.venv.install.call_args_list])

from mock import patch

from .sphinx import SphinxBuilder


def test_setup_installs_sphinx():
    build_config = {}
    builder = SphinxBuilder(build_config=build_config)
    with patch('readthedocs_build.builder.base.VirtualEnv'):
        builder.setup()
        assert any([
            args[0].startswith('Sphinx')
            for args, kwargs in builder.venv.install.call_args_list])

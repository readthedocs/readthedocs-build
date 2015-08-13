from mock import patch
from mock import Mock

from .testing.config import get_project_config
from .build import build
from .builder import builder_types


def test_build_triggers_sphinx_builder(tmpdir):
    config = get_project_config({'type': 'sphinx'})
    build_config = config[0]
    with tmpdir.as_cwd():
        sphinx_mock = Mock()
        sphinx_mock.return_value = sphinx_mock
        with patch.dict(builder_types, {'sphinx': sphinx_mock}):
            build(config)
            sphinx_mock.assert_called_with(build_config=build_config)
            sphinx_mock.setup.assert_called_with()
            sphinx_mock.build.assert_called_with()
            sphinx_mock.cleanup.assert_called_with()

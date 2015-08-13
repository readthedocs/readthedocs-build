from mock import patch
from mock import Mock

from .build import build
from .builder import builder_types


def test_build_triggers_sphinx_builder(tmpdir):
    project_config = [{
        'type': 'sphinx',
    }]
    with tmpdir.as_cwd():
        sphinx_mock = Mock()
        sphinx_mock.return_value = sphinx_mock
        with patch.dict(builder_types, {'sphinx': sphinx_mock}):
            build(project_config)
            sphinx_mock.assert_called_with(build_config=project_config[0])
            sphinx_mock.build.assert_called_with()

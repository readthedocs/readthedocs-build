from mock import patch
from mock import DEFAULT
from pytest import raises
import os

from ..testing.utils import apply_fs
from .config import InvalidConfig
from .config import load
from .config import BuildConfig
from .config import ProjectConfig
from .config import BASE_INVALID
from .config import BASE_NOT_A_DIR
from .config import TYPE_INVALID
from .config import TYPE_REQUIRED
from .config import NAME_REQUIRED
from .config import NAME_INVALID


env_config = {
    'output_base': '/tmp'
}


minimal_config = {
    'name': 'docs',
    'type': 'sphinx',
}


minimal_config_dir = {
    'readthedocs.yml': '''\
name: docs
type: sphinx
'''
}


multiple_config_dir = {
    'readthedocs.yml': '''
name: first
type: sphinx
---
name: second
type: sphinx
    ''',
    'nested': minimal_config_dir,
}


def test_load_no_config_file(tmpdir):
    base = str(tmpdir)
    with raises(InvalidConfig):
        load(base, env_config)


def test_load_empty_config_file(tmpdir):
    apply_fs(tmpdir, {
        'readthedocs.yml': ''
    })
    base = str(tmpdir)
    with raises(InvalidConfig):
        load(base, env_config)


def test_minimal_config(tmpdir):
    apply_fs(tmpdir, minimal_config_dir)
    base = str(tmpdir)
    config = load(base, env_config)
    assert isinstance(config, ProjectConfig)
    assert len(config) == 1
    build = config[0]
    assert isinstance(build, BuildConfig)


def test_build_config_has_source_file(tmpdir):
    base = str(apply_fs(tmpdir, minimal_config_dir))
    build = load(base, env_config)[0]
    assert build.source_file == os.path.join(base, 'readthedocs.yml')
    assert build.source_position == 0


def test_build_config_has_source_position(tmpdir):
    base = str(apply_fs(tmpdir, multiple_config_dir))
    builds = load(base, env_config)
    assert len(builds) == 3
    first, second = filter(
        lambda b: not b.source_file.endswith('nested/readthedocs.yml'),
        builds)
    third, = filter(
        lambda b: b.source_file.endswith('nested/readthedocs.yml'),
        builds)
    assert first.source_position == 0
    assert second.source_position == 1
    assert third.source_position == 0


def test_config_requires_name():
    build = BuildConfig({},
                        {},
                        source_file=None,
                        source_position=None)
    with raises(InvalidConfig) as excinfo:
        build.validate_name()
    assert excinfo.value.code == NAME_REQUIRED


def test_build_requires_valid_name():
    build = BuildConfig({},
                        {'name': 'with/slashes'},
                        source_file=None,
                        source_position=None)
    with raises(InvalidConfig) as excinfo:
        build.validate_name()
    assert excinfo.value.code == NAME_INVALID


def test_config_requires_type():
    build = BuildConfig({},
                        {'name': 'docs'},
                        source_file=None,
                        source_position=None)
    with raises(InvalidConfig) as excinfo:
        build.validate_type()
    assert excinfo.value.code == TYPE_REQUIRED


def test_build_requires_valid_type():
    build = BuildConfig({},
                        {'type': 'unknown'},
                        source_file=None,
                        source_position=None)
    with raises(InvalidConfig) as excinfo:
        build.validate_type()
    assert excinfo.value.code == TYPE_INVALID


def test_valid_build_config():
    build = BuildConfig(env_config,
                        minimal_config,
                        source_file='readthedocs.yml',
                        source_position=0)
    build.validate()
    assert build['type'] == 'sphinx'


def test_build_config_base(tmpdir):
    apply_fs(tmpdir, {'configs': minimal_config, 'docs': {}})
    with tmpdir.as_cwd():
        source_file = str(tmpdir.join('configs', 'readthedocs.yml'))
        build = BuildConfig(
            {},
            {'base': '../docs'},
            source_file=source_file,
            source_position=0)
        build.validate_base()
        assert build['base'] == str(tmpdir.join('docs'))


def test_build_config_invalid_base(tmpdir):
    apply_fs(tmpdir, minimal_config)
    with tmpdir.as_cwd():
        build = BuildConfig(
            {},
            {'base': 1},
            source_file=str(tmpdir.join('readthedocs.yml')),
            source_position=0)
        with raises(InvalidConfig) as excinfo:
            build.validate_base()
        assert excinfo.value.code == BASE_INVALID


def test_build_config_base_not_a_dir(tmpdir):
    apply_fs(tmpdir, minimal_config)
    build = BuildConfig(
        {},
        {'base': 'docs'},
        source_file=str(tmpdir.join('readthedocs.yml')),
        source_position=0)
    with raises(InvalidConfig) as excinfo:
        build.validate_base()
    assert excinfo.value.code == BASE_NOT_A_DIR


def test_build_validate_calls_all_subvalidators(tmpdir):
    apply_fs(tmpdir, minimal_config)
    build = BuildConfig(
        {},
        {},
        source_file=str(tmpdir.join('readthedocs.yml')),
        source_position=0)
    with patch.multiple(BuildConfig,
                        validate_base=DEFAULT,
                        validate_name=DEFAULT,
                        validate_type=DEFAULT,
                        validate_output_base=DEFAULT):
        build.validate()
        BuildConfig.validate_base.assert_called_with()


def test_validate_project_config():
    with patch.object(BuildConfig, 'validate') as build_validate:
        project = ProjectConfig([
            BuildConfig(
                env_config,
                minimal_config,
                source_file='readthedocs.yml',
                source_position=0)
        ])
        project.validate()
        assert build_validate.call_count == 1


def test_load_calls_validate(tmpdir):
    apply_fs(tmpdir, minimal_config_dir)
    base = str(tmpdir)
    with patch.object(BuildConfig, 'validate') as build_validate:
        load(base, env_config)
        assert build_validate.call_count == 1


def test_project_set_output_base():
    project = ProjectConfig([
        BuildConfig(
            env_config,
            minimal_config,
            source_file='readthedocs.yml',
            source_position=0),
        BuildConfig(
            env_config,
            minimal_config,
            source_file='readthedocs.yml',
            source_position=1),
    ])
    project.set_output_base('random')
    for build_config in project:
        assert (
            build_config['output_base'] == os.path.join(os.getcwd(), 'random'))

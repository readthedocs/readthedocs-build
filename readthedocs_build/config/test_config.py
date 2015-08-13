from mock import patch
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


minimal_config = {
    'type': 'sphinx',
}


minimal_config_dir = {
    'readthedocs.yml': '''\
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
        load(base)


def test_load_empty_config_file(tmpdir):
    apply_fs(tmpdir, {
        'readthedocs.yml': ''
    })
    base = str(tmpdir)
    with raises(InvalidConfig):
        load(base)


def test_minimal_config(tmpdir):
    apply_fs(tmpdir, minimal_config_dir)
    base = str(tmpdir)
    config = load(base)
    assert isinstance(config, ProjectConfig)
    assert len(config) == 1
    build = config[0]
    assert isinstance(build, BuildConfig)


def test_build_config_has_source_file(tmpdir):
    base = str(apply_fs(tmpdir, minimal_config_dir))
    build = load(base)[0]
    assert build.source_file == os.path.join(base, 'readthedocs.yml')
    assert build.source_position == 0


def test_build_config_has_source_position(tmpdir):
    base = str(apply_fs(tmpdir, multiple_config_dir))
    builds = load(base)
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


def test_build_requires_type():
    build = BuildConfig({},
                        source_file=None,
                        source_position=None)
    with raises(InvalidConfig) as excinfo:
        build.validate()
    assert excinfo.value.code == TYPE_REQUIRED


def test_build_requires_valid_type():
    build = BuildConfig({'type': 'unknown'},
                        source_file=None,
                        source_position=None)
    with raises(InvalidConfig) as excinfo:
        build.validate()
    assert excinfo.value.code == TYPE_INVALID


def test_valid_build_config():
    build = BuildConfig(minimal_config,
                        source_file='readthedocs.yml',
                        source_position=0)
    build.validate()
    assert build['type'] == 'sphinx'


def test_build_config_base(tmpdir):
    apply_fs(tmpdir, {'configs': minimal_config, 'docs': {}})
    with tmpdir.as_cwd():
        source_file = str(tmpdir.join('configs', 'readthedocs.yml'))
        build = BuildConfig({
            'type': 'sphinx',
            'base': '../docs'
        }, source_file=source_file, source_position=0)
        build.validate()
        assert build['base'] == str(tmpdir.join('docs'))


def test_build_config_invalid_base(tmpdir):
    apply_fs(tmpdir, minimal_config)
    with tmpdir.as_cwd():
        build = BuildConfig({
            'type': 'sphinx',
            'base': 1,
        }, source_file=str(tmpdir.join('readthedocs.yml')), source_position=0)
        with raises(InvalidConfig) as excinfo:
            build.validate()
        assert excinfo.value.code == BASE_INVALID


def test_build_config_base_not_a_dir(tmpdir):
    apply_fs(tmpdir, minimal_config)
    build = BuildConfig({
        'type': 'sphinx',
        'base': 'docs',
    }, source_file=str(tmpdir.join('readthedocs.yml')), source_position=0)
    with raises(InvalidConfig) as excinfo:
        build.validate()
    assert excinfo.value.code == BASE_NOT_A_DIR


def test_validate_project_config():
    with patch.object(BuildConfig, 'validate') as build_validate:
        project = ProjectConfig([
            BuildConfig(
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
        load(base)
        assert build_validate.call_count == 1

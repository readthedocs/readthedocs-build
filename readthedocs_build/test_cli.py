from click.testing import CliRunner
from mock import patch
import os

from .builder.base import BaseBuilder
from .cli import main
from .testing.utils import apply_fs


minimal_config = {
    'readthedocs.yml': '''
name: docs
type: sphinx
''',
}


def run(params):
    runner = CliRunner()
    # Patch ``build`` function to not test the actual build but the config
    # parsing etc.
    with patch.object(BaseBuilder, 'build'):
        return runner.invoke(main, params)


def test_main_fails_with_exit_code_1_if_no_config_found(tmpdir):
    with tmpdir.as_cwd():
        result = run([])
        assert result.exit_code == 1


def test_main_resets_cwd(tmpdir):
    tmpdir = apply_fs(tmpdir, {
        'goodpath': {
            'readthedocs.yml': '''

            '''
        }
    })

    with tmpdir.as_cwd():
        old_cwd = os.getcwd()
        run(['goodpath'])
        assert os.getcwd() == old_cwd


def test_main_takes_path_argument(tmpdir):
    tmpdir = apply_fs(tmpdir, {
        'badpath': {},
        'goodpath': minimal_config,
    })

    with tmpdir.as_cwd():
        result = run(['badpath'])
        assert result.exit_code == 1

        result = run(['goodpath'])
        assert result.exit_code == 0, result.output


def test_main_attaches_outdir_to_env_config(tmpdir):
    with apply_fs(tmpdir, minimal_config).as_cwd():
        with patch('readthedocs_build.cli.build') as build:
            run(['--outdir=out'])
            args, kwargs = build.call_args
            project_config = args[0]
            assert project_config[0]['output_base'] == str(tmpdir.join('out'))


def test_outdir_default(tmpdir):
    with apply_fs(tmpdir, minimal_config).as_cwd():
        with patch('readthedocs_build.cli.build') as build:
            run([])
            args, kwargs = build.call_args
            project_config = args[0]
            outdir = str(tmpdir.join('_readthedocs_build'))
            assert project_config[0]['output_base'] == outdir

from click.testing import CliRunner
import os

from .cli import main
from .testing.utils import apply_fs


def run(params):
    runner = CliRunner()
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
        'goodpath': {
            'readthedocs.yml': '''
type: sphinx
            '''
        }
    })

    with tmpdir.as_cwd():
        result = run(['badpath'])
        assert result.exit_code == 1

        result = run(['goodpath'])
        assert result.exit_code == 0, result.output

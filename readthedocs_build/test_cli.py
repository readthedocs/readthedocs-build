import os
from pytest import raises

from .cli import main
from .testing.utils import apply_fs


def test_main_fails_with_exit_code_1_if_no_config_found(tmpdir):
    with tmpdir.as_cwd():
        with raises(SystemExit) as excinfo:
            main()
    assert excinfo.value.code == 1


def test_main_resets_cwd(tmpdir):
    tmpdir = apply_fs(tmpdir, {
        'goodpath': {
            'readthedocs.yml': '''

            '''
        }
    })

    with tmpdir.as_cwd():
        old_cwd = os.getcwd()
        main(path='goodpath')
        assert os.getcwd() == old_cwd


def test_main_takes_path_argument(tmpdir):
    tmpdir = apply_fs(tmpdir, {
        'badpath': {},
        'goodpath': {
            'readthedocs.yml': '''

            '''
        }
    })

    with tmpdir.as_cwd():
        with raises(SystemExit):
            main(path='badpath')
        main(path='goodpath')

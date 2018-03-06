import os

from .find import find_all, find_one
from ..testing.utils import apply_fs


def test_find_no_files(tmpdir):
    with tmpdir.as_cwd():
        paths = list(find_all(os.getcwd(), ('readthedocs.yml',)))
    assert len(paths) == 0


def test_find_at_root(tmpdir):
    apply_fs(tmpdir, {'readthedocs.yml': '', 'otherfile.txt': ''})

    base = str(tmpdir)
    paths = list(find_all(base, ('readthedocs.yml',)))
    assert paths == [
        os.path.abspath(os.path.join(base, 'readthedocs.yml'))
    ]


def test_find_nested(tmpdir):
    apply_fs(tmpdir, {
        'first': {
            'readthedocs.yml': '',
        },
        'second': {
            'confuser.txt': 'content',
        },
        'third': {
            'readthedocs.yml': 'content',
            'Makefile': '',
        },
    })
    apply_fs(tmpdir, {'first/readthedocs.yml': ''})

    base = str(tmpdir)
    paths = list(find_all(base, ('readthedocs.yml',)))
    assert set(paths) == set([
        str(tmpdir.join('first', 'readthedocs.yml')),
        str(tmpdir.join('third', 'readthedocs.yml')),
    ])


def test_find_multiple_files(tmpdir):
    apply_fs(tmpdir, {
        'first': {
            'readthedocs.yml': '',
            '.readthedocs.yml': 'content',
        },
        'second': {
            'confuser.txt': 'content',
        },
        'third': {
            'readthedocs.yml': 'content',
            'Makefile': '',
        },
    })
    apply_fs(tmpdir, {'first/readthedocs.yml': ''})

    base = str(tmpdir)
    paths = list(find_all(base, ('readthedocs.yml',
                                 '.readthedocs.yml')))
    assert paths == [
        str(tmpdir.join('first', 'readthedocs.yml')),
        str(tmpdir.join('first', '.readthedocs.yml')),
        str(tmpdir.join('third', 'readthedocs.yml')),
    ]

    paths = list(find_all(base, ('.readthedocs.yml',
                                 'readthedocs.yml')))
    assert paths == [
        str(tmpdir.join('first', '.readthedocs.yml')),
        str(tmpdir.join('first', 'readthedocs.yml')),
        str(tmpdir.join('third', 'readthedocs.yml')),
    ]


def test_find_unicode_path(tmpdir):
    base_path = os.path.abspath('integration_tests/bad_encode_project')
    unicode_base_path = base_path  # .decode('utf-8')
    try:
        find_one(unicode_base_path, ('readthedocs.yml',))
    except Exception as e:
        __import__('pdb').set_trace()
        assert isinstance(e, UnicodeDecodeError)
    else:
        assert False, 'No UnicodeDecodeError exception was raised'

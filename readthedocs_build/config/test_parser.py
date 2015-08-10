from io import StringIO
from pytest import raises

from .parser import parse
from .parser import ParseError


def test_parse_empty_config_file():
    buf = StringIO(u'')
    with raises(ParseError):
        parse(buf)


def test_parse_invalid_yaml():
    buf = StringIO(u'- - !asdf')
    with raises(ParseError):
        parse(buf)


def test_parse_bad_type():
    buf = StringIO(u'Hello')
    with raises(ParseError):
        parse(buf)


def test_parse_single_config():
    buf = StringIO(u'base: path')
    config = parse(buf)
    assert isinstance(config, list)
    assert len(config) == 1
    assert config[0]['base'] == 'path'


def test_parse_multiple_configs_in_one_file():
    buf = StringIO(
        u'''
base: path
---
base: other_path
name: second
nested:
    works: true
        ''')
    configs = parse(buf)
    assert isinstance(configs, list)
    assert len(configs) == 2
    assert configs[0]['base'] == 'path'
    assert configs[1]['nested'] == {'works': True}

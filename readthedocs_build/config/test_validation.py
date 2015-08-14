from pytest import raises

from .validation import validate_bool
from .validation import ValidationError
from .validation import INVALID_BOOL


def describe_validate_bool():
    def it_accepts_true():
        assert validate_bool(True) is True

    def it_accepts_false():
        assert validate_bool(False) is False

    def it_accepts_0():
        assert validate_bool(0) is False

    def it_accepts_1():
        assert validate_bool(1) is True

    def it_fails_on_string():
        with raises(ValidationError) as excinfo:
            validate_bool('random string')
        assert excinfo.value.code == INVALID_BOOL

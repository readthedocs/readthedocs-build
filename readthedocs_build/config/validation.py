import os


INVALID_BOOL = 'invalid-bool'
INVALID_CHOICE = 'invalid-choice'
INVALID_DIRECTORY = 'invalid-directory'
INVALID_STRING = 'invalid-string'


class ValidationError(Exception):
    messages = {
        INVALID_BOOL: 'expected one of (0, 1, true, false), got {value}',
        INVALID_CHOICE: 'expected one of ({choices}), got {value}',
        INVALID_DIRECTORY: 'directory {value} does not exist',
        INVALID_STRING: 'expected string',
    }

    def __init__(self, value, code, format_kwargs=None):
        self.value = value
        self.code = code
        defaults = {
            'value': value,
        }
        if format_kwargs is not None:
            defaults.update(format_kwargs)
        message = self.messages[code].format(**defaults)
        super(ValidationError, self).__init__(message)


def validate_choice(value, choices):
    if value not in choices:
        raise ValidationError(value, INVALID_CHOICE, {
            'choices': ', '.join(choices)
        })
    return value


def validate_bool(value):
    if value not in (0, 1, False, True):
        raise ValidationError(value, INVALID_BOOL)
    return bool(value)


def validate_directory(value, base_path):
    value = validate_string(value)
    value = os.path.join(base_path, value)
    value = os.path.abspath(value)
    if not os.path.isdir(value):
        raise ValidationError(value, INVALID_DIRECTORY)
    return value


def validate_string(value):
    if not isinstance(value, basestring):
        raise ValidationError(value, INVALID_STRING)
    return unicode(value)

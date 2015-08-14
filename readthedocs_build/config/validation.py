INVALID_BOOL = 'invalid-bool'


class ValidationError(Exception):
    messages = {
        INVALID_BOOL: 'expected one of (0, 1, true, false), got {value}',
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


def validate_bool(value):
    if value in (0, 1, False, True):
        return bool(value)
    raise ValidationError(value, INVALID_BOOL)

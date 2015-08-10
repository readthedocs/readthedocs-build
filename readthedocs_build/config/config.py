from .find import find_all
from .parser import ParseError
from .parser import parse


CONFIG_FILENAME = 'readthedocs.yml'


CONFIG_SYNTAX_INVALID = 'config-syntax-invalid'
CONFIG_REQUIRED = 'config-required'
TYPE_REQUIRED = 'type-required'
TYPE_INVALID = 'type-invalid'


class InvalidConfig(Exception):
    def __init__(self, *args, **kwargs):
        self.code = kwargs.pop('code')
        self.source_file = kwargs.pop('source_file', None)
        self.source_position = kwargs.pop('source_position', None)
        super(InvalidConfig, self).__init__(*args, **kwargs)


class BuildConfig(dict):
    """
    Config that handles the build of one particular documentation. Config keys
    can be accessed with a dictionary lookup::

        >>> build_config['type']
        'sphinx'

    """

    TYPE_REQUIRED_MESSAGE = 'Missing key "type"'
    INVALID_TYPE_MESSAGE = 'Invalid type "{type}". Valid values are {valid_types}'

    def __init__(self, raw_config, source_file=None, source_position=None):
        self.raw_config = raw_config
        self.source_file = source_file
        self.source_position = source_position

    def error(self, message, code):
        source = '{file} [{pos}]'.format(
            file=self.source_file,
            pos=self.source_position)
        raise InvalidConfig(
            '{source}: {message}'.format(source=source, message=message),
            code=code,
            source_file=self.source_file,
            source_position=self.source_position)

    def get_valid_types(self):
        return (
            'sphinx',
        )

    def validate(self):
        """
        Validate and process config into ``config`` attribute that contains the
        ready to use build configuration.
        """

        type = self.raw_config.get('type', None)
        if not type:
            self.error(self.TYPE_REQUIRED_MESSAGE, code=TYPE_REQUIRED)
        if type != 'sphinx':
            self.error(
                self.INVALID_TYPE_MESSAGE.format(
                    type=type,
                    valid_types=' '.join(
                        '"{}"'.format(valid)
                        for valid in self.get_valid_types())),
                code=TYPE_INVALID)
        self['type'] = type


class ProjectConfig(list):
    """
    Wrapper for multiple build configs.
    """

    pass


def load(path):
    """
    Load a project configuration and all the contained build configs for a
    given path. That is usually the root of the project.
    """

    config_files = list(find_all(path, CONFIG_FILENAME))
    if not config_files:
        raise InvalidConfig(
            'No {filename} found'.format(filename=CONFIG_FILENAME),
            code=CONFIG_REQUIRED)
    build_configs = []
    for filename in config_files:
        with open(filename, 'r') as file:
            try:
                configs = parse(file.read())
            except ParseError as error:
                raise InvalidConfig(
                    'Parse error in {filename}: {message}'.format(
                        filename=filename,
                        message=error.message),
                    code=CONFIG_SYNTAX_INVALID)
            for i, config in enumerate(configs):
                build_config = BuildConfig(
                    config,
                    source_file=filename,
                    source_position=i)
                build_configs.append(build_config)
    return ProjectConfig(build_configs)

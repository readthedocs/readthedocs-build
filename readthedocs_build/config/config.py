import re
import os

from .find import find_all
from .parser import ParseError
from .parser import parse


__all__ = ('load', 'BuildConfig', 'InvalidConfig', 'ProjectConfig')


CONFIG_FILENAME = 'readthedocs.yml'


BASE_INVALID = 'base-invalid'
BASE_NOT_A_DIR = 'base-not-a-directory'
CONFIG_SYNTAX_INVALID = 'config-syntax-invalid'
CONFIG_REQUIRED = 'config-required'
NAME_REQUIRED = 'name-required'
NAME_INVALID = 'name-invalid'
TYPE_REQUIRED = 'type-required'
TYPE_INVALID = 'type-invalid'
PYTHON_INVALID = 'python-invalid'
USE_SYSTEM_SITE_PACKAGES_INVALID = 'use-system-site-packages-invalid'


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

    You need to call ``validate`` before the config is ready to use. Also
    setting the ``output_base`` is required before using it for a build.
    """

    BASE_INVALID_MESSAGE = 'Invalid value for base: {base}'
    BASE_NOT_A_DIR_MESSAGE = '"base" is not a directory: {base}'
    NAME_REQUIRED_MESSAGE = 'Missing key "name"'
    NAME_INVALID_MESSAGE = (
        'Invalid name "{name}". Valid values must match {name_re}')
    TYPE_REQUIRED_MESSAGE = 'Missing key "type"'
    INVALID_TYPE_MESSAGE = 'Invalid type "{type}". Valid values are {valid_types}'
    USE_SYSTEM_SITE_PACKAGES_INVALID_MESSAGE = (
        'Invalid value for "use_system_site_packages". '
        'It must be "true" or "false"')
    PYTHON_INVALID_MESSAGE = '"python" section must be a mapping.'

    def __init__(self, env_config, raw_config, source_file, source_position):
        self.env_config = env_config
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

        It makes sure that:

        - ``type`` is set and is a valid builder
        - ``base`` is a valid directory and defaults to the directory of the
          ``readthedocs.yml`` config file if not set
        """

        # Validate env_config.
        self.validate_output_base()

        # Validate raw_config. Order matters.
        self.validate_name()
        self.validate_type()
        self.validate_base()

    def validate_output_base(self):
        assert 'output_base' in self.env_config, (
            '"output_base" required in "env_config"')
        self['output_base'] = os.path.abspath(self.env_config['output_base'])

    def validate_name(self):
        name = self.raw_config.get('name', None)
        if not name:
            self.error(self.NAME_REQUIRED_MESSAGE, code=NAME_REQUIRED)
        name_re = r'^[-_.0-9a-zA-Z]+$'
        if not re.match(name_re, name):
            self.error(
                self.NAME_INVALID_MESSAGE.format(
                    name=name,
                    name_re=name_re),
                code=NAME_INVALID)

        self['name'] = name

    def validate_type(self):
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

    def validate_base(self):
        if 'base' in self.raw_config:
            base = self.raw_config['base']
            if not isinstance(base, basestring):
                self.error(self.BASE_INVALID_MESSAGE.format(
                    base=repr(base)), code=BASE_INVALID)
            base = os.path.join(
                os.path.dirname(self.source_file),
                self.raw_config['base'])
        else:
            base = os.path.dirname(self.source_file)
        base = os.path.abspath(base)

        if not os.path.isdir(base):
            self.error(
                self.BASE_NOT_A_DIR_MESSAGE.format(base=base),
                code=BASE_NOT_A_DIR)

        self['base'] = base

    def validate_python(self):
        python = {}
        if 'python' in self.raw_config:
            raw_python = self.raw_config['python']
            if not isinstance(raw_python, dict):
                self.error(
                    self.PYTHON_INVALID_MESSAGE,
                    code=PYTHON_INVALID)
            use_system_site_packages = raw_python.get(
                'use_system_site_packages', False)
            if use_system_site_packages not in (True, False, 0, 1):
                self.error(
                    self.USE_SYSTEM_SITE_PACKAGES_INVALID_MESSAGE,
                    code=USE_SYSTEM_SITE_PACKAGES_INVALID)
            python['use_system_site_packages'] = bool(use_system_site_packages)

        self['python'] = python


class ProjectConfig(list):
    """
    Wrapper for multiple build configs.
    """

    def validate(self):
        for build in self:
            build.validate()

    def set_output_base(self, directory):
        for build in self:
            build['output_base'] = os.path.abspath(directory)


def load(path, env_config):
    """
    Load a project configuration and all the contained build configs for a
    given path. That is usually the root of the project.

    The config will be validated.
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
                    env_config,
                    config,
                    source_file=filename,
                    source_position=i)
                build_configs.append(build_config)

    project_config = ProjectConfig(build_configs)
    project_config.validate()
    return project_config
